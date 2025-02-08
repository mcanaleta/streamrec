import unittest
from streamrec.config import RecordingConfig


class TestRecordingConfig(unittest.TestCase):
    def test_default_values(self):
        config = RecordingConfig(
            url="http://example.com", output_folder="/tmp")
        self.assertEqual(config.url, "http://example.com")
        self.assertEqual(config.output_folder, "/tmp")
        self.assertEqual(config.initial_writer_delay, 5)
        self.assertEqual(config.segment_duration, 60)
        self.assertEqual(config.write_period, 1)
        self.assertTrue(config.close_open_files_on_start)

    def test_custom_values(self):
        config = RecordingConfig(
            url="http://example.com",
            output_folder="/tmp",
            initial_writer_delay=10,
            segment_duration=120,
            write_period=2,
            close_open_files_on_start=False
        )
        self.assertEqual(config.initial_writer_delay, 10)
        self.assertEqual(config.segment_duration, 120)
        self.assertEqual(config.write_period, 2)
        self.assertFalse(config.close_open_files_on_start)


if __name__ == '__main__':
    unittest.main()
