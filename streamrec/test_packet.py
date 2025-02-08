import unittest
from unittest.mock import MagicMock
from time import time
import av
from streamrec.packet import PacketWithReceivedTS
from streamrec.session import RecordingSession
from streamrec.config import RecordingConfig


class TestPacketWithReceivedTS(unittest.TestCase):
    def setUp(self):
        self.config = RecordingConfig(
            url="http://example.com", output_folder="/tmp")
        self.session = RecordingSession(config=self.config)
        self.packet = MagicMock(spec=av.Packet)
        self.packet.pts = 1000
        self.packet.time_base = 0.001
        self.packet_with_received_ts = PacketWithReceivedTS(
            self.session, self.packet)

    def test_get_seconds_since_start(self):
        self.assertEqual(
            self.packet_with_received_ts.get_seconds_since_start(), 1.0)

    def test_get_adjusted_ts(self):
        self.session.adjusted_ts_start = 5.0
        self.assertEqual(self.packet_with_received_ts.get_adjusted_ts(), 6.0)

    def test_guess_session_start(self):
        self.packet_with_received_ts.received_ts = time()
        expected_start = self.packet_with_received_ts.received_ts - 1.0
        self.assertAlmostEqual(
            self.packet_with_received_ts.guess_session_start(), expected_start, places=2)

    def test_get_segment_ts(self):
        self.session.adjusted_ts_start = 5.0
        self.session.config.segment_duration = 10
        self.assertEqual(self.packet_with_received_ts.get_segment_ts(), 0)


if __name__ == '__main__':
    unittest.main()
