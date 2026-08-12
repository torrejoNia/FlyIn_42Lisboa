import sys
from pathlib import Path

import webcolors
import pygame
from pygame import Surface

from formatting import X, Y


IMG: dict[str, pygame.Surface] = {}
NAMES: list[str] = webcolors.names() + ['rainbow']

pygame.font.init()
FONT: pygame.font.Font = pygame.font.Font(
    'font/lovely-pixels.otf', size=24)
FONT_BIG: pygame.font.Font = pygame.font.Font(
    'font/lovely-pixels.otf', size=48)


def get_colored(image: str, color: str) -> Surface:
    """Tries to get the colored version of an image.
    If it doesn't exist yet,
    creates a colored version of the asset and stores it in `assets`.
    Returns the resulting surface."""
    def get_black(image: str) -> Surface:
        result = IMG[image].copy()
        result.fill((255, 255, 255), special_flags=pygame.BLEND_ADD)
        result.blit(IMG[image], (0, 0), special_flags=pygame.BLEND_SUB)
        IMG.update({f'{image}:black': result})
        return result

    def get_rainbow(image: str) -> Surface:
        result = IMG[image].copy()
        result.blit(IMG['rainbow'], (0, 0), special_flags=pygame.BLEND_MULT)
        IMG.update({f'{image}:rainbow': result})
        return result

    if color not in NAMES:
        print(
            f'{Y}Warning: Tried to get invalid color "{color}".{X}',
            file=sys.stderr
        )
        return IMG[image]
    result_key = f'{image}:{color}'
    if result_key in IMG:
        return IMG[result_key]

    if color == 'black':
        return get_black(image)
    elif color == 'rainbow':
        return get_rainbow(image)

    result = IMG[image].copy()
    result.fill(
        webcolors.name_to_rgb(color), special_flags=pygame.BLEND_MULT)
    IMG.update({result_key: result})
    return result


def load_assets(path: Path) -> None:
    "Load all `.png` assets from `path`. Does not work recursively."
    for f in path.iterdir():
        if f.suffix == '.png':
            IMG.update({
                str(f).removeprefix('assets/').removesuffix('.png'):
                pygame.image.load(f).convert_alpha()
            })
