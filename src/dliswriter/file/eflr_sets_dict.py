from collections import defaultdict
from typing import Generator, Optional, TypeVar, Union, TYPE_CHECKING

from dliswriter.logical_record.core.eflr import EFLRSet

if TYPE_CHECKING:
    from dliswriter.logical_record.core.eflr.eflr_item import EFLRItem


AnyEFLRSet = TypeVar("AnyEFLRSet", bound="EFLRSet")
AnyEFLRItem = TypeVar("AnyEFLRItem", bound="EFLRItem")


class EFLRSetsDict(defaultdict):
    """Keep track of the defined EFLRSet objects.

    This is a nested dictionary.
    At the top level, it is a defaultdict whose keys are EFLRSet classes. The values are simple dicts.
    At the second level, the keys are EFLRSet instances names and the values are the corresponding instances.
    """

    def __init__(self) -> None:
        """Initialise EFLRSetsDict. Set it up to return an empty dictionary for a new (missing) key."""

        super().__init__(lambda: {})

    def add_set(self, eflr_set: EFLRSet) -> None:
        """Register a new EFLRSet instance in the structure."""

        if eflr_set.set_name in self[eflr_set.__class__]:
            raise RuntimeError(f"{eflr_set.__class__.__name__} with set name '{eflr_set.set_name}' "
                               f"already added to the file")

        self[eflr_set.__class__][eflr_set.set_name] = eflr_set

    def try_add_set(self, eflr_set: EFLRSet) -> bool:
        """Try to register a new EFLRSet instance in the structure. Return True on success, False otherwise."""

        if eflr_set.set_name in self[eflr_set.__class__]:
            return False
        else:
            self[eflr_set.__class__][eflr_set.set_name] = eflr_set
            return True

    def get_or_make_set(self, eflr_set_type: type[AnyEFLRSet], set_name: Optional[str] = None) -> AnyEFLRSet:
        """Given an EFLRSet subclass and name, either retrieve a relevant EFLRSet from the structure or create it.

        Args:
            eflr_set_type   :   Subclass of EFLRSet - type of the EFLRSet to be obtained.
            set_name        :   Name of the EFLRSet instance.

        Returns:
            An EFLRSet instance of given subtype and name, registered in the structure.
        """

        # dict mapping set names on EFLRSet (subclass) instances
        eflr_set_dict: dict[Union[str, None], AnyEFLRSet] = self[eflr_set_type]

        # instance of the EFLRSet with the given set name - if exists
        eflr_set_instance = eflr_set_dict.get(set_name, None)

        # (if not exists - create it)
        if eflr_set_instance is None:
            eflr_set_instance = eflr_set_type(set_name=set_name)
            eflr_set_dict[set_name] = eflr_set_instance

        return eflr_set_instance

    def get_all_items_for_set_type(self, eflr_set_type: type[EFLRSet]) -> Generator[AnyEFLRItem, None, None]:
        """Retrieve all EFLRItem instances registered for all instances of given EFLRSet subclass."""

        for value in self[eflr_set_type].values():
            yield from value.get_all_eflr_items()
