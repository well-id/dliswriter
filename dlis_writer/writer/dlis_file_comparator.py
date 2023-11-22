import logging
from dlis_writer.utils.logging import install_logger


logger = logging.getLogger(__name__)


def read_binary(fname):
    with open(fname, 'rb') as f:
        contents = f.read()
    return contents


def compare(f1, f2, verbose=True):
    data1 = read_binary(f1)
    data2 = read_binary(f2)

    if (l1 := len(data1)) != (l2 := len(data2)):
        if verbose:
            print(f"Lengths of the files don't match ({l1} vs {l2})")
        return False

    nonmatching_indices = [i for i in range(len(data1)) if data1[i] != data2[i]]
    if nonmatching_indices:
        if verbose:
            print(f"Files do not match at {len(nonmatching_indices)} indices: {nonmatching_indices}")
        return False
    return True


if __name__ == '__main__':
    install_logger(logger)

    from sys import argv

    if (na := len(argv)) != 3:
        raise ValueError(f"Expected 2 arguments (names of files to compare), got {na-1}")

    equal = compare(argv[1], argv[2])
    print(f"Files are {'' if equal else 'not '}equal")
