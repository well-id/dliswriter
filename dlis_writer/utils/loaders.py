import os
from configparser import ConfigParser


def load_config(fname):
    if not os.path.exists(fname):
        raise ValueError(f"Config file does not exist at {fname}")

    cfg = ConfigParser()
    cfg.read(fname)
    return cfg
