import sys
from pathlib import Path
from typing import ClassVar

import pygame
import webcolors
from pygame import Surface

from formatting import X, Y


class Assets:
    IMG: ClassVar[dict[str, pygame.Surface]] = {}
    NAMES: ClassVar[list[str]] = webcolors.names() + ['rainbow']

    pygame.font.init()
    FONT: ClassVar[pygame.font.Font] = pygame.font.Font(
        'font/gocake.otf', size=24
    )
    FONT_BIG: ClassVar[pygame.font.Font] = pygame.font.Font(
        'font/gocake.otf', size=48
    )

    @staticmethod
    def _get_black(image: str) -> Surface:
        result = Assets.IMG[image].copy()
        result.fill((255, 255, 255), special_flags=pygame.BLEND_ADD)
        result.blit(Assets.IMG[image], (0, 0), special_flags=pygame.BLEND_SUB)
        Assets.IMG.update({f'{image}:black': result})
        return result

    @staticmethod
    def _get_rainbow(image: str) -> Surface:
        result = Assets.IMG[image].copy()
        result.blit(
            Assets.IMG['rainbow'],
            (0, 0),
            special_flags=pygame.BLEND_MULT,
        )
        Assets.IMG.update({f'{image}:rainbow': result})
        return result

    @classmethod
    def get_colored(cls, image: str, color: str) -> Surface:
        """Return a cached color variant of an image surface."""
        if color not in cls.NAMES:
            print(
                f'{Y}Warning: Tried to get invalid color "{color}".{X}',
                file=sys.stderr
            )
            return cls.IMG[image]
        result_key = f'{image}:{color}'
        if result_key in cls.IMG:
            return cls.IMG[result_key]

        if color == 'black':
            return cls._get_black(image)
        if color == 'rainbow':
            return cls._get_rainbow(image)

        result = cls.IMG[image].copy()
        result.fill(
            webcolors.name_to_rgb(color),
            special_flags=pygame.BLEND_MULT,
        )
        cls.IMG.update({result_key: result})
        return result

    @classmethod
    def load_assets(cls, path: Path) -> None:
        "Load all `.png` assets from `path`. Does not work recursively."
        for f in path.iterdir():
            if f.suffix == '.png':
                key = str(f).removeprefix('assets/').removesuffix('.png')
                cls.IMG[key] = pygame.image.load(f)
