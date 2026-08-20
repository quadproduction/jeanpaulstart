import sys
import argparse
from loguru import logger
import jeanpaulstart


def process_args():
    parser = argparse.ArgumentParser(description="Jean-Paul Start - Cube's Launcher")
    parser.add_argument(
        '-f',
        '--filepath',
        type=str,
        help="Filepath to batch (.json / .yml)"
    )
    parse_args = parser.parse_args()
    return parse_args


if __name__ == '__main__':
    args = process_args()
    jeanpaulstart.load_plugins()

    if not args.filepath:
        sys.exit()

    status = jeanpaulstart.run_from_filepath(args.filepath)

    if status == jeanpaulstart.BATCH_NO_DATA:
        exit_code = 2  # No such file or directory

    elif status in (jeanpaulstart.BATCH_NOT_NORMALIZED, jeanpaulstart.BATCH_NOT_VALID):
        exit_code = 3

    elif status in (jeanpaulstart.OK, jeanpaulstart.TASK_ERROR_IGNORED):
        exit_code = 0  # Success

    else:
        exit_code = status

    logger.info("Exit code is '{}'", exit_code)
    sys.exit(exit_code)
