import logging
from multiprocessing import Process
import os
import signal
import socket
from threading import Thread
import time
import unittest
from streamrec.recorder import Recorder
from streamrec.config import RecordingConfig
from .test_server import test_server_start

logger = logging.getLogger(__name__)


@unittest.skipUnless(os.environ.get("INTEGRATION_TESTS"), "Integration tests")
class TestRecorder(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=os.getenv("LOGLEVEL", "ERROR"))
        # Setup code to initialize Recorder instance
        self.config = RecordingConfig(
            url="http://localhost:8000",
            output_folder="/tmp/output",
            initial_writer_delay=1,
            segment_duration=1,
            write_period=1,
            close_open_files_on_start=True
        )
        self.recorder: Recorder = None
        self.recorder_thread: Thread = None
        self.server: Process = None

    def tearDown(self):
        if self.server:
            self.server.terminate()

    def run_server_process(self):
        self.server = Process(target=test_server_start)
        self.server.start()
        while True:
            # try to connect to the server
            try:
                with socket.create_connection(("localhost", 8000), timeout=1):
                    break
            except ConnectionRefusedError:
                time.sleep(0.1)
        return self.server

    def run_recorder(self, stop_after: int = None):
        self.recorder = Recorder(self.config)
        self.recorder_thread = Thread(target=self.recorder.start)
        self.recorder_thread.start()
        if stop_after:
            time.sleep(stop_after)
            self.recorder.stop(signal.SIGINT, None)

    def check_recorder_finished(self, timeout=None):
        self.recorder_thread.join(timeout)
        self.assertFalse(self.recorder_thread.is_alive(),
                         "Recorder did not stop after timeout")
        self.assertFalse(self.recorder.reader_thread.is_alive(),
                         "Reader did not stop after timeout")
        self.assertFalse(self.recorder.writer_thread.is_alive(),
                         "Writer did not stop after timeout")
        self.assertIsNone(self.recorder.reader_unhandled_exception)

    def test_connection_refused(self):
        self.run_recorder()
        self.check_recorder_finished(2)
        self.assertIsNotNone(self.recorder.reader_exception)

    def test_clean_shutdown(self):
        self.run_server_process()
        self.config.url = "http://localhost:8000?speed=2"
        self.run_recorder(stop_after=2)
        self.assertIsNone(self.recorder.reader_exception)

    def test_server_close(self):
        server = self.run_server_process()
        self.config.url = "http://localhost:8000?limit=2"
        self.run_recorder()
        time.sleep(3)
        server.terminate()
        self.check_recorder_finished(5)
        self.assertIsNotNone(self.recorder.reader_exception)

    def test_server_kill(self):
        server = self.run_server_process()
        self.recorder = Recorder(self.config)
        self.run_recorder()
        time.sleep(3)
        server.kill()
        self.check_recorder_finished(2)
        self.assertIsNotNone(self.recorder.reader_exception)

    def test_keep_open(self):
        self.run_server_process()
        self.config.url = "http://localhost:8000?limit=3&keep_open=True"
        self.config.network_timeout = 2
        self.run_recorder()
        self.check_recorder_finished(6)
        self.assertIsNotNone(self.recorder.reader_exception)


if __name__ == '__main__':
    unittest.main()
