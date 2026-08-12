# Suppress errors for module imports not at top of file,
# because we have to set the env variable before pygame imports.
# flake8: noqa: E402
import sys
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pathlib import Path

import pygame
from pygame import Vector2
from lark import LarkError

import assets
from zone import Zone
from drone import Drone
from link import Link
from parser import parse, ParsingError
from builder import build
from formatting import X, H, D, R, Y


turncount = 0


def execute_turn(goal: Zone, drones: list[Drone], links: list[Link]) -> None:
    "Allow all drones to make a move towards the goal."
    global turncount
    if all([drone.zone is goal for drone in drones]):
        return
    turncount += 1
    for link in links:
        link.drone_load = 0
    for drone in drones:
        if drone.zone is goal:
            continue
        drone.move(links)
    print()


def list_maps(directory: Path, index: int = 0) -> list[Path]:
    "Print all maps in a directory, recursively."
    result = []
    print(f'\n{H}{directory}/{X}')
    for file in directory.iterdir():
        if not file.is_dir():
            if file.suffix == '.txt':
                result += [file]
                print(
                    f'{index:>4}.', str(file)
                    .removeprefix(str(directory) + '/')
                    .removesuffix('.txt'))
                index += 1
    for file in directory.iterdir():
        if file.is_dir():
            recursive_result = list_maps(file, index)
            index += len(recursive_result)
            result += recursive_result
    return result


# Get the map file.
# -----------------------------------------------------------------------------
if len(sys.argv) > 1:
    data = Path(sys.argv[1])
else:
    print(f'{D}No map argument given, defaulting to interactive mode.{X}')

    try:
        maps = []
        path_maps = Path('maps')
        if path_maps.exists():
            maps += list_maps(path_maps)
        maps += list_maps(Path('testmaps'), len(maps))
    except OSError as e:
        print(f'{R}An error occurred while displaying map names.{X}',
              file=sys.stderr)
        print(f'{R}Error: {e}{X}', file=sys.stderr)
        sys.exit(1)

    map_index = int(input('Input index of map to load: ' + H))
    if 0 <= map_index < len(maps):
        data = Path(maps[map_index])
    else:
        print(
            f'{R}Error: input must be an integer'
            f' between 0 and {len(maps) - 1}.{X}',
            file=sys.stderr)
        sys.exit(1)
    print(X)


# Set up pygame.
# -----------------------------------------------------------------------------
pygame.init()
w, h = 1600, 1200
pygame.display.set_icon(pygame.image.load('assets/drone.png'))

screen = pygame.display.set_mode((w, h))
pygame.display.set_caption('Fly-in')
clock = pygame.time.Clock()

assets.load_assets(Path('assets'))
bg = pygame.transform.scale(assets.IMG['bg'], (w, h))
bg_rect = bg.get_rect()


# Build the map.
# -----------------------------------------------------------------------------
try:
    drones, start, end, zones, links = build(parse(data))
except (ParsingError, LarkError, OSError) as e:
    print(f'{R}Error: {e}{X}', file=sys.stderr)
    sys.exit(1)


# Calculate all paths in advance, taking expected congestion in account.
# -----------------------------------------------------------------------------
traffic = {x: 0 for x in zones}
for drone in drones:
    for zone in drone.dijkstras(list(zones.values()), end, traffic):
        traffic[zone.name] += 1
if any([not drone.path for drone in drones]):
    print(
        f'{Y}Warning: Drones could not find a path to the exit.{X}',
        file=sys.stderr
    )


# Initialize UI.
# -----------------------------------------------------------------------------
ui_1 = pygame.font.Font.render(
    assets.FONT_BIG,
    'Mouse 1: Next turn.',
    True,
    (255, 255, 255),
    (0, 0, 0)
)
ui_1_rect = ui_1.get_rect(left=16, top=16)
ui_2 = pygame.font.Font.render(
    assets.FONT_BIG,
    'Mouse 2: Pan the screen.',
    True,
    (255, 255, 255),
    (0, 0, 0)
)
ui_2_rect = ui_2.get_rect(left=16, top=64)
ui_3 = pygame.font.Font.render(
    assets.FONT_BIG,
    'Space: Autoplay off.',
    True,
    (255, 127, 127),
    (0, 0, 0)
)
ui_3_rect = ui_3.get_rect(left=16, top=112)
ui_4 = pygame.font.Font.render(
    assets.FONT_BIG,
    'Space: Autoplay ON.',
    True,
    (127, 255, 127),
    (0, 0, 0)
)
ui_4_rect = ui_4.get_rect(left=16, top=112)


# Main pygame loop.
# -----------------------------------------------------------------------------
cam = Vector2(w / 2, h / 2)
autoplay, autoplay_timer = False, 0
running = True
while running:
    # Handle events.
    for event in pygame.event.get():
        mouse_movement = pygame.mouse.get_rel()
        if pygame.mouse.get_pressed()[2]:
            cam += Vector2(mouse_movement)

        keys = pygame.key.get_pressed()
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                execute_turn(end, drones, links)
        if event.type == pygame.KEYDOWN:
            if keys[pygame.K_SPACE]:
                autoplay, autoplay_timer = not autoplay, 0

    # Update and draw objects.
    screen.blit(bg, bg_rect)
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

    # Draw UI.
    screen.blit(ui_1, ui_1_rect)
    screen.blit(ui_2, ui_2_rect)
    if autoplay:
        screen.blit(ui_4, ui_4_rect)
    else:
        screen.blit(ui_3, ui_3_rect)

    # Update screen and clock.
    pygame.display.flip()
    clock.tick(60)

    if autoplay:
        autoplay_timer -= clock.get_time()
        if autoplay_timer <= 0:
            autoplay_timer += 250
            execute_turn(end, drones, links)

# Optionally print total turn count for debugging.
# print('Turn count:', turncount)
pygame.quit()
