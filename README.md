# StreamRec

StreamRec is a tool for recording streaming data.

## Installation

To install the project, run:
```bash
pip install git+https://github.com/mcanaleta/streamrec.git
```


## Usage

You can use the `streamrec` command-line interface to start recording:

```bash
streamrec --url <STREAM_URL> --output-folder <OUTPUT_FOLDER> [OPTIONS]
```

### Options

- `--url`: The URL of the stream to record.
- `--output-folder`: The folder where the recorded segments will be saved.
- `--initial-writer-delay`: Initial delay before writing the first segment (default: 5 seconds).
- `--segment-duration`: Duration of each segment in seconds (default: 60 seconds).
- `--write-period`: Period between writes in seconds (default: 1 second).
- `--close-open-files-on-start`: Whether to close open files on start (default: True).
- `--no-data-timeout`: Timeout for no data in seconds (default: 30 seconds).

## Example

```bash
streamrec --url http://example.com/stream --output-folder ./recordings --initial-writer-delay 10 --segment-duration 120 --write-period 2 --close-open-files-on-start False --no-data-timeout 60
```

This command will start recording the stream from `http://example.com/stream` and save the segments to the `./recordings` folder.
````