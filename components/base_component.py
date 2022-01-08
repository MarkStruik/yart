from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Engine import Engine
    from Entity import Entity

class BaseComponent:
    entity: Entity

    @property
    def engine(self) -> Engine:
        return self.entity.gamemap.engine