from abc import ABC, abstractmethod

class BaseDBManager(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def save_dataframe(self, df, table_name: str, mode: str = "append"):
        pass

    @abstractmethod
    def close(self):
        pass