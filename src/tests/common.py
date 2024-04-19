from contextlib import contextmanager
from dlisio import dlis    # type: ignore  # untyped library
from typing import Union, Generator
import os

from dliswriter.logical_record.core.eflr.eflr_item import EFLRItem


N_COLS = 128
path_type = Union[str, bytes, os.PathLike]


class FilesNotEqualError(RuntimeError):
    pass


@contextmanager
def load_dlis(fname: Union[str, bytes, os.PathLike]) -> Generator:
    """Load a DLIS file using dlisio. Yield the open file. Close the file on return to the context."""

    with dlis.load(fname) as (f, *tail):
        try:
            yield f
        finally:
            pass


def select_channel(f: dlis.file.LogicalFile, name: str) -> dlis.channel.Channel:
    """Search for a channel with given name in the dlis file and return it."""

    return f.object("CHANNEL", name)


def check_list_of_objects(objects: Union[list[EFLRItem], tuple[EFLRItem, ...]],
                          names: Union[list[str], tuple[str, ...]]) -> None:
    """Check that names of the provided objects match the expected names (in the same order)."""

    assert len(objects) == len(names)
    for i, n in enumerate(names):
        assert objects[i].name == n


def read_binary_file(fname: path_type) -> bytes:
    """Read a binary file and return the contained bytes."""

    with open(fname, 'rb') as f:
        contents = f.read()
    return contents


def compare_binary_files(f1: path_type, f2: path_type) -> bool:
    """Compare two files at binary level.

    Args
        f1      :   Name of the first file.
        f2      :   Name of the second file.

    Returns:
          True if files are identical; False otherwise.
    """

    data1 = read_binary_file(f1)
    data2 = read_binary_file(f2)

    if (l1 := len(data1)) != (l2 := len(data2)):
        raise FilesNotEqualError(f"Lengths of the files don't match ({l1} vs {l2})")

    mismatched_indices = [i for i in range(len(data1)) if data1[i] != data2[i]]
    if mismatched_indices:
        raise FilesNotEqualError(f"Files do not match at {len(mismatched_indices)} indices: {mismatched_indices}")
    return True
