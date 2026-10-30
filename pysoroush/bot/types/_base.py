"""
Base class for all PySoroush types.
Provides automatic serialization and deserialization between JSON
dictionaries and Python objects.
"""

import sys
import types
import typing
import dataclasses
from typing import Any, Dict, Type, TypeVar

T = TypeVar("T", bound="BaseType")


@dataclasses.dataclass
class BaseType:
    """
    Base dataclass for Soroush API types.
    """

    @classmethod
    def _convert_value(cls, value: Any, hint: Any) -> Any:
        """Recursively converts a value based on its type hint."""
        if value is None or hint is None:
            return value

        origin = typing.get_origin(hint)
        args = typing.get_args(hint)

        # Unwrap Optional (Union[T, None])
        if origin is typing.Union or (hasattr(types, "UnionType") and origin is types.UnionType):
            real_types = [t for t in args if t is not type(None)]
            if len(real_types) == 1:
                return cls._convert_value(value, real_types[0])
            return value

        # Handle Lists (including nested lists)
        if origin is list and args:
            item_type = args[0]
            if isinstance(value, list):
                return [cls._convert_value(i, item_type) for i in value]
            return value

        # Handle BaseType objects
        if isinstance(hint, type) and issubclass(hint, BaseType):
            if isinstance(value, dict):
                return hint.from_dict(value)
            return value

        # Return primitive types as-is
        return value

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Create an instance of the class from a dictionary.
        Handles nested BaseType objects and lists of BaseType objects.
        """
        if not data:
            return None

        module = sys.modules.get(cls.__module__)
        globalns = module.__dict__.copy() if module else {}
        
        # Inject the parent package namespace to resolve circular forward references
        if module and module.__package__:
            pkg = sys.modules.get(module.__package__)
            if pkg:
                globalns.update(pkg.__dict__)

        try:
            hints = typing.get_type_hints(cls, globalns=globalns)
        except Exception:
            hints = {}

        field_names = {f.name for f in dataclasses.fields(cls)}
        kwargs = {}

        for k, v in data.items():
            if k not in field_names or v is None:
                continue

            hint = hints.get(k)
            if hint is None:
                kwargs[k] = v
            else:
                kwargs[k] = cls._convert_value(v, hint)

        return cls(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the object to a dictionary.
        Omits fields that are None.
        """
        result = {}
        for k, v in self.__dict__.items():
            if v is None:
                continue
            if isinstance(v, BaseType):
                result[k] = v.to_dict()
            elif isinstance(v, list):
                result[k] = [
                    i.to_dict() if isinstance(i, BaseType) else i for i in v
                ]
            else:
                result[k] = v
        return result
