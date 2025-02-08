from dataclasses import dataclass, field
import logging
from uuid import UUID, uuid1

from streamrec.config import RecordingConfig


logger = logging.getLogger(__name__)


@dataclass
class RecordingSession:
    config: RecordingConfig
    ts_start: float = None
    adjusted_ts_start: float = None
    uuid: UUID = field(default_factory=uuid1)
