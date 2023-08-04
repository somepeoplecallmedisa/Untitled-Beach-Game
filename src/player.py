import json

import pygame

from engine._types import EventInfo, Position
from engine.animations import Animation
from engine.camera import Camera
from engine.enums import EntityStates
from engine.utils import reverse_animation
import itertools


class Player:
    SAVE_PATH = "assets/data/player_save.json"

    def __init__(self, assets: dict):
        self.animations = {
            "walk_left": Animation(assets["player_walk"], 0.8),
            "idle_left": Animation(assets["player_idle"], 0.05),
            "jump_left": Animation(assets["player_jump"], 0),
        }
        self.animations |= {
            "walk_right": reverse_animation(self.animations["walk_left"]),
            "idle_right": reverse_animation(self.animations["idle_left"]),
            "jump_right": reverse_animation(self.animations["jump_left"]),
        }
        self.facing = "right"
        self.state = EntityStates.IDLE

        jump_sfx_arr = [assets[f"jump_{i}"] for i in range(1, 5)]
        self.jump_cycle = itertools.cycle(jump_sfx_arr)
        self.jump_sfx = jump_sfx_arr[0]

        self.rect = assets["player_idle"][0].get_frect()
        self.vel = pygame.Vector2()
        self.speed = 4
        self.gravity = 3.5
        self.jump_height = 15
        self.jumping = False
        self.alive = True

        self.new_quest = False

        self.load_save()

    def load_save(self):
        with open(self.SAVE_PATH, "r") as f:
            self.settings = json.loads(f.read())
            self.rect.topleft = self.settings["checkpoint_pos"]

    def dump_save(self):
        with open(self.SAVE_PATH, "w") as f:
            f.write(json.dumps(self.settings, indent=4))

    def move(self, event_info: EventInfo):
        dt = event_info["dt"]
        keys = event_info["keys"]

        self.state = EntityStates.IDLE
        self.vel.x = 0
        if not (keys[pygame.K_a] and keys[pygame.K_d]):
            if keys[pygame.K_d]:
                self.state = EntityStates.WALK
                self.facing = "right"
                self.vel.x = self.speed
            elif keys[pygame.K_a]:
                self.state = EntityStates.WALK
                self.facing = "left"
                self.vel.x = -self.speed

        self.vel.y += self.gravity * dt

        for event in event_info["events"]:
            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_SPACE
                and not self.jumping
            ):
                self.jumping = True
                self.vel.y = -self.jump_height

                self.jump_sfx = next(self.jump_cycle)
                self.jump_sfx.play()
                
        if self.jumping:
            self.state = EntityStates.JUMP

    def update(self, event_info: EventInfo):
        # the player shouldn't be able to walk outside the map
        self.rect.x = max(0, self.rect.x)
        if self.rect.y > 260:
            self.alive = False
            self.vel.x = 0
        else:
            self.move(event_info)

    def draw(self, screen: pygame.Surface, camera: Camera, event_info: EventInfo):
        animation = self.animations[f"{self.state.value}_{self.facing}"]
        animation.play(screen, camera.apply(self.rect), event_info["dt"])
