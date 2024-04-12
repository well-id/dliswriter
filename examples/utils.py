import os
from pathlib import Path
import logging

from dliswriter.utils.types import file_name_type


logger = logging.getLogger(__name__)


def _check_write_access(p: file_name_type) -> None:
    """Check if the provided path supports write action. Raise a RuntimeError otherwise."""

    if not os.access(p, os.W_OK):
        raise RuntimeError(f"Write permissions missing for directory: {p}")


def prepare_directory(output_file_name: file_name_type, overwrite: bool = False) -> None:
    """Prepare directory for the output file.

    Create up to 1 top level on the path. Make sure the directory allows writing.
    Check if a file of the given name already exists.

    Args:
        output_file_name    :   Name of the file to be created.
        overwrite           :   Used if the file already exists. If True, include a warning in the logs and overwrite
                                the file. If False, raise a RuntimeError.
    """

    output_file_name = Path(output_file_name).resolve()
    save_dir = output_file_name.parent
    parent_dir = save_dir.parent

    if not parent_dir.exists():
        raise RuntimeError(f"Directory {parent_dir} does not exist")

    _check_write_access(parent_dir)

    os.makedirs(save_dir, exist_ok=True)
    _check_write_access(save_dir)

    if os.path.exists(output_file_name):
        if overwrite:
            logger.warning(f"Output file at {output_file_name} will be overwritten")
        else:
            raise RuntimeError(f"Cannot overwrite existing file at {output_file_name}")
