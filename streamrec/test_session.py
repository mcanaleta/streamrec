import unittest
from uuid import UUID
from streamrec.session import RecordingSession
from streamrec.config import RecordingConfig


class TestRecordingSession(unittest.TestCase):
    def setUp(self):
        self.config = RecordingConfig(
            url="http://example.com", output_folder="/tmp")
        self.session = RecordingSession(config=self.config)

    def test_initialization(self):
        self.assertEqual(self.session.config, self.config)
        self.assertIsNone(self.session.ts_start)
        self.assertIsNone(self.session.adjusted_ts_start)
        self.assertIsInstance(self.session.uuid, UUID)

    def test_uuid_uniqueness(self):
        another_session = RecordingSession(config=self.config)
        self.assertNotEqual(self.session.uuid, another_session.uuid)


if __name__ == '__main__':
    unittest.main()
