import os
import logging
from typing import Union

from dliswriter.utils.logging import install_colored_logger


logger = logging.getLogger(__name__)

path_type = Union[str, bytes, os.PathLike]


def read_binary(fname: path_type) -> bytes:
    """Read a binary file and return the contained bytes."""

    with open(fname, 'rb') as f:
        contents = f.read()
    return contents


def compare(f1: path_type, f2: path_type, verbose: bool = True) -> bool:
    """Compare two files at binary level.

    Args
        f1      :   Name of the first file.
        f2      :   Name of the second file.
        verbose :   If True and the two files don't match, print out the reason (mismatching lengths or contents).

    Returns:
          True if files are identical; False otherwise.
    """

    data1 = read_binary(f1)
    data2 = read_binary(f2)

    if (l1 := len(data1)) != (l2 := len(data2)):
        if verbose:
            print(f"Lengths of the files don't match ({l1} vs {l2})")
        return False

    mismatched_indices = [i for i in range(len(data1)) if data1[i] != data2[i]]
    if mismatched_indices:
        if verbose:
            print(f"Files do not match at {len(mismatched_indices)} indices: {mismatched_indices}")
        return False
    return True


if __name__ == '__main__':
    install_colored_logger(logger)

    from sys import argv

    if (na := len(argv)) != 3:
        raise ValueError(f"Expected 2 arguments (names of files to compare), got {na-1}")

    equal = compare(argv[1], argv[2])
    print(f"Files are {'' if equal else 'not '}equal")
