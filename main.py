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
stamina_current = 1
stamina_recovery_counter = 0
STAMINA_RECOVERY_FRAMES = 12
STAMINA_BAR_X = 20
STAMINA_BAR_Y = 20
STAMINA_BAR_WIDTH = 18
STAMINA_BAR_HEIGHT = 18
STAMINA_BAR_GAP = 4

# Game state variables
is_playing = True  # Whether in game or in menu
GROUND_Y = 300  # The Y-coordinate of the ground level
JUMP_GRAVITY_START_SPEED = -17  # The speed at which the player jumps
players_gravity_speed = 0  # The current speed at which the player falls

# Load level assets
SKY_SURF = pygame.image.load("graphics/level/sky.png").convert()
GROUND_SURF = pygame.image.load("graphics/level/ground.png").convert()
game_font = pygame.font.Font(pygame.font.get_default_font(), 50)
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


def spawn_egg():
    # added feature: there is a chance of spawning bigger eggs
    # the probability increases as the game progresses
    global current_egg_surf, egg_rect, eggs

    elapsed_seconds = (pygame.time.get_ticks() - game_start_time) / 1000
    oversized_egg_chance = min(0.1 + elapsed_seconds * 0.003, 0.55)
    ultrasized_egg_chance = min(0.02 + elapsed_seconds * 0.002, 0.15)

    egg_sprite = big_egg_surf
    seed = random.random()
    if seed < oversized_egg_chance:
        current_egg_surf = big_egg_surf
    elif seed > 1-oversized_egg_chance:
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


while running:
    # Poll for events
    for event in pygame.event.get():
        # pygame.QUIT --> user clicked X to close your window
        if event.type == pygame.QUIT:
            running = False

        elif is_playing:
            # When player wants to jump by pressing SPACE
            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_SPACE
                or event.type == pygame.MOUSEBUTTONDOWN
            ):
                if stamina_current > 0:
                    players_gravity_speed = JUMP_GRAVITY_START_SPEED
                    stamina_current -= 1
        else:
            # When player wants to play again by pressing SPACE
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player_score = 0.0
                update_score_surface()
                is_playing = True
                game_start_time = pygame.time.get_ticks()
                stamina_current = 1
                stamina_recovery_counter = 0
                spawn_egg()

    if is_playing:
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
            is_playing = False

    # When game is over, display game over message
    else:
        screen.fill("black")

    # flip the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # Limits game loop to 60 FPS

pygame.quit()
