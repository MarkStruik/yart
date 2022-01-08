from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Engine import Engine
    from Entity import Entity

class Action:
    def perform(self, engine: Engine, entity: Entity) -> None:
        """
        Perform this action with the objects needed to determine its scope

        `engine` is the scope this action is being performed in.
        `entity` is the object performing the action

        this method must be overridden by Action subclasses        
        """
        raise NotImplementedError()

class EscapeAction(Action):
    def perform(self, engine: Engine, entity: Entity) -> None:
        raise SystemExit()

class ActionWitghDirection(Action):
    def __init__(self, dx:int, dy: int):
        self.dx = dx
        self.dy = dy

    def perform(self, engine: Engine, entity: Entity) -> None:
        raise NotImplementedError()

class MovementAction(ActionWitghDirection):

    def perform(self, engine: Engine, entity: Entity) -> None:
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy

        if not engine.game_map.in_bounds(dest_x, dest_y):
            return #destination is out of bounds
        if not engine.game_map.tiles["walkable"][dest_x,dest_y]:
            return #destination is blocked by non walkable tile
        if engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            return # destination is blocked by an entity

        entity.move(self.dx, self.dy)

class MeleeAction(ActionWitghDirection):
    def perform(self, engine: Engine, entity: Entity) -> None:
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy
        target = engine.game_map.get_blocking_entity_at_location(dest_x,dest_y)
        if not target:
            return # nothing to see here :)

        print(f"You kick the {target.name}, much to its annoyance!")

class BumpAction(ActionWitghDirection):
    def perform(self, engine: Engine, entity: Entity) -> None:
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy

        if engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            return MeleeAction(self.dx, self.dy).perform(engine, entity)
        else:
            return MovementAction(self.dx, self.dy).perform(engine, entity)

       