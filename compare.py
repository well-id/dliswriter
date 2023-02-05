import sys

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


def compare(f1, f2):
    for attribute in ATTRIBUTES:
        if getattr(f1, attribute) != getattr(f2, attribute):
            print(f'Comparison returned False for attribute "{attribute}"')
            return False
    else:
        return True


if __name__ == '__main__':
    filename1, filename2 = sys.argv[1:3]

    file1, *tails1 = dlis.load(filename1)
    file2, *tails2 = dlis.load(filename2)

    print("Equal" if compare(file1, file2) else "Not equal")

