from enum import Enum, IntEnum
from struct import Struct
from typing import Union, Any
from typing_extensions import Self

from dlis_writer.utils.validator_enum import ValidatorEnum


class RepresentationCode(int, Enum):
    """Collect RP66 V1 representation codes with Struct converters where possible.

    Some representation codes can not be directly converted using Struct.
    In these cases, the converter is set to None. These codes are still included here,
    so that the enumeration also serves as a full list of representation codes included in the RP66 V1.

    The overridden '__new__' method assigns a new 'converter' attribute to each enum member. This facilitates calling
    the member's converter on any value, e.g.:
        RepresentationCode.FDOUBL.converter.pack(<value>)
    """

    converter: Union[Struct, None]

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

    def convert(self, value: Any) -> bytes:
        if self.converter is None:
            raise RuntimeError("Converter struct not defined; cannot directly convert the value to bytes")
        return self.converter.pack(value)

    def decode_bytes(self, value: bytes) -> tuple[Any]:
        if self.converter is None:
            raise RuntimeError("Converter struct not defined; cannot directly decode the bytes")

        s = self.converter.size
        v = len(value)
        if v % s:
            raise ValueError(f"Size of the provided bytes must be an integer multiple of {s}; got {v}")

        return tuple(self.converter.unpack(value[i*s:(i+1)*s])[0] for i in range(v//s))

    @classmethod
    def get_member(cls, v: Union[str, int, None, Self], allow_none: bool = False) -> Union[Self, None]:
        """Helper function: get a member of the RepresentationCode enum, given the name, value, or the member itself.

        Args:
            v           :   Name or value of the enum, the enum member itself, or None (see below).
            allow_none  :   If True and v is None, return None. Otherwise, a ValueError will be raised.

        Returns:
            The member of the enumeration corresponding to the provided value/name/member (or None).
        """

        if allow_none and v is None:
            return None

        if isinstance(v, cls):
            return v

        if isinstance(v, int):
            try:
                return cls(v)
            except ValueError:
                pass

        if isinstance(v, str):
            try:
                return cls[v]
            except KeyError:
                pass

        raise ValueError(f"{cls.__name__} '{v}' is not defined")


class Units(ValidatorEnum):
    # all units explicitly allowed by the RP66 standard
    AMPERE = "A"
    KELVIN = "K"
    CANDELA = "cd"
    API_GRAVITY = "dAPI"
    DECIBEL = "dB"
    API_GAMMA_RAY = "gAPI"
    KILOGRAM = "kg"
    METER = "m"
    MOLE = "mol"
    API_NEUTRON = "nAPI"
    RADIAN = "rad"
    SECOND = "s"
    STERADIAN = "sr"
    BRITISH_THERMAL_UNIT = "Btu"
    COULOMB = "C"
    DARCY = "D"
    GIGAPASCAL = "GPa"
    GAL = "Gal"
    HERTZ = "Hz"
    JOULE = "J"
    LITER = "L"
    MEGAHERTZ = "MHz"
    MEGAPASCAL = "MPa"
    MEGAELECTRONVOLT = "MeV"
    TONNE = "Mg"
    MEGA_POUNDS_PER_SQUARE_METER = "Mpsi"
    NEWTON = "N"
    OERSTED = "Oe"
    POISE = "P"
    PASCAL = "Pa"
    SIEMENS = "S"
    TESLA = "T"
    VOLT = "V"
    WATT = "W"
    WEBER = "Wb"
    ANNUM = "a"
    ACRE = "acre"
    STD_ATMOSPHERE = "atm"
    BARN = "b"
    BAR = "bar"
    BARREL = "bbl"
    REVOLUTION_CYCLE = "c"
    CENTIPOISE = "cP"
    CALORIE = "cal"
    CENTIMETER = "cm"
    CAPTURE_UNIT = "cu"
    DAY = "d"
    DECANEWTON = "daN"
    DEGREE_ANGLE = "deg"
    DEGREE_CELSIUS = "degC"
    DEGREE_FAHRENHEIT = "degF"
    DECIMETER = "dm"
    ELECTRONVOLT = "eV"
    FEMTOCOULOMB = "fC"
    FOOT = "ft"
    GRAM = "g"
    GALLON = "gal"
    HOUR = "h"
    INCH = "in"
    KILOHERTZ = "kHz"
    KILOPASCAL = "kPa"
    KILOVOLT = "kV"
    KILOELECTRONVOLT = "keV"
    KILOGRAM_FORCE = "kgf"
    KILOMETER = "km"
    POUND_FORCE = "lbf"
    POUND_MASS = "lbm"
    MILLIAMPERE = "mA"
    MILLICOULOMB = "mC"
    MILLIDARCY = "mD"
    MILLIGAL = "mGal"
    MILLILITER = "mL"
    MILLISIEMENS = "mS"
    MILLITESLA = "mT"
    MILLIVOLT = "mV"
    MILLIWAT = "mW"
    MILLIGRAM = "mg"
    MINUTE = "min"
    MILLIMETER = "mm"
    MILLIOHM = "mohm"
    MILLISECOND = "ms"
    NANOCOULOMB = "nC"
    NANOWATT = "nW"
    NANOSECOND = "ns"
    OHM = "ohm"
    PICCOCOULOMB = "pC"
    PICOPASCAL = "pPa"
    PART_PER_TEN_THOUSAND = "ppdk"
    PART_PER_THOUSAND = "ppk"
    PART_PER_MILLION = "ppm"
    POUND_PER_SQUARE_INCH = "psi"
    POROSITY_UNIT = "pu"
    METRIC_TON = "t"
    US_SHORT_TON = "ton"
    MICROAMPERE = "uA"
    MICROCOULOMB = "uC"
    MICROPASCAL = "uPa"
    MICROVOLT = "uV"
    MICROMETER = "um"
    MICROOHM = "uohm"
    MICRO_POUND_PER_SQUARE_INCH = "upsi"
    MICROSECOND = "us"


class Properties(ValidatorEnum):
    # allowed values for elements of the 'properties' attribute of Channel, Computation, and Process
    AVERAGED = 'AVERAGED'
    CALIBRATED = 'CALIBRATED'
    CHANGED_INDEX = 'CHANGED-INDEX'
    COMPUTED = 'COMPUTED'
    DEPTH_MATCHED = 'DEPTH-MATCHED'
    DERIVED = 'DERIVED'
    FILTERED = 'FILTERED'
    HOLE_SIZE_CORRECTED = 'HOLE-SIZE-CORRECTED'
    INCLINOMETRY_CORRECTED = 'INCLINOMETRY-CORRECTD'
    LITHOLOGY_CORRECTED = 'LITHOLOGY-CORRECTED'
    LOCAL_COMPUTATION = 'LOCAL-COMPUTATION'
    LOCALLY_DEFINED = 'LOCALLY-DEFINED'
    MODELLED = 'MODELLED'
    MUDCAKE_CORRECTED = 'MUDCAKE-CORRECTED'
    NORMALIZED = 'NORMALIZED'
    OVERSAMPLED = 'OVER-SAMPLED'
    PATCHED = 'PATCHED'
    PRESSURE_CONTROLLED = 'PRESSURE-CORRECTED'
    RESAMPLED = 'RE-SAMPLED'
    SALINITY_CONTROLLED = 'SALINITY-CORRECTED'
    SAMPLED_DOWNWARD = 'SAMPLED-DOWNWARD'
    SAMPLED_UPWARD = 'SAMPLED-UPWARD'
    SPEED_CORRECTED = 'SPEED-CORRECTED'
    SPLICED = 'SPLICED'
    SQUARED = 'SQUARED'
    STACKED = 'STACKED'
    STD = 'STANDARD-DEVIATION'
    STANDOFF_CORRECTED = 'STANDOFF-CORRECTED'
    TEMPERATURE_CORRECTED = 'TEMPERATURE-CORRECTED'
    UNDERSAMPLED = 'UNDER-SAMPLED'


class CalibrationMeasurementPhase(ValidatorEnum):
    AFTER = 'AFTER'
    BEFORE = 'BEFORE'
    MASTER = 'MASTER'


class EquipmentType(ValidatorEnum):
    # options for the 'type' ('_type') attribute of Equipment, allowed by the standard
    ADAPTER = "Adapter"
    BOARD = "Board"
    BOTTOM_NOSE = "Bottom-Nose"
    BRIDLE = "Bridle"
    CABLE = "Cable"
    CALIBRATOR = "Calibrator"
    CARTRIDGE = "Cartridge"
    CENTRALIZER = "Centralizer"
    CHAMBER = "Chamber"
    CUSHION = "Cushion"
    DEPTH_DEVICE = "Depth-Device"
    DISPLAY = "Display"
    DRAWER = "Drawer"
    EXCENTRALIZER = "Excentralizer"
    EXPLOSIVE_SOURCE = "Explosive-Source"
    FLASK = "Flask"
    GEOPHONE = "Geophone"
    GUN = "Gun"
    HEAD = "Head"
    HOUSING = "Housing"
    JIG = "Jig"
    JOINT = "Joint"
    NUCLEAR_DETECTOR = "Nuclear-Detector"
    PACKER = "Packer"
    PAD = "Pad"
    PANE = "Pane"
    POSITIONING = "Positioning"
    PRINTER = "Printer"
    RADIOACTIVE_SOURCE = "Radioactive-Source"
    SHIELD = "Shield"
    SIMULATOR = "Simulator"
    SKID = "Skid"
    SONDE = "Sonde"
    SPACER = "Spacer"
    STANDOFF = "Standoff"
    SYSTEM = "System"
    TOOL = "Tool"
    TOOL_MODULE = "Tool-Module"
    TRANSDUCER = "Transducer"
    VIBRATION_SOURCE = "Vibration-Source"


class EquipmentLocation(ValidatorEnum):
    # options for the 'location' attribute of Equipment, allowed by the standard
    LOGGING_SYSTEM = 'Logging-System'
    REMOTE = 'Remote'
    RIG = 'Rig'
    WELL = 'Well'


class FrameIndexType(ValidatorEnum):
    # values for frame index type allowed by the standard
    ANGULAR_DRIFT = 'ANGULAR-DRIFT'
    BOREHOLE_DEPTH = 'BOREHOLE-DEPTH'
    NON_STANDARD = 'NON-STANDARD'
    RADIAL_DRIFT = 'RADIAL-DRIFT'
    VERTICAL_DEPTH = 'VERTICAL-DEPTH'


class ProcessStatus(ValidatorEnum):
    # allowed values of the 'status' Attribute of Process
    COMPLETE = 'COMPLETE'
    ABORTED = 'ABORTED'
    IN_PROGRESS = 'IN-PROGRESS'


class ZoneDomains(ValidatorEnum):
    # allowed values for 'domain' Attribute of Zone
    # comments are quotes from RP66; 'Zone interval is'...:
    BOREHOLE_DEPTH = 'BOREHOLE-DEPTH',  # 'along the borehole'
    TIME = 'TIME',                      # 'elapsed time'
    VERTICAL_DEPTH = 'VERTICAL-DEPTH'   # 'depth along the Vertical Generatrix'


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
