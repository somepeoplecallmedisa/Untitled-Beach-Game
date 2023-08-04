import json
from pathlib import Path
from typing import List, Sequence

import pygame

pygame.mixer.init()


def get_images(
    sheet: pygame.Surface,
    size: Sequence[int],
) -> List[pygame.Surface]:
    """
    Converts a sprite sheet to a list of surfaces
    Parameters:
        sheet: A pygame.Surface that contains the sprite sheet
        size: Size of a sprite in the sprite sheet
    """
    images = []

    width, height = size

    # loop through all sprites in the sprite sheet
    rows = int(sheet.get_height() / height)
    columns = int(sheet.get_width() / width)

    for row in range(rows):
        for col in range(columns):
            image = sheet.subsurface(pygame.Rect((col * width), (row * height), *size))

            images.append(image)

    return images


def load_assets(state: str) -> dict:
    assets = {}
    path = Path("assets/loadable/")

    json_files = path.rglob("*.json")
    for metadata_f in json_files:
        metadata = json.loads(metadata_f.read_text())
        for file, data in metadata.items():
            if state not in data["states"]:
                continue

            file_extension = file[file.find(".") :]
            complete_path = metadata_f.parent / file

            if file_extension in (".png", ".jpg"):
                if data["convert_alpha"]:
                    image = pygame.image.load(complete_path).convert_alpha()
                else:
                    image = pygame.image.load(complete_path).convert()

                asset = image

                if data["sprite_sheet"] is not None:
                    asset = get_images(image, data["sprite_sheet"])

            elif file_extension in (".mp3", ".wav"):
                if data["bgm"]:
                    asset = pygame.mixer.Sound(complete_path)
                    asset.set_volume(data["volume"])

            assets[file.replace(file_extension, "")] = asset

    return assets
