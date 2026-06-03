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
STAMINA_BAR_X = 20
STAMINA_BAR_Y = 20
STAMINA_BAR_WIDTH = 18
STAMINA_BAR_HEIGHT = 18
STAMINA_BAR_GAP = 4

# Game state variables
game_state = "intro1"  # intro, playing, game_over
GROUND_Y = 300  # The Y-coordinate of the ground level
JUMP_GRAVITY_START_SPEED = -17  # The speed at which the player jumps
players_gravity_speed = 0  # The current speed at which the player falls

# Load level assets
SKY_SURF = pygame.image.load("graphics/level/sky.png").convert()
GROUND_SURF = pygame.image.load("graphics/level/ground.png").convert()
game_font = pygame.font.Font(pygame.font.get_default_font(), 50)
title_font = pygame.font.Font(pygame.font.get_default_font(), 64)
body_font = pygame.font.Font(pygame.font.get_default_font(), 28)
small_font = pygame.font.Font(pygame.font.get_default_font(), 20)
score_surf = game_font.render(f"SCORE: {player_score}", False, "Black")
score_rect = score_surf.get_rect(center=(400, 50))

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


def reset_player_position():
    global player_rect, players_gravity_speed

    player_rect.bottomleft = (25, GROUND_Y)
    players_gravity_speed = 0


def start_game():
    global player_score, stamina_current, stamina_recovery_counter, game_start_time
    global game_state, game_over_score

    player_score = 0.0
    stamina_current = 1
    stamina_recovery_counter = 0
    game_over_score = 0
    game_state = "playing"
    game_start_time = pygame.time.get_ticks()
    reset_player_position()
    update_score_surface()
    spawn_egg()


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
    global score_surf, score_rect, stamina_current

    score_surf = game_font.render(f"SCORE: {int(player_score)}", False, "Black")
    score_rect = score_surf.get_rect(center=(400, 50))
    stamina_current = min(stamina_current, get_max_stamina())


def get_max_stamina():
    score_for_stamina = max(int(player_score), 9)
    return max(1, int((math.log(score_for_stamina, 9)**2)))


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
            if stamina_recovery_counter >= STAMINA_RECOVERY_FRAMES:
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

    panel_rect = pygame.Rect(120, 42, 560, 300)
    draw_panel(panel_rect)

    draw_centered_text("DINO DASH", title_font, 90, "white")
    draw_centered_text("How to Play", body_font, 140, "#d7f3ff")
    draw_centered_text("SPACE or click to start", body_font, 185, "white")
    draw_centered_text("SPACE or click while playing to jump", small_font, 230, "#e9e9e9")
    draw_centered_text("Avoid the eggs and keep yourself alive", small_font, 260, "#e9e9e9")
    draw_centered_text(f"Historical high: {high_score}", body_font, 300, "#ffd86b")


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
    draw_centered_text("Press SPACE or click to play again", body_font, 270, "#d7f3ff")
    draw_centered_text("The next run starts immediately from a clean slate", small_font, 315, "#e9e9e9")


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
                    players_gravity_speed = JUMP_GRAVITY_START_SPEED
                    stamina_current -= 1
        else:
            # Start or restart from the menu screens
            if (
                event.type == pygame.KEYDOWN
                and event.key in (pygame.K_SPACE, pygame.K_RETURN)
            ) or event.type == pygame.MOUSEBUTTONDOWN:
                start_game()

    if game_state == "playing":
        screen.fill("purple")  # Wipe the screen

        # Blit the level assets
        screen.blit(SKY_SURF, (0, 0))
        screen.blit(GROUND_SURF, (0, GROUND_Y))
        pygame.draw.rect(screen, "#c0e8ec", score_rect)
        pygame.draw.rect(screen, "#c0e8ec", score_rect, 10)
        screen.blit(score_surf, score_rect)
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
        screen.blit(player_surf, player_rect)
        recharge_stamina()
        if player_rect.bottom == GROUND_Y or is_player_directly_above_egg():
            player_score += get_score_step()/5
            update_score_surface()
        # When player collides with enemy, game ends
        if egg_rect.colliderect(player_rect):
            game_over_score = int(player_score)
            high_score = max(high_score, game_over_score)
            game_state = "game_over"

    # When game is over, display game over message
    elif game_state == "game_over":
        draw_game_over_screen()
    else:
        draw_intro_screen()

    # flip the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # Limits game loop to 60 FPS

pygame.quit()
