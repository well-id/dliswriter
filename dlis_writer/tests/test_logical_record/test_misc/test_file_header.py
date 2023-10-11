import pytest

from dlis_writer.logical_record.misc import FileHeader
from dlis_writer.tests.common import base_data_path, config_params, make_config


def _check_with_config(fh, config):
    assert fh.identifier == config['FileHeader']['name']
    assert fh.sequence_number == int(config['FileHeader']['sequence_number'])


def test_from_config(config_params):
    fh = FileHeader.from_config(config_params)
    _check_with_config(fh, config_params)


@pytest.mark.parametrize(("identifier", "sequence_number"), (("a", "9"), ("123ert", "3")))
def test_from_config_with_params(identifier, sequence_number):
    config = make_config("FileHeader")
    config["FileHeader"]["name"] = identifier
    config["FileHeader"]["sequence_number"] = sequence_number

    fh = FileHeader.from_config(config)
    _check_with_config(fh, config)
