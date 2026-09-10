from collections.abc import Callable

import pygame
from pygame import Vector2

from assets import Assets
from drone import Drone
from link import Link
from zone import Zone


class Renderer:
    WINDOW_WIDTH = 1600
    WINDOW_HEIGHT = 1200

    @staticmethod
    def _make_ui(
        label: str,
        y: int,
        color: tuple[int, int, int],
    ) -> tuple[pygame.Surface, pygame.Rect]:
        surface = pygame.font.Font.render(
            Assets.FONT_BIG,
            label,
            True,
            color,
            (0, 0, 0)
        )
        return surface, surface.get_rect(left=16, top=y)

    def run(
        self,
        drones: list[Drone],
        end: Zone,
        zones: dict[str, Zone],
        links: list[Link],
        execute_turn: Callable[
            [Zone, list[Drone], list[Link], dict[str, Zone]],
            None,
        ],
    ) -> None:
        """Run the pygame rendering loop for the simulation."""
        pygame.init()
        pygame.display.set_icon(pygame.image.load('assets/drone.png'))
        screen = pygame.display.set_mode(
            (self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        )
        pygame.display.set_caption('Fly-in')
        clock = pygame.time.Clock()

        background = pygame.transform.scale(
            Assets.IMG['bg'], (self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        )
        background_rect = background.get_rect()

        ui_1, ui_1_rect = self._make_ui(
            'Mouse 1: Next turn.', 16, (255, 255, 255)
        )
        ui_2, ui_2_rect = self._make_ui(
            'Mouse 2: Pan the screen.', 64, (255, 255, 255)
        )
        ui_3, ui_3_rect = self._make_ui(
            'Space: Autoplay off.', 112, (255, 127, 127)
        )
        ui_4, ui_4_rect = self._make_ui(
            'Space: Autoplay ON.', 112, (127, 255, 127)
        )

        cam = Vector2(self.WINDOW_WIDTH / 2, self.WINDOW_HEIGHT / 2)
        autoplay = False
        autoplay_timer = 0
        running = True

        while running:
            for event in pygame.event.get():
                mouse_movement = pygame.mouse.get_rel()
                if pygame.mouse.get_pressed()[2]:
                    cam += Vector2(mouse_movement)

                keys = pygame.key.get_pressed()
                if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pygame.mouse.get_pressed()[0]:
                        execute_turn(end, drones, links, zones)
                if event.type == pygame.KEYDOWN:
                    if keys[pygame.K_SPACE]:
                        autoplay, autoplay_timer = not autoplay, 0

            screen.blit(background, background_rect)
            display_hovertext = False
            for link in links:
                link.draw(screen, cam)
            for zone in zones.values():
                zone.draw(screen, cam)
                if zone.rect.move(cam).collidepoint(pygame.mouse.get_pos()):
                    display_hovertext = True
                    hovertext, hoverrect = zone.nametext, zone.nametext_rect
            for drone in drones:
                drone.update()
                drone.draw(screen, cam)
            if display_hovertext:
                screen.blit(hovertext, hoverrect)

            screen.blit(ui_1, ui_1_rect)
            screen.blit(ui_2, ui_2_rect)
            if autoplay:
                screen.blit(ui_4, ui_4_rect)
            else:
                screen.blit(ui_3, ui_3_rect)

            pygame.display.flip()
            clock.tick(60)

            if autoplay:
                autoplay_timer -= clock.get_time()
                if autoplay_timer <= 0:
                    autoplay_timer += 250
                    execute_turn(end, drones, links, zones)

        pygame.quit()
