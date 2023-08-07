import pygame

from engine._types import EventInfo
from engine.animations import FadeTransition
from engine.asset_loader import load_assets
from engine.enums import GameStates
from engine.utils import render_outline_text
from src.common import DATA_PATH, FADE_SPEED, FONT_PATH, HEIGHT, WIDTH

pygame.font.init()


class CreditsInit:
    def __init__(self, *args):
        self.assets = load_assets("credits")
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


class TextStage(CreditsInit):
    FONT = pygame.Font(FONT_PATH, 8)

    def __init__(self, *args):
        super().__init__(*args)

        self.FONT.align = pygame.FONT_CENTER

        text = "And just like that, you made it to the beach, fearlessly helping all the doofuses you've met along the way.\n\npress E to continue"
        self.text, _ = render_outline_text(text, self.FONT, "white")
        self.text_rect = self.text.get_rect(center=(WIDTH / 2, HEIGHT / 2))

    def update(self, event_info: EventInfo):
        super().update(event_info)

        for event in event_info["events"]:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                self._next_state = GameStates.MENU
                self.transition.fade_speed /= 5

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
            self.assets["beach"].fadeout(700)
            if self.transition.event:
                self.next_state = self._next_state

    def draw(self, screen: pygame.Surface, event_info: EventInfo):
        super().draw(screen, event_info)

        self.transition.draw(screen)


class CreditsState(TransitionStage):
    pass
