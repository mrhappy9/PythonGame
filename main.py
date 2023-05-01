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


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(first_direction, second_direction, width, height, direction=False):
    path = join(var.ASSETS_FOLDER_NAME, first_direction, second_direction)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, var.DEPTH)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):
    path = join(var.ASSETS_FOLDER_NAME, var.TERRAIN, var.TERRAIN_PNG)
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, var.DEPTH)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


# creating the player
class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets(var.MAIN_CHARACTER_FOLDER_NAME, var.MASK_DUDE_HERO, var.DEPTH, var.DEPTH, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_velocity = 0
        self.y_velocity = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.acceleration_count = 0
        self.hit = False
        self.hit_count = 0

    def jump(self):
        self.y_velocity = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
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

    def acceleration(self):
        print(self.x_velocity)
        self.x_velocity *= var.ACCELERATION_VELOCITY_RATIO
        self.acceleration_count += 1

    def loop(self, fps):
        # define the acceleration by using fall_count and Gravity value
        self.y_velocity += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_velocity, self.y_velocity)

        self.fall_count += 1
        self.update_sprite()

    # creating landed method for collided two objects
    def landed(self):
        self.fall_count = 0
        self.y_velocity = 0
        self.jump_count = 0
        self.acceleration_count = 0

    # creating hit_head method for collided two objects
    def hit_head(self):
        self.count = 0
        self.y_velocity *= -1

    # Creating animation
    def update_sprite(self):
        sprite_sheet = "idle"

        if self.y_velocity < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_velocity > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_velocity != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]

        # picking a new index of every animation frames from our sprites dynamically
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    # update the rectangle that bounds our character based on the sprite
    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        # mask is mapping of all of the pixels that exist in the Sprite
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, window, offset_x):
        window.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


# generating objects on the map
class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, window, offset_x):
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y))


# inhering from Object class
class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


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


def draw(window, background, bg_image, player, objects, offset_x):
    # drawing each tile by using its position from list of tuples 'background' including positions
    for tile in background:
        window.blit(bg_image, tile)

    # drawing objects from terrain folder
    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)
    return collided_objects


# horizontal collision
def handle_horizontal_collision(player, objects, dx):
    """
    1) player is trying move on the x direction
    2) after moving here is updating mask
    3) if there is exist collide mask between player and obj -> return player back on dx
    """
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_velocity = 0
    collide_left = handle_horizontal_collision(player, objects, -var.PLAYER_VELOCITY * 2)
    collide_right = handle_horizontal_collision(player, objects, var.PLAYER_VELOCITY * 2 )

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(var.PLAYER_VELOCITY)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(var.PLAYER_VELOCITY)

    handle_vertical_collision(player, objects, player.y_velocity)


def main(window):
    clock = pygame.time.Clock()
    random_image_id = random.randint(0, len(var.ARRAY_OF_ALL_BG_TILES) - 1)
    background, bg_image = generate_background(var.ARRAY_OF_ALL_BG_TILES[random_image_id])

    player = Player(100, 100, 50, 50)

    # creating blocks for vertical collision
    blocks_floor = [Block(i * var.BLOCK_SIZE, var.HEIGHT - var.BLOCK_SIZE, var.BLOCK_SIZE)
                    for i in range(-var.WIDTH // var.BLOCK_SIZE, (var.WIDTH * 2) // var.BLOCK_SIZE)]

    # creating blocks for horizontal collision
    random_block = [Block(i * var.BLOCK_SIZE, random.randint(200, 400), var.BLOCK_SIZE)
                    for i in range(-var.WIDTH // var.BLOCK_SIZE, (var.WIDTH * 2) // var.BLOCK_SIZE, 4)]
    random_block_second = [Block(i * var.BLOCK_SIZE, random.randint(200, 400), var.BLOCK_SIZE)
                    for i in range(-var.WIDTH // var.BLOCK_SIZE, (var.WIDTH * 2) // var.BLOCK_SIZE, 9)]

    # list with blocks for horizontal and vertical collision
    objects_blocks = [*blocks_floor, *random_block, *random_block_second]

    offset_x = 0
    scroll_area_width = 400

    run = True
    while run:
        clock.tick(var.FPS)

        # define to stop program when quit button pressed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            # hero double jumping and acceleration realisation
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 3:
                    player.jump()
                if event.key == pygame.K_a and player.acceleration_count < 2:
                    player.acceleration()
            # if keys[pygame.K_a]:
            #     player.acceleration(var.ACCELERATION_VELOCITY_RATIO)

        player.loop(var.FPS)
        handle_move(player, objects_blocks)
        draw(window, background, bg_image, player, objects_blocks, offset_x)

        # scrolling backgrounds
        if ((player.rect.right - offset_x >= var.WIDTH - scroll_area_width and player.x_velocity > 0) or
                (player.rect.left - offset_x <= scroll_area_width and player.x_velocity < 0)):
            if player.acceleration_count == 0:
                offset_x += player.x_velocity
            else:
                offset_x += player.x_velocity * var.ACCELERATION_VELOCITY_RATIO

    pygame.quit()
    quit()


if __name__ == '__main__':
    main(window)
