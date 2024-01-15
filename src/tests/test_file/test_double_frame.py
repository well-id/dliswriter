import pytest
from pathlib import Path
import os
from typing import Generator
from dlisio import dlis

from dlis_writer.file.file import DLISFile

from tests.common import load_dlis
from tests.dlis_files_for_testing.double_frame_dlis import write_double_frame_dlis


@pytest.fixture(scope='session')
def double_frame_dlis_path(base_data_path: Path) -> Generator:
    p = base_data_path/'double_frame.DLIS'
    yield p

    if p.exists():
        os.remove(p)


@pytest.fixture(scope='session')
def double_frame_dlis(double_frame_dlis_path: Path) -> Generator:
    df = write_double_frame_dlis(double_frame_dlis_path)
    yield df


@pytest.fixture(scope='session')
def double_frame_dlis_contents(double_frame_dlis_path: Path, double_frame_dlis: DLISFile) -> dlis.LogicalFile:
    with load_dlis(double_frame_dlis_path) as f:
        yield f


@pytest.fixture(scope='session')
def channels(double_frame_dlis_contents: dlis.LogicalFile) -> list[dlis.Channel]:
    return double_frame_dlis_contents.channels


def test_channel_names(channels: list[dlis.Channel]) -> None:
    assert len(channels) == 6

    names = [c.name for c in channels]
    assert names.count('DEPTH') == 2
    assert names.count('RPM') == 2
    assert names.count('AMPLITUDE') == 2


def test_channel_copy_numbers(channels: list[dlis.Channel]) -> None:
    cn = [c.copynumber for c in channels]
    assert cn.count(0) == 3
    assert cn.count(1) == 3


@pytest.mark.parametrize('nr', (0, 1))
def test_frame_channels(double_frame_dlis_contents: dlis.LogicalFile, nr: int) -> None:
    frame = double_frame_dlis_contents.frames[nr]
    assert frame.copynumber == 0  # frames have different names, so can have the same copy number

    ch = frame.channels
    assert len(ch) == 3

    assert ch[0].name == 'DEPTH'
    assert ch[1].name == 'RPM'
    assert ch[2].name == 'AMPLITUDE'

    for ch in ch:
        assert ch.copynumber == nr

