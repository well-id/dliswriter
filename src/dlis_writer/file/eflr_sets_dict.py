from collections import defaultdict
from typing import Generator, Optional

from dlis_writer.logical_record.core.eflr import EFLRItem, EFLRSet


class EFLRSetsDict(defaultdict):
    def __init__(self):
        super().__init__(lambda: {})

    def add_set(self, eflr_set: EFLRSet) -> None:
        if eflr_set.set_name in self[eflr_set.__class__]:
            raise RuntimeError(f"{eflr_set.__class__.__name__} with set name '{eflr_set.set_name}' "
                               f"already added to the file")

        self[eflr_set.__class__][eflr_set.set_name] = eflr_set

    def get_or_make_set(self, eflr_item_type: type[EFLRItem], set_name: Optional[str] = None) -> EFLRSet:

        # the relevant EFLRSet subclass
        eflr_set_type = eflr_item_type.parent_eflr_class

        # dict mapping set names on EFLRSet (subclass) instances
        eflr_set_dict = self[eflr_set_type]

        # instance of the EFLRSet with the given set name - if exists
        eflr_set_instance = eflr_set_dict.get(set_name, None)

        # (if not exists - create it)
        if eflr_set_instance is None:
            eflr_set_instance = eflr_set_type(set_name=set_name)
            eflr_set_dict[set_name] = eflr_set_instance

        return eflr_set_instance

    def get_all_items_for_set_type(self, eflr_set_type: type[EFLRSet]) -> Generator:
        for value in self[eflr_set_type].values():
            yield from value.get_all_eflr_items()
