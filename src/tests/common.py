from contextlib import contextmanager
from dlisio import dlis    # type: ignore  # untyped library
from typing import Union, Generator
import os

from dliswriter.logical_record.core.eflr.eflr_item import EFLRItem


N_COLS = 128


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
