import json

import pygame

from engine._types import EventInfo
from engine.animations import FadeTransition
from engine.enums import GameStates
from engine.utils import render_outline_text
from src.common import DATA_PATH, FADE_SPEED, FONT_PATH, HEIGHT, WIDTH
from engine.asset_loader import load_assets

pygame.font.init()


class IntroInit:
    def __init__(self, *args):
        self.assets = load_assets("intro")
        self.assets["beach"].play(-1)
        # triggers the state switch
        self.next_state = None
        # decides which state is next,
        # but doesn't trigger the state switch
        self._next_state = None
        self.exit = False
        self.ost_pos = 0

    def update(self, event_info: EventInfo):
        pass

    def draw(self, screen: pygame.Surface, event_info: EventInfo):
        screen.fill((6, 6, 8))


class TextStage(IntroInit):
    FONT = pygame.Font(FONT_PATH, 8)

    def __init__(self, *args):
        super().__init__(*args)

        self.FONT.align = pygame.FONT_CENTER

        text = "game\ndescription\nthing\nhere"
        self.text, _ = render_outline_text(text, self.FONT, "white")
        self.text_rect = self.text.get_rect(center=(WIDTH / 2, HEIGHT / 2))

    def update(self, event_info: EventInfo):
        super().update(event_info)

        for event in event_info["events"]:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                self._next_state = GameStates.GAME

                with open(DATA_PATH, "r") as file:
                    settings = json.loads(file.read())

                settings["run_intro"] = False

                with open(DATA_PATH, "w") as file:
                    file.write(json.dumps(settings, indent=4))

    def draw(self, screen: pygame.Surface, event_info: EventInfo):
        super().draw(screen, event_info)

        screen.blit(self.text, self.text_rect)


class TransitionStage(TextStage):
    def __init__(self, *args):
        super().__init__(*args)

        self.transition = FadeTransition(True, FADE_SPEED, (WIDTH, HEIGHT))

    def update(self, event_info: EventInfo):
        super().update(event_info)

        self.transition.update(event_info["dt"])
        if self._next_state is not None:
            self.transition.fade_in = False
            self.assets["beach"].fadeout(450)
            if self.transition.event:
                self.next_state = self._next_state

    def draw(self, screen: pygame.Surface, event_info: EventInfo):
        super().draw(screen, event_info)

        self.transition.draw(screen)


class IntroState(TransitionStage):
    pass
