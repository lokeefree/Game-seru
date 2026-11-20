import asyncio
import random
import pygame

# ============================================================
# MINI RACING
# Browser-friendly Pygame version for Pygbag
#
# This game uses only shapes and built-in fonts:
# no external images, audio files, or filesystem loading.
# ============================================================

WIDTH = 480
HEIGHT = 650
FPS = 60

# ----------------------------
# Initialize Pygame
# ----------------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MINI RACING")
clock = pygame.time.Clock()

# ----------------------------
# Colors
# ----------------------------
WHITE = (245, 245, 245)
BLACK = (15, 18, 24)
DARK = (28, 34, 44)
GRAY = (67, 70, 76)
GREEN = (35, 130, 65)
BLUE = (35, 135, 255)
RED = (230, 55, 55)
YELLOW = (255, 210, 55)
CYAN = (70, 225, 255)
MUTED = (170, 180, 190)

# ----------------------------
# Fonts
# ----------------------------
font = pygame.font.Font(None, 34)
small_font = pygame.font.Font(None, 25)
big_font = pygame.font.Font(None, 66)
title_font = pygame.font.Font(None, 76)

# ----------------------------
# Track and car settings
# ----------------------------
ROAD_LEFT = 65
ROAD_RIGHT = 415
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
LANES = (125, 240, 355)
LANE_MARKERS = (182, 297)

PLAYER_START_X = 240
PLAYER_Y = 455
PLAYER_SPEED = 390

BASE_WORLD_SPEED = 300
MAX_WORLD_SPEED = 600
MIN_WORLD_SPEED = 150

# ----------------------------
# On-screen controls
# ----------------------------
left_button = pygame.Rect(18, 565, 86, 65)
right_button = pygame.Rect(112, 565, 86, 65)
brake_button = pygame.Rect(280, 565, 86, 65)
gas_button = pygame.Rect(374, 565, 88, 65)

start_button = pygame.Rect(100, 395, 280, 72)
restart_button = pygame.Rect(100, 420, 280, 75)

# A pointer can be a mouse or an individual touch.
# Keeping pointers separate allows two-finger controls.
active_pointers = {}

# ----------------------------
# Game state
# ----------------------------
player_x = float(PLAYER_START_X)
world_speed = float(BASE_WORLD_SPEED)
score = 0
enemies = []
spawn_timer = 0.0
road_offset = 0.0

game_started = False
game_over = False
running = True


# ============================================================
# Drawing helpers
# ============================================================

def draw_text(surface, text, font_type, color, center_x, center_y):
    image = font_type.render(str(text), True, color)
    rect = image.get_rect(center=(int(center_x), int(center_y)))
    surface.blit(image, rect)


def draw_car(surface, x, y, color):
    """Draw a simple top-down car using Pygame shapes."""
    x = int(x)
    y = int(y)

    # Wheels
    pygame.draw.rect(surface, BLACK, (x - 27, y + 14, 11, 25), border_radius=4)
    pygame.draw.rect(surface, BLACK, (x + 16, y + 14, 11, 25), border_radius=4)
    pygame.draw.rect(surface, BLACK, (x - 27, y + 55, 11, 25), border_radius=4)
    pygame.draw.rect(surface, BLACK, (x + 16, y + 55, 11, 25), border_radius=4)

    # Body
    pygame.draw.rect(surface, color, (x - 22, y, 44, 85), border_radius=10)

    # Windows
    pygame.draw.rect(
        surface, (125, 210, 240),
        (x - 16, y + 17, 32, 23), border_radius=5
    )
    pygame.draw.rect(
        surface, (30, 60, 90),
        (x - 15, y + 48, 30, 16), border_radius=4
    )

    # Headlights
    pygame.draw.rect(surface, YELLOW, (x - 18, y + 3, 10, 5))
    pygame.draw.rect(surface, YELLOW, (x + 8, y + 3, 10, 5))


def draw_road(surface, dt):
    global road_offset

    surface.fill(GREEN)
    pygame.draw.rect(surface, GRAY, (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT))

    # Road edges
    pygame.draw.rect(surface, WHITE, (ROAD_LEFT, 0, 6, HEIGHT))
    pygame.draw.rect(surface, WHITE, (ROAD_RIGHT - 6, 0, 6, HEIGHT))

    # Moving lane markers
    road_offset = (road_offset + world_speed * dt) % 100

    for lane_x in LANE_MARKERS:
        for y in range(-100, HEIGHT + 100, 100):
            marker_y = y + int(road_offset)
            pygame.draw.rect(
                surface,
                WHITE,
                (lane_x, marker_y, 6, 50),
                border_radius=3
            )


def draw_button(surface, rect, label, active=False, color=None):
    if active:
        fill = (0, 135, 185)
    elif color is not None:
        fill = color
    else:
        fill = DARK

    pygame.draw.rect(surface, fill, rect, border_radius=12)
    pygame.draw.rect(surface, WHITE, rect, width=2, border_radius=12)
    draw_text(surface, label, font, WHITE, rect.centerx, rect.centery)


def draw_hud(surface):
    pygame.draw.rect(surface, BLACK, (10, 10, 170, 78), border_radius=12)
    draw_text(surface, "SCORE: " + str(score), font, WHITE, 95, 37)
    draw_text(surface, "SPEED: " + str(int(world_speed)), small_font, CYAN, 95, 67)


def draw_controls(surface):
    controls = get_active_controls()
    draw_button(surface, left_button, "<", "left" in controls)
    draw_button(surface, right_button, ">", "right" in controls)
    draw_button(surface, brake_button, "BRAKE", "brake" in controls)
    draw_button(surface, gas_button, "GAS", "gas" in controls)


# ============================================================
# Game logic
# ============================================================

def spawn_enemy():
    lane_x = random.choice(LANES)
    enemy_colors = (
        RED,
        YELLOW,
        (180, 65, 220),
        (255, 130, 35),
    )

    enemies.append({
        "x": lane_x,
        "y": -100.0,
        "speed": random.randint(50, 150),
        "color": random.choice(enemy_colors),
    })


def reset_game():
    global player_x, world_speed, score
    global enemies, spawn_timer, road_offset
    global game_started, game_over

    player_x = float(PLAYER_START_X)
    world_speed = float(BASE_WORLD_SPEED)
    score = 0
    enemies = []
    spawn_timer = 0.0
    road_offset = 0.0

    game_started = True
    game_over = False
    active_pointers.clear()


def player_enemy_collision(enemy):
    player_rect = pygame.Rect(int(player_x) - 19, PLAYER_Y + 5, 38, 75)
    enemy_rect = pygame.Rect(
        int(enemy["x"]) - 19,
        int(enemy["y"]) + 5,
        38,
        75
    )
    return player_rect.colliderect(enemy_rect)


def get_control_at(x, y):
    if left_button.collidepoint(x, y):
        return "left"
    if right_button.collidepoint(x, y):
        return "right"
    if brake_button.collidepoint(x, y):
        return "brake"
    if gas_button.collidepoint(x, y):
        return "gas"
    return None


def get_active_controls():
    return {
        control
        for control in active_pointers.values()
        if control is not None
    }


def pointer_down(pointer_id, x, y):
    """Handle a mouse click or a new touchscreen contact."""
    if not game_started or game_over:
        target = restart_button if game_over else start_button
        if target.collidepoint(x, y):
            reset_game()
        return

    active_pointers[pointer_id] = get_control_at(x, y)


def pointer_move(pointer_id, x, y):
    """Allow a held pointer to slide between on-screen buttons."""
    if pointer_id in active_pointers and game_started and not game_over:
        active_pointers[pointer_id] = get_control_at(x, y)


def pointer_up(pointer_id):
    active_pointers.pop(pointer_id, None)


def handle_events():
    global running

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if not game_started or game_over:
                    reset_game()

        # Mouse input (also supported by many mobile browsers).
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pointer_down("mouse", event.pos[0], event.pos[1])

        elif event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:
                pointer_move("mouse", event.pos[0], event.pos[1])

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            pointer_up("mouse")

        # Native touchscreen input. Pygame finger coordinates are normalized.
        elif event.type == pygame.FINGERDOWN:
            finger_x = int(event.x * WIDTH)
            finger_y = int(event.y * HEIGHT)
            pointer_down(("finger", event.finger_id), finger_x, finger_y)

        elif event.type == pygame.FINGERMOTION:
            finger_x = int(event.x * WIDTH)
            finger_y = int(event.y * HEIGHT)
            pointer_move(("finger", event.finger_id), finger_x, finger_y)

        elif event.type == pygame.FINGERUP:
            pointer_up(("finger", event.finger_id))


def update_game(dt):
    global player_x, world_speed, spawn_timer, score
    global game_over

    if not game_started or game_over:
        return

    # Read keyboard input after processing this frame's events.
    keys = pygame.key.get_pressed()
    move_left = bool(keys[pygame.K_LEFT] or keys[pygame.K_a])
    move_right = bool(keys[pygame.K_RIGHT] or keys[pygame.K_d])
    accelerate = bool(keys[pygame.K_UP] or keys[pygame.K_w])
    brake = bool(keys[pygame.K_DOWN] or keys[pygame.K_s])

    touch_controls = get_active_controls()
    move_left = move_left or ("left" in touch_controls)
    move_right = move_right or ("right" in touch_controls)
    accelerate = accelerate or ("gas" in touch_controls)
    brake = brake or ("brake" in touch_controls)

    # Speed control
    if accelerate:
        world_speed = min(world_speed + 180 * dt, MAX_WORLD_SPEED)
    elif brake:
        world_speed = max(world_speed - 250 * dt, MIN_WORLD_SPEED)
    else:
        world_speed += (BASE_WORLD_SPEED - world_speed) * min(dt * 2, 1)

    # Player movement
    if move_left:
        player_x -= PLAYER_SPEED * dt
    if move_right:
        player_x += PLAYER_SPEED * dt

    player_x = max(ROAD_LEFT + 30, min(ROAD_RIGHT - 30, player_x))

    # Spawn traffic
    spawn_timer += dt
    spawn_delay = max(0.45, 1.2 - score / 1000)

    if spawn_timer >= spawn_delay:
        spawn_enemy()
        spawn_timer = 0.0

    # Move enemies and check collisions
    for enemy in enemies:
        enemy["y"] += (world_speed + enemy["speed"]) * dt

        if player_enemy_collision(enemy):
            game_over = True
            active_pointers.clear()
            break

    # Remove cars that have passed the player and award points
    remaining_enemies = []
    for enemy in enemies:
        if enemy["y"] > HEIGHT + 100:
            score += 10
        else:
            remaining_enemies.append(enemy)

    enemies[:] = remaining_enemies


# ============================================================
# Screens
# ============================================================

def draw_start_screen(surface):
    pygame.draw.rect(surface, BLACK, (35, 235, 410, 285), border_radius=20)
    draw_text(surface, "MINI RACING", title_font, CYAN, WIDTH // 2, 305)
    draw_text(surface, "Dodge the traffic!", font, WHITE, WIDTH // 2, 355)
    draw_button(surface, start_button, "START RACE", color=(20, 105, 155))
    draw_text(surface, "PC: Arrow keys / WASD", small_font, MUTED, WIDTH // 2, 490)
    draw_text(surface, "Mobile: Use the buttons", small_font, MUTED, WIDTH // 2, 515)


def draw_game_over_screen(surface):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 185))
    surface.blit(overlay, (0, 0))

    draw_text(surface, "GAME OVER", big_font, RED, WIDTH // 2, 300)
    draw_text(surface, "FINAL SCORE: " + str(score), font, WHITE, WIDTH // 2, 365)
    draw_button(surface, restart_button, "PLAY AGAIN", color=(25, 105, 185))
    draw_text(surface, "Or press ENTER / SPACE", small_font, YELLOW, WIDTH // 2, 525)


def draw_frame(dt):
    draw_road(screen, dt if game_started and not game_over else 0)

    for enemy in enemies:
        draw_car(screen, enemy["x"], enemy["y"], enemy["color"])

    if game_started:
        draw_car(screen, player_x, PLAYER_Y, BLUE)

    draw_hud(screen)

    if game_started and not game_over:
        draw_controls(screen)

    if not game_started:
        draw_start_screen(screen)
    elif game_over:
        draw_game_over_screen(screen)

    pygame.display.flip()


# ============================================================
# Pygbag-compatible asynchronous main loop
# ============================================================

async def main():
    global running

    while running:
        # Keep delta time stable after a slow frame or tab switch.
        dt = min(clock.tick(FPS) / 1000.0, 0.05)

        handle_events()
        update_game(dt)
        draw_frame(dt)

        # Yield to the browser every frame so WebAssembly can render,
        # process input, and keep the page responsive.
        await asyncio.sleep(0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        pygame.quit()
