import sys
import numpy as np

from dlisio import dlis

ATTRIBUTES = [
    'axes',
    'calibrations',
    'channels',
    'coefficients',
    'comments',
    'computations',
    'equipments',
    'fdata_index',
    'fileheader',
    'frames',
    'groups',
    'longnames',
    'measurements',
    'messages',
    'noformats',
    'parameters',
    'paths',
    'processes',
    'splices',
    'sul',
    'tools',
    'types',
    'unknowns',
    'wellrefs',
    'zones'
]


def compare_arrays(arr1, arr2):
    if arr1.shape != arr2.shape:
        return False

    return ((arr1 == arr2) | (np.isnan(arr1) & np.isnan(arr2))).all()


def compare(f1, f2):
    for attribute in ATTRIBUTES:
        print(f"Checking attribute '{attribute}'")
        if getattr(f1, attribute) != getattr(f2, attribute):
            print(f'Comparison returned False for attribute "{attribute}"')
            return False

    nc = len(f1.channels)
    for i in range(nc):
        print(f'Checking channel {i+1}/{nc}: {f1.channels[i]}')
        if not compare_arrays(f1.channels[i].curves(), f2.channels[i].curves()):
            return False

    return True


if __name__ == '__main__':
    filename1, filename2 = sys.argv[1:3]

    file1, *tails1 = dlis.load(filename1)
    file2, *tails2 = dlis.load(filename2)

    print("Equal" if compare(file1, file2) else "Not equal")

