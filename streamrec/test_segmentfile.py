from datetime import datetime, timezone
import unittest
from unittest.mock import Mock, patch

from streamrec.segmentfile import SegmentFile
from streamrec.session import RecordingSession
from streamrec.packet import PacketWithReceivedTS
from streamrec.config import RecordingConfig


def utc_timestamp(date_str: str) -> float:
    dt = datetime.strptime(date_str, "%Y%m%d-%H%M%S")
    dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


class TestSegmentFileIntegration(unittest.TestCase):
    def setUp(self):
        self.config = RecordingConfig(
            url="http://example.com", output_folder="/tmp")
        self.session = RecordingSession(config=self.config)
        self.session.adjusted_ts_start = utc_timestamp("20200101-000000")

    @patch("os.rename")
    @patch("streamrec.segmentfile.open")
    def test_write_and_close(self, mock_open, mock_rename):
        p1 = Mock()
        p1.pts = 1999
        p1.time_base = 1 / 1000

        packet1 = PacketWithReceivedTS(
            session=self.session, packet=p1)

        p2 = Mock()
        p2.pts = 3000
        p2.time_base = 1 / 1000

        packet2 = PacketWithReceivedTS(
            session=self.session, packet=p2)

        packets = [packet1, packet2]
        it = iter(packets)

        segment_file = SegmentFile(
            session=self.session, segment_ts=packet1.get_segment_ts())

        segment_file.write(it)

        uuid = self.session.uuid
        self.assertEqual(str(segment_file.get_path()),
                         f"/tmp/20200101-000001-UTC_{uuid}.mp3")

        segment_file.close()

        mock_open.assert_called()
        mock_rename.assert_called()


if __name__ == "__main__":
    unittest.main()
