"""
memory_stores/list_store.py

Stores memories as a list.
"""

MemoryItem = namedtuple("MemoryItem", ["key", "value"])


class ListMemory:
    def __init__(self) -> None:
        self.items: list[MemoryItem] = []
