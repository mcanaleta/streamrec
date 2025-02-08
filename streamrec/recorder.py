from itertools import groupby
import logging
from pathlib import Path
import re
import signal
import time
import threading
import av
import av.container
import av.error

from streamrec.config import RecordingConfig

from .packet import PacketWithReceivedTS
from .segmentfile import SegmentFile
from .session import RecordingSession

logger = logging.getLogger("recorder")


def format_ts(ts: float) -> str:
    return time.strftime("%H:%M:%S", time.gmtime(ts))

# pylint: disable=too-many-instance-attributes


class Recorder:

    def __init__(self, config: RecordingConfig):
        self.config = config
        self.session = RecordingSession(config)
        self.current_segment: SegmentFile = None
        self.queue: list[PacketWithReceivedTS] = []
        self.queue_lock = threading.Lock()
        self.stopping = False
        self.reader_finished = False
        self.container: av.container.InputContainer = None
        self.reader_thread: threading.Thread = None
        self.writer_thread: threading.Thread = None
        self.reader_exception: Exception = None
        self.reader_unhandled_exception: Exception = None

    def close_open_files(self):
        path = Path(self.config.output_folder)
        for f in path.glob("*.tmp"):
            # renname without tmp
            logger.warning("Found open file %s, renaming", f)
            new_name = re.sub(r"\.tmp$", "", f.name)
            f.rename(new_name)

    def calc_adjusted_ts_start(self, packets: list[PacketWithReceivedTS]):
        s = self.session
        s.adjusted_ts_start = min(p.guess_session_start() for p in packets)
        buffer_secs = self.session.ts_start - s.adjusted_ts_start
        logger.info("Adjusted TS start: %s, buffer: %.2f seconds",
                    format_ts(s.adjusted_ts_start), buffer_secs)

    def stream_reader(self):
        fn_logger = logging.getLogger("recorder.reader")
        self.session.ts_start = time.time()
        fn_logger.info("Starting reader: %s", format_ts(self.session.ts_start))
        try:
            self.container = av.open(
                self.config.url, options={'timeout': str(self.config.network_timeout * 10**6)})
            stream = next(
                s for s in self.container.streams if s.type == "audio")
            for packet in self.container.demux(stream):
                if packet.is_corrupt:
                    fn_logger.warning("Corrupt packet")
                    continue
                if packet.size == 0:
                    fn_logger.warning("Packet with size 0")
                    continue
                with self.queue_lock:
                    p = PacketWithReceivedTS(
                        session=self.session, packet=packet)
                    self.queue.append(p)
                if self.stopping:
                    break
            self.container.close()
            fn_logger.info("Reader finished successfully")
        # pylint: disable=broad-except
        except Exception as e:
            if any(isinstance(e, exc) for exc in [av.error.ConnectionResetError, av.error.ConnectionRefusedError, av.error.OSError, av.error.TimeoutError]):
                fn_logger.warning("Connection error: %s", e)
            else:
                fn_logger.error("Reader exception: %s", e)
                fn_logger.exception("Reader exception occurred")
                self.reader_unhandled_exception = e
            self.reader_exception = e
        finally:
            self.reader_finished = True

    def file_writer(self):
        fn_logger = logging.getLogger("recorder.writer")
        fn_logger.info("Waiting %s seconds before starting writer "
                       "to have enough packets to calculate adjusted TS start",
                       self.config.initial_writer_delay)
        time.sleep(self.config.initial_writer_delay)
        fn_logger.info("Starting writer, will write every %s seconds",
                       self.config.write_period)
        while len(self.queue) > 0 or not self.reader_finished:
            time.sleep(self.config.write_period)
            fn_logger.debug("Queue size: %s", len(self.queue))

            if len(self.queue) == 0:
                continue

            with self.queue_lock:
                packets = self.queue
                self.queue = []

            if not self.session.adjusted_ts_start:
                self.calc_adjusted_ts_start(packets)

            by_segment = groupby(packets, key=lambda p: p.get_segment_ts())
            for segment_ts, packets in by_segment:
                # Close if segment finished
                if self.current_segment:
                    if self.current_segment.segment_ts != segment_ts:
                        self.current_segment.close()
                        self.current_segment = None

                # Open if its a new segment
                if not self.current_segment:
                    self.current_segment = SegmentFile(session=self.session,
                                                       segment_ts=segment_ts)

                # Write packets
                self.current_segment.write(packets)

        if self.current_segment:
            self.current_segment.close()
        fn_logger.info("Writer finished")

    def stop(self, sig, _frame):
        logger.info("Received signal %s", signal.Signals(sig).name)
        self.stopping = True

    def start(self):
        Path(self.config.output_folder).mkdir(parents=True, exist_ok=True)

        if self.config.close_open_files_on_start:
            self.close_open_files()

        self.reader_thread = threading.Thread(target=self.stream_reader)
        self.reader_thread.start()

        self.writer_thread = threading.Thread(target=self.file_writer)
        self.writer_thread.start()

        self.reader_thread.join()
        self.writer_thread.join()
        logger.info("All threads finished")
