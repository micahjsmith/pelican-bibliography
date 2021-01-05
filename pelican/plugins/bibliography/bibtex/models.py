from dataclasses import dataclass

@dataclass
class BibtexEntry:
    type: str
    key: str
    fields: dict
