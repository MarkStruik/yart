from __future__ import annotations
import random
from typing import List, Optional, Tuple, TYPE_CHECKING

import numpy as np
import tcod
from tcod.path import Pathfinder


from actions import Action, MeleeAction, MovementAction, WaitAction, BumpAction

if TYPE_CHECKING:
    from Entity import Actor

class BaseAI(Action):

    def perform(self) -> None:
        raise NotImplementedError()

    def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int,int]]:
        """
        Compute and return a path to the target postion
        
        If ther eis no valid path the returns an empty list
        """
        cost = np.array(self.entity.gamemap.tiles["walkable"], dtype=np.int8)

        for entity in self.entity.gamemap.entities:
            #check that an entity blocks movement and th ecosst ins't zero(blocking.)
            if entity.blocks_movement and cost[entity.x, entity.y]:
                # add to the cost of a blocked position
                # A lower number means more enimies will crowd behind each other in hallways.
                # A higher number means enemies will take longer paths in order to surround the player
                cost[entity.x, entity.y] += 10
        
        #creat a graph from the cost array and pass that graph to a pathfinder
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph=graph)

        pathfinder.add_root((self.entity.x, self.entity.y))

        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        return [(index[0], index[1]) for index in path]

class ConfusedEnemy(BaseAI):
    """
    A confused enemy will stumble around aimlessly for a
    given number of tuns, then revert back to its previous AI.
    
    if an actor accupies a tile it is randomly moving into it will attach
    """
    def __init__(self, entity: Actor, previous_ai: Optional[BaseAI], turns_remaining: int) -> None:
        super().__init__(entity)
        self.previous_ai = previous_ai
        self.turns_remaining = turns_remaining

    def perform(self) -> None:
        # revert the AI back to the original state if the effect has run its course
        if self.turns_remaining <= 0:
            self.engine.message_log.add_message(
                f"The {self.entity.name} is no longer confused."
            )
            self.entity.ai = self.previous_ai
        else:
            # Pick a random direction
            direction_x, direction_y = random.choice(
                [
                    (-1,-1),
                    (0,-1),
                    (1,-1),
                    (-1,0),
                    (1,0),
                    (-1,1),
                    (0,1),
                    (1,1),
                ]
            )
            self.turns_remaining -= 1

            return BumpAction(self.entity, direction_x, direction_y,).perform()

class HostileEnemy(BaseAI):
    def __init__(self, entity: Actor) -> None:
        super().__init__(entity)
        self.path: List[Tuple[int,int]] = []

    def perform(self) -> None:
        target = self.engine.player
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx),abs(dy))

        if self.engine.game_map.visible[self.entity.x, self.entity.y]:
            if distance <= 1:
                return MeleeAction(self.entity, dx,dy).perform()
            
            self.path = self.get_path_to(target.x, target.y)
        
        if self.path:
            dest_x, dest_y = self.path.pop(0)
            return MovementAction(
                self.entity,
                dest_x - self.entity.x, dest_y - self.entity.y
            ).perform()
        
        return WaitAction(self.entity).perform()