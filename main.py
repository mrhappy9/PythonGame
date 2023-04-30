import os
import random
import math
import pygame
import numpy as np
import variables as var
from os import listdir
from os.path import isfile, join

pygame.init()

pygame.display.set_caption("PyGame")
window = pygame.display.set_mode((var.WIDTH, var.HEIGHT))


# creating the player
class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.x_velocity = 0
        self.y_velocity = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, velocity):
        self.x_velocity = -velocity
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, velocity):
        self.x_velocity = velocity
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        # define the acceleration by using fall_count and Gravity value
        self.y_velocity += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_velocity, self.y_velocity)

        self.fall_count += 1

    def draw(self, window):
        pygame.draw.rect(window, self.COLOR, self.rect)


# generating the background
def generate_background(name):
    image = pygame.image.load(join(var.ASSETS_FOLDER_NAME, var.BACKGROUND_FOLDER_NAME, name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(var.WIDTH // width + 1):
        for j in range(var.HEIGHT // height + 1):
            # drawing background starts from top left corner, so here we should to know the position of each tile
            position = (i * width, j * height)
            tiles.append(position)

    return tiles, image


def draw(window, background, bg_image, player):
    # drawing each tile by using its position from list of tuples 'background' including positions
    for tile in background:
        window.blit(bg_image, tile)

    player.draw(window)

    pygame.display.update()


def handle_move(player):
    keys = pygame.key.get_pressed()

    player.x_velocity = 0
    player.y_velocity = 0

    if keys[pygame.K_LEFT]:
        player.move_left(var.PLAYER_VELOCITY)
    if keys[pygame.K_RIGHT]:
        player.move_right(var.PLAYER_VELOCITY)


def main(window):
    clock = pygame.time.Clock()
    random_image_id = random.randint(0, len(var.ARRAY_OF_ALL_BG_TILES)-1)
    background, bg_image = generate_background(var.ARRAY_OF_ALL_BG_TILES[random_image_id])

    player = Player(100, 100, 50, 50)

    run = True
    while run:
        clock.tick(var.FPS)

        # define to stop program when quit button pressed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        player.loop(var.FPS)
        handle_move(player)
        draw(window, background, bg_image, player)
    pygame.quit()
    quit()


if __name__ == '__main__':
    main(window)