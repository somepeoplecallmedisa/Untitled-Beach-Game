import json

import pygame

from engine._types import EventInfo
from engine.enums import GameStates
from src.common import HEIGHT, WIDTH
from src.states.credits import CreditsState
from src.states.game_state import GameState
from src.states.intro import IntroState
from src.states.menu import MenuState


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
        self.clock = pygame.time.Clock()

        self.states = {
            GameStates.GAME: GameState,
            GameStates.MENU: MenuState,
            GameStates.INTRO: IntroState,
            GameStates.CREDITS: CreditsState,
        }
        self.state = GameStates.MENU
        self.game_state = self.states[self.state](0)

    def _exit(self):
        if self.state == GameStates.GAME:
            self.game_state.save()
        pygame.quit()
        raise SystemExit

    def run(self):
        while True:
            dt = self.clock.tick(60) / 100
            dt = min(0.7, dt)

            event_info: EventInfo = {
                "events": pygame.event.get(),
                "dt": dt,
                "keys": pygame.key.get_pressed(),
                "mouse_pos": pygame.mouse.get_pos(),
                "mouse_keys": pygame.mouse.get_pressed(),
            }

            for event in event_info["events"]:
                if event.type == pygame.QUIT:
                    self._exit()

            if self.game_state.next_state is not None:
                self.state = self.game_state.next_state
                self.game_state = self.states[self.state](self.game_state.ost_pos)

            self.game_state.draw(self.screen, event_info)
            self.game_state.update(event_info)

            if self.game_state.exit:
                self._exit()

            pygame.display.flip()
            pygame.display.set_caption(f"Untitled Beach Game | FPS: {self.clock.get_fps():.0f}")
