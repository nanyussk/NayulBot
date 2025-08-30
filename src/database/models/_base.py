from pydantic.dataclasses import dataclass
from pydantic import Field, ConfigDict

from typing import Dict, Any, Union

__all__ = (
    'BaseDataClass',
    'DataClassMeta',
    'Field',
)

model_config = ConfigDict(
    populate_by_name=True
)

class DataClassMeta(type):
    def __new__(cls, name: str, bases: tuple, dct: Dict[str, Any]) -> type:
        new_cls = super().__new__(cls, name, bases, dct)
        return dataclass(
            frozen=True,
            kw_only=True,
            config=model_config
        )(new_cls)

class BaseDataClass(metaclass=DataClassMeta):
    """Modelo base para os modelos Pydantic."""
    model_config = model_config

    def to_dict(self, by_alias: bool = True) -> Dict[str, Union[str, int, float, bool, Dict[str, Any], None]]:
        """Converte o objeto para um dicionário, respeitando os aliases se `by_alias` for True."""
        
        from pydantic_core import to_jsonable_python
        return to_jsonable_python(self, by_alias=by_alias)