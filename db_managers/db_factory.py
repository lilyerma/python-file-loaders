from .base import BaseDBManager

class DBManagerFactory:
    _registry = {}

    @classmethod
    def register(cls, db_type: str, manager_cls):
        cls._registry[db_type] = manager_cls

    @classmethod
    def create_manager(cls, db_type: str, **kwargs) -> BaseDBManager:
        manager_cls = cls._registry.get(db_type.lower())
        if not manager_cls:
            raise ValueError(f"Неизвестный тип базы данных / движка: {db_type}")
        return manager_cls(**kwargs)