from contextlib import contextmanager
from dlisio import dlis    # type: ignore  # untyped library
from typing import Union, Generator
import os

from dlis_writer.logical_record.eflr_types import eflr_sets


def clear_eflr_instance_registers() -> None:
    """Remove all defined instances of EFLR from the internal dicts. Clear the EFLRObject dicts of the instances."""

    for eflr_type in eflr_sets:
        for eflr in eflr_type.get_all_sets():
            eflr.clear_eflr_item_dict()
        eflr_type.clear_set_instance_dict()


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
