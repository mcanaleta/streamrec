from dataclasses import dataclass


@dataclass
class RecordingConfig:
    url: str
    output_folder: str
    initial_writer_delay: int = 5
    segment_duration: int = 60
    write_period: int = 1
    close_open_files_on_start: bool = True
    network_timeout: int = 30
