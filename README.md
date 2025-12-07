# time_utils

Utility script for timing common filesystem tasks.

## Usage

Run operations via the `time_operations.py` script with the desired subcommand:

- **Zip a directory**: `python time_operations.py zip <source_dir> [--output <archive.zip>]`
- **Search for a string**: `python time_operations.py search <term> <directory>`
- **Copy a file or directory**: `python time_operations.py copy <source> <destination>`

Each operation prints the result along with the elapsed time in seconds.
