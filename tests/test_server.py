import http.server
import io
import logging
import os
import time
from urllib.parse import parse_qs, urlparse
import av
import numpy as np

PORT = 8000
SAMPLE_RATE = 44100
CHANNELS = 2
BIT_RATE = 128000  # 128 kbps

logger = logging.getLogger(__name__)

logging.basicConfig(level=os.getenv("LOGLEVEL", "ERROR"))


class TestServer:

    def __init__(self):
        self.httpd = None
        self.packet = self.generate_white_noise_packet()

    def generate_white_noise_packet(self) -> av.Packet:
        """Generate white noise and encode it as MP3 in memory."""
        output_buffer = io.BytesIO()
        container = av.open(output_buffer, mode='w', format='mp3')
        stream = container.add_stream('mp3', rate=SAMPLE_RATE)
        # stream.bit_rate = BIT_RATE
        # stream.layout = 'stereo'
        # stream.sample_rate = SAMPLE_RATE
        mono_samples = (np.random.uniform(-1, 1, 100000)
                        * 2**14).astype(np.int16)
        stereo_samples = np.array([mono_samples])
        frame = av.AudioFrame.from_ndarray(
            stereo_samples, format='s16', layout='mono')
        frame.sample_rate = SAMPLE_RATE
        packets = stream.encode(frame)
        packet = packets[0]
        container.close()
        return packet

    def serve(self, request: http.server.BaseHTTPRequestHandler):
        parsed_url = urlparse(request.path)
        parsed_qs = parse_qs(parsed_url.query)

        limit_seconds = float(parsed_qs.get("limit", [0])[0])

        initial_burst = float(parsed_qs.get("initial_burst", [5])[0])
        speed = float(parsed_qs.get("speed", [1.0])[0])

        keep_open = bool(parsed_qs.get("keep_open", [False])[0])

        request.send_response(200)
        request.send_header("Content-Type", "audio/mpeg")

        request.end_headers()

        bytes_sent = 0
        start_ts = time.time()
        try:
            while True:  # Infinite loop to repeat the audio
                request.wfile.write(self.packet)
                bytes_sent += self.packet.size
                seconds_sent = bytes_sent * 8 / BIT_RATE
                request.wfile.flush()
                if limit_seconds and seconds_sent > limit_seconds:
                    if keep_open:
                        logger.info("Limit reached, keeping connection open")
                        time.sleep(10**6)
                    break
                elapsed = time.time() - start_ts
                seconds_to_be_sent = initial_burst + elapsed * speed
                if seconds_sent > seconds_to_be_sent:
                    time.sleep(seconds_sent - seconds_to_be_sent)
            # self.wfile.close()
        except (BrokenPipeError, ConnectionResetError):
            pass  # Client disconnected
        logger.info("Request finished")

    def start(self):
        server = self

        class Handler(http.server.BaseHTTPRequestHandler):
            # pylint: disable=invalid-name
            def do_GET(self):
                server.serve(self)

            def log_message(self, format, *args):
                pass  # Suppress log messages

        self.httpd = http.server.ThreadingHTTPServer(("", PORT), Handler)
        self.httpd.serve_forever()


def test_server_start():
    server = TestServer()
    server.start()


if __name__ == "__main__":
    TestServer().start()
