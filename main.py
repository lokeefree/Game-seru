# ==========================================
# AFTERFALL - MAIN GAME
# ==========================================

import pygame

import config

from world import World
from asset_loader import AssetLoader
from building import get_building_definition

from jobs import (
    assign_job,
    send_to_workplace
)

from systems.simulation import Simulation
from rendering.world_renderer import WorldRenderer
from rendering.hud_renderer import HUDRenderer
from game.game_state import GameState
from game.input_handler import InputHandler
from ui import SettlementUI
from relationships import RelationshipsSystem
from exploration import ExplorationSystem


# ==========================================
# INITIALIZATION
# ==========================================

pygame.init()

screen = pygame.display.set_mode(
    (
        config.SCREEN_WIDTH,
        config.SCREEN_HEIGHT
    )
)

pygame.display.set_caption(
    config.GAME_TITLE
)

clock = pygame.time.Clock()

assets = AssetLoader()

world = World()


# ==========================================
# SURVIVOR SPRITE FUNCTION
# ==========================================

def load_survivor_sprite(survivor):

    skin = assets.get_skin(
        survivor.appearance["skin"]
    )

    eyes = assets.get_eyes(
        survivor.appearance["eyes"]
    )

    hair = assets.get_hair(
        survivor.appearance["hair"]
    )

    top = assets.get_top(
        survivor.appearance["top"]
    )

    bottom = assets.get_bottom(
        survivor.appearance["bottom"]
    )

    shoes = assets.get_shoes(
        survivor.appearance["shoes"]
    )

    return (
        skin,
        eyes,
        hair,
        top,
        bottom,
        shoes
    )


# ==========================================
# STARTING SURVIVOR
# ==========================================

starting_survivor = world.survivors[0]

assign_job(
    starting_survivor,
    "Farmer"
)

send_to_workplace(
    starting_survivor,
    world
)


# ==========================================
# FONTS
# ==========================================

font = pygame.font.Font(
    None,
    24
)

small_font = pygame.font.Font(
    None,
    18
)

large_font = pygame.font.Font(
    None,
    32
)


# ==========================================
# GAME STATE
# ==========================================

# These values used to live as loose variables in main.py.
# They now live together in one object so later systems can share
# the current game state without adding more global variables here.
game = GameState(world)
input_handler = InputHandler()
exploration = ExplorationSystem()
simulation = Simulation(exploration)
world_renderer = WorldRenderer()
hud_renderer = HUDRenderer()
ui = SettlementUI(screen)
ui.exploration = exploration
ui.events = simulation.events
ui.research = simulation.research
ui.trading = simulation.trading
ui.relationships = simulation.relationships


# ==========================================
# CANDIDATE APPLICATION
# ==========================================

def draw_candidate_application(
    candidate
):

    overlay = pygame.Surface(
        (
            config.SCREEN_WIDTH,
            config.SCREEN_HEIGHT
        )
    )

    overlay.set_alpha(
        210
    )

    overlay.fill(
        (10, 12, 15)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    panel = pygame.Rect(
        120,
        55,
        912,
        540
    )

    pygame.draw.rect(
        screen,
        (32, 35, 40),
        panel
    )

    pygame.draw.rect(
        screen,
        (100, 105, 115),
        panel,
        2
    )

    title = large_font.render(
        "SURVIVOR APPLICATION",
        True,
        (255, 255, 255)
    )

    screen.blit(
        title,
        (
            390,
            75
        )
    )

    person = candidate.survivor

    sprite_parts = load_survivor_sprite(
        person
    )

    preview_x = 190
    preview_y = 145

    for sprite in sprite_parts:

        screen.blit(
            sprite,
            (
                preview_x,
                preview_y
            )
        )

    info_x = 390

    name_text = font.render(
        person.name,
        True,
        (255, 255, 255)
    )

    screen.blit(
        name_text,
        (
            info_x,
            140
        )
    )

    age_text = small_font.render(
        f"Age: {person.age}",
        True,
        (220, 220, 220)
    )

    screen.blit(
        age_text,
        (
            info_x,
            180
        )
    )

    health_text = small_font.render(
        f"Health: {person.health}/100",
        True,
        (220, 220, 220)
    )

    screen.blit(
        health_text,
        (
            info_x,
            210
        )
    )

    morale_text = small_font.render(
        f"Morale: {person.morale}/100",
        True,
        (220, 220, 220)
    )

    screen.blit(
        morale_text,
        (
            info_x,
            240
        )
    )

    # ==========================================
    # SKILLS
    # ==========================================

    skills_title = font.render(
        "SKILLS",
        True,
        (255, 255, 255)
    )

    screen.blit(
        skills_title,
        (
            390,
            285
        )
    )

    skill_y = 325

    for skill_name, value in (
        person.skills.items()
    ):

        skill_text = small_font.render(
            f"{skill_name}: {value}/10",
            True,
            (210, 210, 210)
        )

        screen.blit(
            skill_text,
            (
                390,
                skill_y
            )
        )

        bar_x = 540
        bar_y = skill_y + 3

        pygame.draw.rect(
            screen,
            (55, 58, 65),
            (
                bar_x,
                bar_y,
                120,
                14
            )
        )

        pygame.draw.rect(
            screen,
            (130, 175, 130),
            (
                bar_x,
                bar_y,
                value * 12,
                14
            )
        )

        skill_y += 28

    # ==========================================
    # TRAITS
    # ==========================================

    traits_title = font.render(
        "TRAITS",
        True,
        (255, 255, 255)
    )

    screen.blit(
        traits_title,
        (
            700,
            285
        )
    )

    trait_y = 325

    for trait in person.traits:

        trait_text = small_font.render(
            f"• {trait}",
            True,
            (210, 210, 210)
        )

        screen.blit(
            trait_text,
            (
                700,
                trait_y
            )
        )

        trait_y += 28

    # ==========================================
    # CAPACITY STATUS
    # ==========================================

    capacity_available = (
        world.has_population_space()
    )

    if capacity_available:

        capacity_text = small_font.render(
            "Settlement has available space.",
            True,
            (150, 220, 150)
        )

    else:

        capacity_text = small_font.render(
            "SETTLEMENT CAPACITY REACHED",
            True,
            (230, 150, 120)
        )

    screen.blit(
        capacity_text,
        (
            390,
            475
        )
    )

    # ==========================================
    # BUTTONS
    # ==========================================

    accept_button = pygame.Rect(
        430,
        515,
        130,
        45
    )

    reject_button = pygame.Rect(
        590,
        515,
        130,
        45
    )

    if capacity_available:

        pygame.draw.rect(
            screen,
            (65, 115, 75),
            accept_button
        )

    else:

        pygame.draw.rect(
            screen,
            (75, 75, 75),
            accept_button
        )

    pygame.draw.rect(
        screen,
        (120, 65, 65),
        reject_button
    )

    accept_text = small_font.render(
        "ACCEPT",
        True,
        (255, 255, 255)
    )

    reject_text = small_font.render(
        "REJECT",
        True,
        (255, 255, 255)
    )

    screen.blit(
        accept_text,
        (
            468,
            529
        )
    )

    screen.blit(
        reject_text,
        (
            628,
            529
        )
    )

    controls = small_font.render(
        "Click a button   |   C: close",
        True,
        (160, 160, 160)
    )

    screen.blit(
        controls,
        (
            425,
            570
        )
    )

    return (
        accept_button,
        reject_button
    )


# ==========================================
# MAIN LOOP
# ==========================================

while game.running:

    delta_time = (
        clock.tick(config.FPS)
        / 1000.0
    )

    game_minutes = 0

    # ==========================================
    # EVENTS / INPUT
    # ==========================================

    input_handler.handle_events(
        game,
        world,
        ui
    )

    # ==========================================
    # ==========================================
    # SIMULATION
    # ==========================================

    simulation.update(
        game,
        world,
        delta_time
    )

    # ==========================================
    # DRAW WORLD
    # ==========================================

    screen.fill(
        (35, 38, 42)
    )

    hud_renderer.draw_top_bar(
        screen,
        world,
        font,
        small_font
    )

    # ==========================================
    # WORLD OBJECTS
    # ==========================================

    world_renderer.draw(
        screen,
        world,
        game,
        small_font,
        load_survivor_sprite
    )

    # Keep the selected survivor valid if the population changes.
    if game.selected_survivor is not None and game.selected_survivor not in world.survivors:
        game.selected_survivor = world.survivors[0] if world.survivors else None

    hud_renderer.draw_status(
        screen,
        game.last_event_message,
        small_font
    )

    # ==========================================
    # SETTLEMENT COMMAND BAR / MANAGEMENT WINDOWS
    # ==========================================

    if not game.application_open:
        ui.draw(world, game)

    # ==========================================
    # CANDIDATE APPLICATION
    # ==========================================

    if (
        game.application_open
        and
        world.current_candidate is not None
    ):

        draw_candidate_application(
            world.current_candidate
        )

    # ==========================================
    # DISPLAY
    # ==========================================

    pygame.display.flip()


# ==========================================
# SHUTDOWN
# ==========================================

pygame.quit()