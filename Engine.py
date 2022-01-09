from __future__ import annotations

from typing import TYPE_CHECKING 

from tcod.context import Context
from tcod.console import Console
from tcod.event import Event
from tcod.map import compute_fov

from input_handlers import MainGameEventHandler
from message_log import MessageLog
from render_function import render_bar, render_names_at_mouse_location

if TYPE_CHECKING:
    from Entity import Actor
    from game_map import GameMap
    from input_handlers import EventHandler

class Engine:
    game_map: GameMap

    def __init__(self, player: Actor) -> None:
        self.event_handler: EventHandler = MainGameEventHandler(self)
        self.player = player
        self.mouse_location = (0,0)
        self.message_log = MessageLog()

    def handle_enemy_turns(self)-> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                entity.ai.perform()

    def update_fov(self) -> None:
        """Recompute the visible area based on the players point ov view."""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8,
        )
        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console) -> None:
        self.game_map.render(console)
        self.message_log.render(console=console, x=22, y=45, width=39, height=5)

        render_bar(
            console = console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=20
        )

        render_names_at_mouse_location(console=console, x=22,y=44, engine=self)