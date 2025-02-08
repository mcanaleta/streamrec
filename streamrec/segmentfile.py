from itertools import tee
from pathlib import Path
from time import strftime, gmtime
from typing import Iterable
import logging
import os


from streamrec.packet import PacketWithReceivedTS
from streamrec.session import RecordingSession

logger = logging.getLogger(__name__)


class SegmentFile:
    def __init__(self, session: RecordingSession, segment_ts: float):
        self.session = session
        self.config = session.config
        self.segment_ts = segment_ts
        self.first_packet: PacketWithReceivedTS = None

    def write(self, packets: Iterable[PacketWithReceivedTS]):
        if not self.first_packet:
            packets, tee_packets = tee(packets)
            self.first_packet = next(tee_packets)
        with open(self.get_path(tmp=True), "ab") as file:
            for packet in packets:
                file.write(packet.packet)

    def close(self):
        logger.info("Closing segment %s", self.get_path())
        os.rename(self.get_path(tmp=True), self.get_path())

    def get_path(self, tmp=False) -> Path:
        ts = self.first_packet.get_adjusted_ts()
        if ts < self.segment_ts:
            logger.error("First packet ts %s is less than segment ts %s",
                         ts, self.segment_ts)
            raise ValueError("First packet ts is less than segment ts")
        ts_str = strftime("%Y%m%d-%H%M%S-%Z", gmtime(ts))
        filename = f"{ts_str}_{self.session.uuid}.mp3"
        if tmp:
            filename += ".tmp"
        return Path(self.config.output_folder) / filename
