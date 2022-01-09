from __future__ import annotations

from typing import List, TYPE_CHECKING

from components.base_component import BaseComponent

if TYPE_CHECKING:
    from Entity import Actor, Item

class Inventory(BaseComponent):
    parent: Actor

    def __init__(self, capacity: int) -> None:
        super().__init__()
        self.capacity = capacity
        self.items: List[Item] = []

    def drop(self, item: Item) -> None:
        """
        Removes an item from the inventory and restores it to the game map, 
        at the players current position
        """
        self.items.remove(item)
        item.place(self.parent.x, self.parent.y, self.gamemap)

        if self.parent is self.engine.player:
            name = "You"
        else:
            name = f"The {self.parent.name}"

        self.engine.message_log.add_message(f"{name} dropped the {item.name}")
