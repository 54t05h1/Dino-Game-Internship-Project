"""Dino Game in Python

A game similar to the famous Chrome Dino Game, built using pygame-ce.
Made by intern: @bassemfarid, no one or nothing else. 🤖
"""

import pygame
import random
import math

# Initialize Pygame and create a window
pygame.init()
screen = pygame.display.set_mode((800, 400))
clock = pygame.time.Clock()
running = True  # Pygame main loop, kills pygames when False
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
MIN_EGG_DISTANCE = SCREEN_WIDTH/3
player_score = 0.0
high_score = 0
game_over_score = 0
stamina_current = 1
stamina_recovery_counter = 0
STAMINA_RECOVERY_FRAMES = 12
selected_stamina_recovery_frames = STAMINA_RECOVERY_FRAMES
STAMINA_BAR_X = 20
STAMINA_BAR_Y = 20
STAMINA_BAR_WIDTH = 18
STAMINA_BAR_HEIGHT = 18
STAMINA_BAR_GAP = 4
MENU_PANEL_RECT = pygame.Rect(90, 24, 620, 350)
MENU_OPTION_WIDTH = 112
MENU_OPTION_HEIGHT = 44
MENU_OPTION_GAP = 12
MENU_OPTION_START_X = 220
MENU_ROW_START_Y = 146
MENU_ROW_GAP = 68
MENU_START_BUTTON_RECT = pygame.Rect(280, 316, 240, 40)

# Game state variables
game_state = "intro"  # intro, debuff_menu, playing, game_over
show_stamina_tutorial = False
stamina_tutorial_end_time = 0
has_shown_stamina_tutorial = False
GROUND_Y = 300  # The Y-coordinate of the ground level
JUMP_GRAVITY_START_SPEED = -17  # The speed at which the player jumps
selected_jump_start_speed = JUMP_GRAVITY_START_SPEED
selected_stamina_cap = None
players_gravity_speed = 0  # The current speed at which the player falls

debuff_menu_rows = [
    {
        "key": "stamina_recovery",
        "label": "Stamina\nrecovery",
        "options": [
            {"label": "None", "detail": "12 frames", "value": 12},
            {"label": "+30%", "detail": "16 frames", "value": 16},
            {"label": "+70%", "detail": "20 frames", "value": 20},
            {"label": "+100%", "detail": "24 frames", "value": 24},
        ],
    },
    {
        "key": "jump_power",
        "label": "Jump height",
        "options": [
            {"label": "None", "detail": "Jump -17", "value": -17},
            {"label": "Lower", "detail": "Jump -16", "value": -16},
            {"label": "Lower", "detail": "Jump -14", "value": -14},
        ],
    },
    {
        "key": "stamina_cap",
        "label": "Stamina cap",
        "options": [
            {"label": "None", "detail": "No cap", "value": None},
            {"label": "7 blocks", "detail": "Cap 7", "value": 7},
            {"label": "4 blocks", "detail": "Cap 4", "value": 4},
            {"label": "2 blocks", "detail": "Cap 2", "value": 2},
        ],
    },
]
selected_menu_option_indices = {
    "stamina_recovery": 0,
    "jump_power": 0,
    "stamina_cap": 0,
}

# Load level assets
SKY_SURF = pygame.image.load("graphics/level/sky.png").convert()
GROUND_SURF = pygame.image.load("graphics/level/ground.png").convert()
game_font = pygame.font.Font(pygame.font.get_default_font(), 50)
title_font = pygame.font.Font(pygame.font.get_default_font(), 64)
body_font = pygame.font.Font(pygame.font.get_default_font(), 28)
menu_label_font = pygame.font.Font(pygame.font.get_default_font(), 22)
small_font = pygame.font.Font(pygame.font.get_default_font(), 15)
score_surf = game_font.render(f"SCORE: {player_score}", False, "Black")
score_rect = score_surf.get_rect(center=(400, 50))
score_multiplier_surf = small_font.render("DEBUFF MULTIPLIER: x1.00", False, "Black")
score_multiplier_rect = score_multiplier_surf.get_rect(center=(600, 78))

# Load sprite assets
player_surf = pygame.image.load("graphics/player/player_walk_1.png").convert_alpha()
player_rect = player_surf.get_rect(bottomleft=(25, GROUND_Y))
egg_surf = pygame.image.load("graphics/egg/egg_1.png").convert_alpha()
big_egg_surf = pygame.transform.scale(
    egg_surf,
    (int(egg_surf.get_width() * 1.6), int(egg_surf.get_height() * 1.6)),
)
huge_egg_surf = pygame.transform.scale(
    egg_surf,
    (int(egg_surf.get_width() * 2.5), int(egg_surf.get_height() * 2.5)),)

eggs = []
egg_spawn_counter = 0
egg_rect = egg_surf.get_rect(bottomleft=(800, GROUND_Y))
current_egg_surf = egg_surf
game_start_time = pygame.time.get_ticks()

times_i_jump = 0


def reset_player_position():
    global player_rect, players_gravity_speed

    player_rect.bottomleft = (25, GROUND_Y)
    players_gravity_speed = 0


def start_game():
    global player_score, stamina_current, stamina_recovery_counter, game_start_time
    global game_state, game_over_score, show_stamina_tutorial
    global stamina_tutorial_end_time, has_shown_stamina_tutorial
    global selected_stamina_recovery_frames, selected_jump_start_speed
    global selected_stamina_cap

    player_score = 0.0
    stamina_current = 1
    stamina_recovery_counter = 0
    game_over_score = 0
    apply_selected_debuffs()
    game_state = "playing"
    game_start_time = pygame.time.get_ticks()
    reset_player_position()
    update_score_surface()
    spawn_egg()
    show_stamina_tutorial = not has_shown_stamina_tutorial
    has_shown_stamina_tutorial = True
    stamina_tutorial_end_time = pygame.time.get_ticks() + 10000


def apply_selected_debuffs():
    global selected_stamina_recovery_frames, selected_jump_start_speed, selected_stamina_cap

    selected_stamina_recovery_frames = debuff_menu_rows[0]["options"][
        selected_menu_option_indices["stamina_recovery"]
    ]["value"]
    selected_jump_start_speed = debuff_menu_rows[1]["options"][
        selected_menu_option_indices["jump_power"]
    ]["value"]
    selected_stamina_cap = debuff_menu_rows[2]["options"][
        selected_menu_option_indices["stamina_cap"]
    ]["value"]


def get_final_score_multiplier():
    multiplier = 1.0
    tier_multipliers = {
        1: 1.2,
        2: 1.4,
        3: 1.6,
    }

    for row in debuff_menu_rows:
        selected_index = selected_menu_option_indices[row["key"]]
        multiplier *= tier_multipliers.get(selected_index, 1.0)

    return multiplier


def get_adjusted_final_score(base_score):
    return int(round(base_score * get_final_score_multiplier()))

def draw_text(text,font,x,y,color = "black"):
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=(x, y))
    screen.blit(text_surf, text_rect)


def draw_left_text(text, font, x, y, color="black"):
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(midleft=(x, y))
    screen.blit(text_surf, text_rect)


def draw_left_multiline_text(text, font, x, y, color="black", line_gap=2):
    lines = text.split("\n")
    line_surfs = [font.render(line, True, color) for line in lines]
    total_height = sum(surf.get_height() for surf in line_surfs)
    total_height += line_gap * (len(line_surfs) - 1)
    top = y - total_height // 2

    current_top = top
    for surf in line_surfs:
        rect = surf.get_rect(midleft=(x, current_top + surf.get_height() // 2))
        screen.blit(surf, rect)
        current_top += surf.get_height() + line_gap


def draw_centered_text(text, font, y, color="black"):
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y))
    screen.blit(text_surf, text_rect)


def draw_panel(rect, fill_color=(20, 20, 20, 210), border_color=(255, 255, 255)):
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    panel.fill(fill_color)
    screen.blit(panel, rect.topleft)
    pygame.draw.rect(screen, border_color, rect, 3, border_radius=16)


def spawn_egg():
    # added feature: there is a chance of spawning bigger eggs
    # the probability increases as the game progresses
    global current_egg_surf, egg_rect, eggs

    elapsed_seconds = (pygame.time.get_ticks() - game_start_time) / 1000
    oversized_egg_chance = min(0.1 + elapsed_seconds * 0.003, 0.6)

    seed = random.random()
    if seed < oversized_egg_chance:
        current_egg_surf = big_egg_surf
    elif seed > 1-oversized_egg_chance and get_max_stamina() >= 2:
        current_egg_surf = huge_egg_surf
    else:
        current_egg_surf = egg_surf

    egg_rect = current_egg_surf.get_rect(bottomleft=(800, GROUND_Y))


def update_score_surface():
    '''showing the score'''
    global score_surf, score_rect, score_multiplier_surf, score_multiplier_rect, stamina_current

    score_surf = game_font.render(f"SCORE: {int(player_score)}", False, "Black")
    score_rect = score_surf.get_rect(center=(600, 50))
    score_multiplier_surf = small_font.render(
        f"DEBUFF MULTIPLIER: x{get_final_score_multiplier():.2f}",
        False,
        "Black",
    )
    score_multiplier_rect = score_multiplier_surf.get_rect(center=(600, 78))
    stamina_current = min(stamina_current, get_max_stamina())


def get_max_stamina():
    score_for_stamina = max(int(player_score), 9)
    natural_max = max(1, int((math.log(score_for_stamina, 9)**2)))
    if selected_stamina_cap is None:
        return natural_max
    return max(1, min(natural_max, selected_stamina_cap))


def draw_button_label(rect, title, detail, selected):
    color = "black" if selected else "white"
    title_y = rect.centery - 8
    detail_y = rect.centery + 8
    draw_text(title, small_font, rect.centerx,title_y, color)
    draw_text(detail, small_font, rect.centerx,detail_y, color)


def draw_stamina_bar():
    max_stamina = get_max_stamina()
    stamina_x = STAMINA_BAR_X

    for index in range(max_stamina):
        segment_rect = pygame.Rect(
            stamina_x,
            STAMINA_BAR_Y,
            STAMINA_BAR_WIDTH,
            STAMINA_BAR_HEIGHT,
        )
        fill_color = "#5fd45f" if index < stamina_current else "#3a3a3a"
        pygame.draw.rect(screen, fill_color, segment_rect)
        pygame.draw.rect(screen, "black", segment_rect, 2)
        stamina_x += STAMINA_BAR_WIDTH + STAMINA_BAR_GAP


def recharge_stamina():
    global stamina_current, stamina_recovery_counter

    max_stamina = get_max_stamina()
    stamina_current = min(stamina_current, max_stamina)
    if player_rect.bottom == GROUND_Y:
        if stamina_current < max_stamina:
            stamina_recovery_counter += 1
            if stamina_recovery_counter >= selected_stamina_recovery_frames:
                stamina_current += 1
                stamina_recovery_counter = 0
        else:
            stamina_recovery_counter = 0
    else:
        stamina_recovery_counter = 0


def get_game_speed():
    # new feature: the game speeds up proportional to log the score
    score_for_speed = max(pygame.time.get_ticks() - game_start_time, 1)
    return max(1, int(5 + (4 * math.log(score_for_speed, 100))))


def get_score_step():
    # the score also increases proportional to the game speed, but slower than 1 point per frame
    return get_game_speed() / 10


def is_player_directly_above_egg():
    # detects if the player is directly above the egg
    # - you will know why we need this later
    return player_rect.centerx >= egg_rect.left and player_rect.centerx <= egg_rect.right


def draw_intro_screen():
    screen.blit(SKY_SURF, (0, 0))
    screen.blit(GROUND_SURF, (0, GROUND_Y))

    draw_panel(MENU_PANEL_RECT)

    draw_centered_text("DINO DASH", title_font, 62, "white")
    draw_centered_text("Press Enter or click to configure your debuffs", body_font, 152, "#d7f3ff")
    draw_centered_text("Avoid the eggs and keep yourself alive", small_font, 205, "#e9e9e9")
    draw_centered_text(f"Historical high: {high_score}", body_font, 270, "#ffd86b")
    draw_centered_text("The next screen lets you pick your run penalties", small_font, 315, "#e9e9e9")


def draw_debuff_menu_screen():
    screen.blit(SKY_SURF, (0, 0))
    screen.blit(GROUND_SURF, (0, GROUND_Y))

    draw_panel(MENU_PANEL_RECT)

    draw_centered_text("Choose your debuffs", body_font, 50, "#d7f3ff")
    draw_centered_text("Click an option in each row, then press Start Run", small_font, 74, "#e9e9e9")

    for row_index, row in enumerate(debuff_menu_rows):
        row_y = MENU_ROW_START_Y + row_index * MENU_ROW_GAP
        draw_left_multiline_text(row["label"], small_font, 110, row_y, "white")
        for option_index, option in enumerate(row["options"]):
            option_rect = get_menu_option_rect(row_index, option_index)
            is_selected = selected_menu_option_indices[row["key"]] == option_index
            fill_color = "#ffd86b" if is_selected else "#2a2a2a"
            border_color = "#ffffff" if is_selected else "#7f7f7f"
            pygame.draw.rect(screen, fill_color, option_rect, border_radius=10)
            pygame.draw.rect(screen, border_color, option_rect, 2, border_radius=10)
            draw_button_label(option_rect, option["label"], option["detail"], is_selected)

    pygame.draw.rect(screen, "#1e5f4a", MENU_START_BUTTON_RECT, border_radius=12)
    pygame.draw.rect(screen, "#b9f5d1", MENU_START_BUTTON_RECT, 2, border_radius=12)
    draw_centered_text("START RUN", body_font, MENU_START_BUTTON_RECT.centery, "white")
    draw_centered_text("Esc to go back", small_font, 360, "#e9e9e9")


def draw_game_over_screen():
    screen.blit(SKY_SURF, (0, 0))
    screen.blit(GROUND_SURF, (0, GROUND_Y))
    screen.blit(player_surf, player_rect)
    screen.blit(current_egg_surf, egg_rect)

    overlay_rect = pygame.Rect(100, 55, 600, 290)
    draw_panel(overlay_rect, fill_color=(10, 10, 10, 225), border_color="#ffd86b")

    draw_centered_text("GAME OVER", title_font, 100, "#ffd86b")
    draw_centered_text(f"Your score: {game_over_score}", body_font, 170, "white")
    draw_centered_text(f"Historical high: {high_score}", body_font, 215, "white")
    draw_centered_text("Press SPACE or click to return to the menu", body_font, 270, "#d7f3ff")
    draw_centered_text("Your debuff setup stays selected for the next run", small_font, 315, "#e9e9e9")


def get_menu_option_rect(row_index, option_index):
    x = MENU_OPTION_START_X + option_index * (MENU_OPTION_WIDTH + MENU_OPTION_GAP)
    y = MENU_ROW_START_Y - 16 + row_index * MENU_ROW_GAP
    return pygame.Rect(x, y, MENU_OPTION_WIDTH, MENU_OPTION_HEIGHT)


def handle_menu_click(position):
    for row_index, row in enumerate(debuff_menu_rows):
        for option_index, _ in enumerate(row["options"]):
            if get_menu_option_rect(row_index, option_index).collidepoint(position):
                selected_menu_option_indices[row["key"]] = option_index
                apply_selected_debuffs()
                return

    if MENU_START_BUTTON_RECT.collidepoint(position):
        start_game()


def draw_stamina_tutorial():
    tutorial_rect = pygame.Rect(14, 54, 290, 92)
    draw_panel(tutorial_rect, fill_color=(18, 18, 18, 225), border_color="#8f8f8f")
    pygame.draw.rect(
        screen,
        "#ffd86b",
        pygame.Rect(14, 14, STAMINA_BAR_WIDTH * 3 + STAMINA_BAR_GAP * 2 + 8, 26),
        2,
        border_radius=8,
    )
    draw_text("These boxes are stamina", small_font, 160,78, "white")
    draw_text("Jumping uses one.", small_font, 160,102, "#e9e9e9")
    draw_text("Staying on the ground refills them.", small_font, 160, 124, "#e9e9e9")


while running:
    # Poll for events
    for event in pygame.event.get():
        # pygame.QUIT --> user clicked X to close your window
        if event.type == pygame.QUIT:
            running = False

        elif game_state == "playing":
            # When player wants to jump by pressing SPACE
            if (
                (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)
                or event.type == pygame.MOUSEBUTTONDOWN
            ):
                if stamina_current > 0:
                    players_gravity_speed = selected_jump_start_speed + 2*times_i_jump
                    stamina_current -= 1
                    times_i_jump += 1
        else:
            # Start from the intro or configure debuffs in the setup menu
            if game_state == "intro":
                if (
                    event.type == pygame.KEYDOWN
                    and event.key in (pygame.K_RETURN, pygame.K_SPACE)
                ) or event.type == pygame.MOUSEBUTTONDOWN:
                    game_state = "debuff_menu"
            elif game_state == "debuff_menu":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    handle_menu_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        start_game()
                    elif event.key == pygame.K_ESCAPE:
                        game_state = "intro"
            elif game_state == "game_over":
                if (
                    event.type == pygame.KEYDOWN
                    and event.key in (pygame.K_SPACE, pygame.K_RETURN)
                ) or event.type == pygame.MOUSEBUTTONDOWN:
                    game_state = "intro"

    if game_state == "playing":
        screen.fill("purple")  # Wipe the screen

        # Blit the level assets
        screen.blit(SKY_SURF, (0, 0))
        screen.blit(GROUND_SURF, (0, GROUND_Y))
        pygame.draw.rect(screen, "#c0e8ec", score_rect)
        pygame.draw.rect(screen, "#c0e8ec", score_rect, 10)
        screen.blit(score_surf, score_rect)
        pygame.draw.rect(screen, "#c0e8ec", score_multiplier_rect)
        pygame.draw.rect(screen, "#c0e8ec", score_multiplier_rect, 8)
        screen.blit(score_multiplier_surf, score_multiplier_rect)
        draw_stamina_bar()

        # Adjust egg's horizontal location then blit it
        egg_rect.x -= get_game_speed()
        if egg_rect.right <= 0:
            spawn_egg()
        screen.blit(current_egg_surf, egg_rect)

        # Adjust player's vertical location then blit it
        players_gravity_speed += 1
        player_rect.y += players_gravity_speed
        if player_rect.bottom > GROUND_Y:
            player_rect.bottom = GROUND_Y
            times_i_jump = 0
        screen.blit(player_surf, player_rect)
        recharge_stamina()
        if player_rect.bottom == GROUND_Y or is_player_directly_above_egg():
            player_score += get_score_step()/5
            update_score_surface()
        if show_stamina_tutorial and pygame.time.get_ticks() <= stamina_tutorial_end_time:
            draw_stamina_tutorial()
        else:
            show_stamina_tutorial = False
        # When player collides with enemy, game ends
        if egg_rect.colliderect(player_rect):
            game_over_score = get_adjusted_final_score(player_score)
            high_score = max(high_score, game_over_score)
            game_state = "game_over"

    # When game is over, display game over message
    elif game_state == "game_over":
        draw_game_over_screen()
    elif game_state == "debuff_menu":
        draw_debuff_menu_screen()
    else:
        draw_intro_screen()

    # flip the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # Limits game loop to 60 FPS

pygame.quit()
