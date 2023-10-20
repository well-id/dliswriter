from abc import abstractmethod


class MultiLogicalRecord:
    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def set_origin_reference(self, value):
        pass
