from typing import Dict, Any


class Style:
    def __init__(self) -> None:
        self._attributes = {}

    def get_attr(self, key: str) -> Any:
        if not key in self._attributes:
            return None

        return self._attributes[key]

    def set_attr(self, key: str, value: Any):
        self._attributes[key] = value

    @staticmethod
    def from_dict(s: Dict):
        style = Style()

        for key in s:
            style.set_attr(key, s[key])

        return style


class Theme(object):
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Theme, cls).__new__(cls)

        return cls.instance

    @property
    def style(self):
        return self._style

    def use(self, style: Style):
        self._style = style
