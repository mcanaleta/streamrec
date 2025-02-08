import logging
import signal

import typer
from typing_extensions import Annotated

from streamrec.config import RecordingConfig
from streamrec.recorder import Recorder


logger = logging.getLogger("main")

logging.basicConfig(level=logging.INFO)
app = typer.Typer()


@app.command()
def cli(
    url: Annotated[
        str, typer.Option(envvar="URL")],
    output_folder: Annotated[
        str, typer.Option(envvar="OUTPUT_FOLDER")],
    initial_writer_delay: Annotated[
        int, typer.Option(envvar="INITIAL_WRITER_DELAY")] = 5,
    segment_duration: Annotated[
        int, typer.Option(envvar="SEGMENT_DURATION")] = 60,
    write_period: Annotated[
        int, typer.Option(envvar="WRITE_PERIOD")] = 1,
    close_open_files_on_start: Annotated[
        bool, typer.Option(envvar="CLOSE_OPEN_FILES_ON_START")] = True,
    no_data_timeout: Annotated[
        int, typer.Option(envvar="NO_DATA_TIMEOUT")] = 30
):
    config = RecordingConfig(url=url,
                             output_folder=output_folder,
                             initial_writer_delay=initial_writer_delay,
                             segment_duration=segment_duration,
                             write_period=write_period,
                             close_open_files_on_start=close_open_files_on_start,
                             network_timeout=no_data_timeout)
    processor = Recorder(config)
    signal.signal(signal.SIGINT, processor.stop)
    signal.signal(signal.SIGTERM, processor.stop)
    processor.start()
    logger.info("Exiting main")
