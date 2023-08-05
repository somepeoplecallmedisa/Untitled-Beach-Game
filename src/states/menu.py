import json

import pygame

from engine._types import EventInfo
from engine.animations import FadeTransition
from engine.asset_loader import load_assets
from engine.background import ParallaxBackground
from engine.button import Button
from engine.enums import GameStates
from src.common import FADE_SPEED, HEIGHT, WIDTH, DATA_PATH

pygame.font.init()
pygame.mixer.init()


class MenuInit:
    def __init__(self, ost_pos: float):
        self.assets = load_assets("menu")
        # triggers the state switch
        self.next_state = None
        # decides which state is next,
        # but doesn't trigger the state switch
        self._next_state = None
        self.exit = False

        self.ost_pos = ost_pos

    def update(self, event_info: EventInfo):
        pass

    def draw(self, screen: pygame.Surface, event_info: EventInfo):
        pass


class BackgroundStage(MenuInit):
    def __init__(self, ost_pos: float):
        super().__init__(ost_pos)

        self.background = ParallaxBackground(
            [
                (self.assets["bg0"], 0.05),
                (self.assets["bg1"], 0.15),
                (self.assets["bg2"], 0.3),
                (self.assets["bg3"], 0.4),
            ]
        )
        self.scroll = pygame.Vector2()

    def update(self, event_info: EventInfo):
        super().update(event_info)

        mouse_pos = event_info["mouse_pos"][0] // 10
        self.scroll.x += (
            (mouse_pos - self.scroll.x - WIDTH // 2) // 1 * event_info["dt"]
        )

    def draw(self, screen: pygame.Surface, event_info: EventInfo):
        super().draw(screen, event_info)

        self.background.draw(screen, self.scroll)


class ButtonStage(BackgroundStage):
    def __init__(self, ost_pos: float):
        super().__init__(ost_pos)

        button_colors = {
            "static": (109, 117, 141),
            "hover": (139, 147, 175),
            "text": (6, 6, 8),
        }
        size = pygame.Vector2(64, 16)
        button_texts = ("exit", "play")
        self.buttons = [
            Button(
                self.assets,
                (WIDTH - size.x - 10, HEIGHT - size.y * (i + 1) - 5 * (i + 1)),
                size,
                button_colors,
                text,
                4,
            )
            for i, text in enumerate(button_texts)
        ]

    def update(self, event_info: EventInfo):
        super().update(event_info)

        self.settings_active = False
        for button in self.buttons:
            button.update(event_info)

            if button.clicked:
                if button.text == "exit":
                    self.exit = True
                elif button.text == "play":
                    with open(DATA_PATH, "r") as file:
                        settings = json.loads(file.read())
                        if settings["run_intro"]:
                            self._next_state = GameStates.INTRO
                        else:
                            self._next_state = GameStates.GAME
                        self.ost_pos += pygame.mixer.music.get_pos()


    def draw(self, screen: pygame.Surface, event_info: EventInfo):
        super().draw(screen, event_info)

        for button in self.buttons:
            button.draw(screen)

    
class OSTStage(ButtonStage):
    def __init__(self, ost_pos: float):
        super().__init__(ost_pos)

        self.ost = self.assets["ost_quiet"]
        pygame.mixer.music.load(self.ost)
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.7)

        # set the ost to the last position
        pygame.mixer.music.rewind()
        pygame.mixer.music.set_pos(self.ost_pos / 1000)


class TransitionStage(OSTStage):
    def __init__(self, ost_pos: float):
        super().__init__(ost_pos)

        self.transition = FadeTransition(True, FADE_SPEED, (WIDTH, HEIGHT))

    def update(self, event_info: EventInfo):
        super().update(event_info)

        self.transition.update(event_info["dt"])
        if self._next_state is not None:
            self.transition.fade_in = False
            if self.transition.event:
                self.next_state = self._next_state

    def draw(self, screen: pygame.Surface, event_info: EventInfo):
        super().draw(screen, event_info)

        self.transition.draw(screen)


class MenuState(TransitionStage):
    pass
