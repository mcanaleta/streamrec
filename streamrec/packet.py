from time import time
import av

from .session import RecordingSession


class PacketWithReceivedTS:
    def __init__(self, session: RecordingSession, packet: av.Packet):
        self.session = session
        self.packet = packet
        self.received_ts = time()

    def get_seconds_since_start(self) -> float:
        return self.packet.pts * self.packet.time_base

    def get_adjusted_ts(self) -> float:
        return self.packet.pts * self.packet.time_base + self.session.adjusted_ts_start

    def guess_session_start(self):
        return self.received_ts - self.get_seconds_since_start()

    def get_segment_ts(self) -> int:
        ts = self.get_adjusted_ts()
        segment_duration = self.session.config.segment_duration
        return int(ts // segment_duration) * segment_duration
