import json
from typing import Dict, Sequence, Tuple

import pygame

from engine._types import Color, EventInfo, Position
from src.common import FONT_PATH


class Button:
    """
    Clickable button
    """

    def __init__(
        self,
        assets: dict,
        pos: Position,
        size: Position,
        colors: Dict[str, Color],
        text: str,
        border_radius: int = None,
    ) -> None:
        self.colors = colors

        self.rect = pygame.Rect(pos, size)

        self.text = text
        font = pygame.Font(FONT_PATH, 8)
        self.text_surf = font.render(text, False, colors["text"])
        self.text_pos = self.text_surf.get_rect(center=self.rect.center).topleft

        self.border_radius = border_radius

        self.state = "static"
        self.clicked = False
        self.toggle = False
        self.hover_sound_played = False

        self.assets = assets

    def update(self, event_info: EventInfo) -> None:
        self.clicked = False
        self.state = "static"

        if self.rect.collidepoint(event_info["mouse_pos"]):
            for event in event_info["events"]:
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.clicked = True
                    self.toggle = not self.toggle
                    self.assets["button_high"].play()

            self.state = "hover"

        # play the hover sound but only once
        if self.state == "hover" and not self.hover_sound_played:
            self.hover_sound_played = True
            self.assets["button_low"].play()
        # this resets the sound
        elif self.state != "hover" and self.hover_sound_played:
            self.hover_sound_played = False

    def draw(self, screen: pygame.Surface) -> None:
        if self.border_radius is None:
            pygame.draw.rect(screen, self.colors[self.state], self.rect)
        else:
            pygame.draw.rect(
                screen,
                self.colors[self.state],
                self.rect,
                border_radius=self.border_radius,
            )

        screen.blit(self.text_surf, self.text_pos)
