"""Shared fixed-acquisition fixtures and strict incremental DLIS readback."""

from datetime import datetime, timezone
import logging
import warnings

from dlisio import dlis
from dlisio.common import Actions, ErrorHandler
import numpy as np

from dliswriter.file.file import DLISFile


N_ROWS = 300
CREATED = datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
SCHEMA = (
    ('DEPTH', np.float64, [1], 'm', 7),
    ('QUALITY', np.uint16, [1], 'pu', 16),
    ('SIGNAL', np.float32, [1], 'V', 2),
    ('VECTOR', np.float32, [3], 'V', 2),
)


def synthetic_data():
    row = np.arange(N_ROWS)
    return {
        'DEPTH': 1000.0 + row.astype(np.float64) * 0.25,
        'QUALITY': (row % 17).astype(np.uint16),
        'SIGNAL': (row * 0.5 - 40).astype(np.float32),
        'VECTOR': np.column_stack((row, -row, row * 0.25)).astype(np.float32),
    }


def definition(data):
    """Specify all inferred fields from the full known acquisition, before writing."""
    df = DLISFile(set_identifier='APPEND-SPIKE', sul_sequence_number=1, max_record_length=8192)
    lf = df.add_logical_file(fh_id='APPEND-SPIKE-LF', fh_identifier='0', fh_sequence_number=1)
    lf.add_origin(
        'ORIGIN', origin_reference=1, file_set_number=12345, file_set_name='SPIKE',
        file_number=1, file_type='TEST', product='dliswriter-spike', version='1',
        programs=['single-frame-append'], creation_time=CREATED, producer_code=0,
        producer_name='Synthetic', well_name='SYNTHETIC', field_name='SYNTHETIC',
    )
    channels = []
    for name, dtype, dimension, units, _ in SCHEMA:
        channels.append(lf.add_channel(
            name, dataset_name=name, cast_dtype=dtype, long_name=f'Synthetic {name}',
            dimension=dimension, element_limit=dimension, units=units,
            minimum_value=float(data[name].min()), maximum_value=float(data[name].max()),
            origin_reference=1,
        ))
    frame = lf.add_frame(
        'FRAME', channels=channels, description='Fixed 300-row acquisition',
        # RP66 encryption is indicated by attribute presence, not a zero value.
        index_type='BOREHOLE-DEPTH', direction='INCREASING', encrypted=None, origin_reference=1,
        spacing={'value': 0.25, 'units': 'm'},
        index_min={'value': 1000.0, 'units': 'm'},
        index_max={'value': 1074.75, 'units': 'm'},
    )
    lf.check_objects()
    return df, frame


def freeze(value):
    """Detach parsed metadata, retaining object reference identity rather than handles."""
    if hasattr(value, 'fingerprint'):
        return value.fingerprint
    if isinstance(value, np.ndarray):
        return freeze(value.tolist())
    if isinstance(value, (list, tuple)):
        return tuple(freeze(item) for item in value)
    return value


def snapshot(objects):
    result = []
    for obj in objects:
        # Access every known and stored attribute while strict diagnostics are active.
        keys = sorted(set(obj.attributes) | set(obj.attic.keys()))
        attributes = tuple((key, freeze(obj[key]),
                            obj.attic[key].units if key in obj.attic.keys() else None)
                           for key in keys)
        result.append((obj.fingerprint, attributes))
    return tuple(sorted(result))


def readback(path, expected, count, caplog):
    handler = ErrorHandler(info=Actions.RAISE, minor=Actions.RAISE,
                           major=Actions.RAISE, critical=Actions.RAISE)
    caplog.clear()
    with caplog.at_level(logging.WARNING), warnings.catch_warnings():
        warnings.simplefilter('error')
        with dlis.load(str(path), error_handler=handler) as physical:
            assert len(physical) == 1
            lf = physical[0]
            assert len(lf.frames) == 1
            assert len(lf.origins) == 1
            assert len(lf.channels) == len(SCHEMA)
            assert not lf.noformats
            frame = lf.frames[0]
            assert frame.name == 'FRAME'
            assert frame.index_type == 'BOREHOLE-DEPTH'
            assert frame.index == 'DEPTH'
            assert frame.index_min == 1000.0
            assert frame.index_max == 1074.75
            assert frame.spacing == 0.25
            assert frame.direction == 'INCREASING'
            assert frame.encrypted is False
            assert lf.fileheader.id == 'APPEND-SPIKE-LF'
            assert lf.origins[0].creation_time == CREATED.replace(tzinfo=None)
            assert lf.origins[0].file_set_nr == 12345
            assert [channel.name for channel in frame.channels] == [s[0] for s in SCHEMA]

            curves = frame.curves()
            expected_dtype = np.dtype([('FRAMENO', np.int32)] + [
                ((f'T.CHANNEL-I.{name}-O.1-C.0', name), dtype) if dimension == [1] else
                ((f'T.CHANNEL-I.{name}-O.1-C.0', name), dtype, tuple(dimension))
                for name, dtype, dimension, _, _ in SCHEMA
            ])
            assert curves.dtype == expected_dtype
            assert frame.dtype() == expected_dtype
            assert curves.shape == (count,)
            np.testing.assert_array_equal(curves['FRAMENO'], np.arange(1, count + 1))
            for channel, (name, dtype, dimension, units, reprc) in zip(frame.channels, SCHEMA):
                assert channel.dimension == dimension
                assert channel.element_limit == dimension
                assert channel.reprc == reprc
                assert channel.units == units
                assert channel.long_name == f'Synthetic {name}'
                assert channel.origin == 1
                assert channel.frame.fingerprint == frame.fingerprint
                assert curves[name].dtype == np.dtype(dtype)
                assert curves[name].shape == expected[name][:count].shape
                np.testing.assert_array_equal(curves[name], expected[name][:count])
                np.testing.assert_array_equal(channel.curves(), expected[name][:count])
                assert channel['MINIMUM-VALUE'] == [float(expected[name].min())]
                assert channel['MAXIMUM-VALUE'] == [float(expected[name].max())]

            metadata = (lf.storage_label(), snapshot([
                lf.fileheader, *lf.origins, frame, *lf.channels,
            ]))
            detached_curves = curves.copy()
        assert not [record for record in caplog.records if record.levelno >= logging.WARNING]
    return detached_curves, metadata
