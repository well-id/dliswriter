from enum import Enum, IntEnum
from struct import Struct
from typing import Union, Any
from typing_extensions import Self


class RepresentationCode(int, Enum):
    """Collect RP66 V1 representation codes with Struct converters where possible.

    Some representation codes can not be directly converted using Struct.
    In these cases, the converter is set to None. These codes are still included here,
    so that the enumeration also serves as a full list of representation codes included in the RP66 V1.

    The overridden '__new__' method assigns a new 'converter' attribute to each enum member. This facilitates calling
    the member's converter on any value, e.g.:
        RepresentationCode.FDOUBL.converter.pack(<value>)
    """

    def __new__(cls, code: int, converter: Union[Struct, None] = None) -> "RepresentationCode":
        """When a new member is created, assign not only the integer value, but also a converter.

        Args:
            code        :   Integer value of the enum member.
            converter   :   Struct which can be used to convert a value to bytes according to the format specified
                            when the Struct is initialised.
        """

        obj = super().__new__(cls, code)
        obj._value_ = code
        obj.converter = converter
        return obj

    FSHORT = 1, Struct('>h')
    FSINGL = 2, Struct('>f')
    FSING1 = 3, Struct('>ff')
    FSING2 = 4, Struct('>fff')
    ISINGL = 5, Struct('>i')
    VSINGL = 6, Struct('>i')
    FDOUBL = 7, Struct('>d')
    FDOUB1 = 8, Struct('>dd')
    FDOUB2 = 9, Struct('>ddd')
    CSINGL = 10, Struct('>ff')
    CDOUBL = 11, Struct('>dd')
    SSHORT = 12, Struct('>b')
    SNORM = 13, Struct('>h')
    SLONG = 14, Struct('>i')
    USHORT = 15, Struct('>B')
    UNORM = 16, Struct('>H')
    ULONG = 17, Struct('>I')
    UVARI = 18, None
    IDENT = 19, None
    ASCII = 20, None
    DTIME = 21, Struct('>BBBBBBH')
    ORIGIN = 22, None
    OBNAME = 23, None
    OBJREF = 24, None
    ATTREF = 25, None
    STATUS = 26, Struct('>B')

    def convert(self, value: Any):
        if self.converter is None:
            raise RuntimeError("Converter struct not defined; cannot directly convert the value to bytes")
        return self.converter.pack(value)

    @classmethod
    def get_member(cls, v: Union[str, int, None, Self], allow_none: bool = False) -> Union[Self, None]:
        """Helper function: get a member of the RepresentationCode enum, given the name, value, or the member itself.

        Args:
            v           :   Name or value of the enum, the enum member itself, or None (see below).
            allow_none  :   If True and v is None, return None. Otherwise, a ValueError will be raised.

        Returns:
            The member of the enumeration corresponding to the provided value/name/member (or None).
        """

        if allow_none:
            if v is None:
                return None

        if isinstance(v, cls):
            return v

        if isinstance(v, int):
            try:
                return cls(v)
            except ValueError:
                pass

        if isinstance(v, str):
            if v.isdigit():
                try:
                    return cls(int(v))
                except ValueError:
                    pass

            try:
                return cls[v]
            except KeyError:
                pass

        raise ValueError(f"{cls.__name__} '{v}' is not defined")


# all units explicitly allowed by the RP66 standard
UNITS = (
    "A",
    "K",
    "cd",
    "dAPI",
    "dB",
    "gAPI",
    "kg",
    "m",
    "mol",
    "nAPI",
    "rad",
    "s",
    "sr",
    "Btu",
    "C",
    "D",
    "GPa",
    "Gal",
    "Hz",
    "J",
    "L",
    "MHz",
    "MPa",
    "MeV",
    "Mg",
    "Mpsi",
    "N",
    "Oe",
    "P",
    "Pa",
    "S",
    "T",
    "V",
    "W",
    "Wb",
    "a",
    "acre",
    "atm",
    "b",
    "bar",
    "bbl",
    "c",
    "cP",
    "cal",
    "cm",
    "cu",
    "d",
    "daN",
    "deg",
    "degC",
    "degF,"
    "dm",
    "eV",
    "fC",
    "ft",
    "g",
    "gal",
    "h",
    "in",
    "kHz",
    "kPa",
    "kV",
    "keV",
    "kgf",
    "km",
    "lbf",
    "lbm",
    "mA",
    "mC",
    "mD",
    "mGal",
    "mL",
    "mS",
    "mT",
    "mV",
    "mW",
    "mg",
    "min",
    "mm",
    "mohm",
    "ms",
    "nC",
    "nW",
    "ns",
    "ohm",
    "pC",
    "pPa",
    "ppdk",
    "ppk",
    "ppm",
    "psi",
    "pu",
    "t",
    "ton",
    "uA",
    "uC",
    "uPa",
    "uV",
    "um",
    "uohm",
    "upsi",
    "us"
)


class EFLRType(IntEnum):
    """Types of explicitly formatted logical records."""

    FHLR = 0
    OLR = 1
    AXIS = 2
    CHANNL = 3
    FRAME = 4
    STATIC = 5
    SCRIPT = 6
    UPDATE = 7
    UDI = 8
    LNAME = 9
    SPEC = 10
    DICT = 11


class IFLRType(IntEnum):
    """Types of indirectly formatted logical records."""

    FDATA = 0
    NOFMT = 1

