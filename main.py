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
running = True  # Pygame main loop, kills pygame when False
player_score = 0.0

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
egg_rect = egg_surf.get_rect(bottomleft=(800, GROUND_Y))
current_egg_surf = egg_surf
game_start_time = pygame.time.get_ticks()
on_double_jump = 0


def spawn_egg():
    # added feature: there is a chance of spawning bigger eggs
    # the probability increases as the game progresses
    global current_egg_surf, egg_rect

    elapsed_seconds = (pygame.time.get_ticks() - game_start_time) / 1000
    oversized_egg_chance = 0 if player_score > 1000 else min(0.1 + elapsed_seconds * 0.005, 0.65)

    if random.random() < oversized_egg_chance:
        current_egg_surf = big_egg_surf
    else:
        current_egg_surf = egg_surf

    egg_rect = current_egg_surf.get_rect(bottomleft=(800, GROUND_Y))


def update_score_surface():
    '''showing the score'''
    global score_surf, score_rect

    score_surf = game_font.render(f"SCORE: {int(player_score)}", False, "Black")
    score_rect = score_surf.get_rect(center=(400, 50))


def get_game_speed():
    # new feature: the game speeds up proportional to log the score
    score_for_speed = max(player_score, 1)
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
                if(not on_double_jump):
                    players_gravity_speed = JUMP_GRAVITY_START_SPEED
                    on_double_jump = 1
                elif(on_double_jump == 1):
                    players_gravity_speed = JUMP_GRAVITY_START_SPEED*1.11
                    on_double_jump = 2
        else:
            # When player wants to play again by pressing SPACE
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player_score = 0.0
                update_score_surface()
                is_playing = True
                game_start_time = pygame.time.get_ticks()
                spawn_egg()

    if is_playing:
        screen.fill("purple")  # Wipe the screen

        # Blit the level assets
        screen.blit(SKY_SURF, (0, 0))
        screen.blit(GROUND_SURF, (0, GROUND_Y))
        pygame.draw.rect(screen, "#c0e8ec", score_rect)
        pygame.draw.rect(screen, "#c0e8ec", score_rect, 10)
        screen.blit(score_surf, score_rect)

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
        if player_rect.bottom == GROUND_Y:
            on_double_jump = 0
            player_score += get_score_step()
            update_score_surface()
        elif not is_player_directly_above_egg():
            player_score = max(0, player_score - get_score_step())
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
