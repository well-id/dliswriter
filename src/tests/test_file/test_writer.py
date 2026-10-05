"""Prepared byte copying is internal and independent of record serialization."""

from io import BytesIO

import pytest

from dliswriter.file.writer import DLISWriter


@pytest.mark.parametrize('size', [0, -1, True, 1.5, None])
def test_prepared_copy_rejects_invalid_read_size_without_output(tmp_path, size):
    path = tmp_path / 'invalid.dlis'
    writer = DLISWriter(path)
    with pytest.raises(ValueError, match='positive integer'):
        writer._commit_prepared(BytesIO(b'prepared'), size, includes_sul=True)
    assert not path.exists() and not writer._sul_written


def test_prepared_copy_exact_chunks_and_sul_state(tmp_path):
    class BoundedStream(BytesIO):
        def read(self, size=-1):
            assert size == 3
            return super().read(size)

    path = tmp_path / 'copy.dlis'
    writer = DLISWriter(path)
    initial = BoundedStream(b'prepared SUL and records')
    with pytest.raises(RuntimeError, match='SUL exactly once'):
        writer._commit_prepared(initial, 3)
    assert not path.exists() and initial.tell() == 0
    writer._commit_prepared(initial, 3, includes_sul=True)
    assert writer._sul_written and not initial.closed
    with pytest.raises(RuntimeError, match='SUL exactly once'):
        writer._commit_prepared(BytesIO(b'duplicate SUL'), 3, includes_sul=True)
    writer._commit_prepared(BoundedStream(b'new FDATA only'), 3)
    assert path.read_bytes() == b'prepared SUL and recordsnew FDATA only'
