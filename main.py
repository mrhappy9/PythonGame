import random
import pygame
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
    SPRITES = load_sprite_sheets(var.MAIN_CHARACTER_FOLDER_NAME, var.NINJA_FROG_HERO, var.DEPTH, var.DEPTH, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height, hp=100):
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
        self.hp_value = hp
        self.collect_fruit = {}
        self.killed_enemies = 0

    def jump(self):
        self.y_velocity = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def show_hp(self):
        font = pygame.font.Font("freesansbold.ttf", 24)
        return font.render("HP: " + str(self.hp_value), True, (255, 255, 255))

    def show_inventory(self):
        font = pygame.font.Font("freesansbold.ttf", 24)
        result = ""
        for fruit in self.collect_fruit:
            result += "{}: {} | ".format(fruit, self.collect_fruit[fruit])

        return font.render(result, True, (255, 255, 255))

    def show_killed_enemy(self):
        font = pygame.font.Font("freesansbold.ttf", 24)
        return font.render("Killed enemies: " + str(self.killed_enemies), True, (255, 255, 255))

    def make_hit(self, name_object):
        self.hit = True
        self.hit_count = 0

        # decreasing hero hp from fire
        if name_object == var.FIRE_OBJECT_NAME:
            self.hp_value -= 1

    def store_fruit(self, collided_object):
        self.hp_value += 20
        if collided_object.fruit_name in self.collect_fruit.keys():
            self.collect_fruit[str(collided_object.fruit_name)] += 1
        else:
            self.collect_fruit[str(collided_object.fruit_name)] = 1

    def enemy_damage(self):
        self.hit = True
        self.hit_count = 0
        self.hp_value -= var.MONSTER_DAMAGE

    def kill_enemy(self):
        self.killed_enemies += 1

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
        self.x_velocity *= var.ACCELERATION_VELOCITY_RATIO
        self.acceleration_count += 1

    def loop(self, fps):
        # define the acceleration by using fall_count and Gravity value
        self.y_velocity += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_velocity, self.y_velocity)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > var.FPS * 2:
            self.hit = False
            self.hit_count = 0
        if self.hp_value == 0:
            self.remove()

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

        if self.hit:
            sprite_sheet = "hit"
        elif self.y_velocity < 0:
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
        window.blit(self.show_hp(), (10, 10))
        window.blit(self.show_inventory(), (10, 30))
        window.blit(self.show_killed_enemy(), (10, 50))


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


# creating fire class inhering from Object
class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, var.FIRE_OBJECT_NAME)
        self.fire = load_sprite_sheets(var.TRAPS_FOLDER_NAME, var.FIRE_FOLDER_NAME, width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "on"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]

        # picking a new index of every animation frames from our sprites dynamically
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


# creating Enemy class inhering from Object
class Enemy(Object):
    def __init__(self, x, y, width, height, enemy_name="monster"):
        super().__init__(x, y, width, height, var.MONSTER_OBJECT_NAME)
        self.enemy = load_sprite_sheets(var.ENEMIES_FOLDER_NAME, var.CYCLOPS_FOLDER_NAME, width, height)
        self.image = self.enemy[enemy_name][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.enemy_name = enemy_name

    def move_up(self, dy):
        self.rect.y -= dy

    def move_left(self, dx):
        self.rect.x += dx

    def move_down(self, dy):
        self.rect.y += dy

    def move_right(self, dx):
        self.rect.x -= dx

    def move(self, ratio, side):
        if side == var.MONSTER_UP:
            self.move_up(ratio)
        elif side == var.MONSTER_LEFT:
            self.move_left(ratio)
        elif side == var.MONSTER_RIGHT:
            self.move_right(ratio)
        elif side == var.MONSTER_DOWN:
            self.move_down(ratio)

    def loop(self, side):
        self.move(var.MONSTER_SPEED, side)
        # picking a new index of every animation frames from our sprites dynamically
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)


# creating Fruit class inhering from Object
class Fruit(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height, fruit_name="Apple"):
        super().__init__(x, y, width, height, var.FRUIT_OBJECT_NAME)
        self.fruit = load_sprite_sheets(var.ITEMS_FOLDER_NAME, var.FRUIT_FOLDER_NAME, width, height)
        self.image = self.fruit[fruit_name][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.fruit_name = fruit_name

    def loop(self):
        sprites = self.fruit[self.fruit_name]

        # picking a new index of every animation frames from our sprites dynamically
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


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


def draw(window, background, bg_image, player, objects_blocks, offset_x):
    # drawing each tile by using its position from list of tuples 'background' including positions
    for tile in background:
        window.blit(bg_image, tile)

    # drawing objects from terrain folder
    for obj in objects_blocks:
        obj.draw(window, offset_x)

    # adding disappearing hero when hp_value <= 0
    if player.hp_value > 0:
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


def handle_move(player, objects_blocks):
    keys = pygame.key.get_pressed()

    player.x_velocity = 0

    collide_left = handle_horizontal_collision(player, objects_blocks, -var.PLAYER_VELOCITY * 2)
    collide_right = handle_horizontal_collision(player, objects_blocks, var.PLAYER_VELOCITY * 2)
    vertical_collide = handle_vertical_collision(player, objects_blocks, player.y_velocity)

    remove_monsters_collide = []

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(var.PLAYER_VELOCITY)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(var.PLAYER_VELOCITY)
    if keys[pygame.K_t] and collide_left and collide_left.name == var.MONSTER_OBJECT_NAME:
        remove_monsters_collide.append(collide_left)
    if keys[pygame.K_t] and collide_right and collide_right.name == var.MONSTER_OBJECT_NAME:
        remove_monsters_collide.append(collide_right)
    if keys[pygame.K_t] and vertical_collide and vertical_collide[-1].name == var.MONSTER_OBJECT_NAME:
        remove_monsters_collide.append(vertical_collide[-1])

    to_check = [collide_left, collide_right, *vertical_collide]

    # killing monster by pressing "T" key, for horizontal and vertical collisions
    if remove_monsters_collide:
        for monster_collide in remove_monsters_collide:
            if monster_collide in objects_blocks:
                objects_blocks.remove(monster_collide)
                player.kill_enemy()

    for obj in to_check:
        if obj and obj.name == var.FIRE_OBJECT_NAME:
            player.make_hit(var.FIRE_OBJECT_NAME)
        if obj and obj.name == var.FRUIT_OBJECT_NAME:
            # collect fruit and remove fruit from map
            player.store_fruit(obj)
            if obj in objects_blocks:
                objects_blocks.remove(obj)
        if obj and obj.name == var.MONSTER_OBJECT_NAME:
            # handle fight with monster
            player.enemy_damage()
            # if obj in objects_blocks:
            #     objects_blocks.remove(obj)
    return objects_blocks


def main(window):
    clock = pygame.time.Clock()
    random_image_id = random.randint(0, len(var.ARRAY_OF_ALL_BG_TILES) - 1)
    background, bg_image = generate_background(var.ARRAY_OF_ALL_BG_TILES[random_image_id])

    player = Player(100, 100, 50, 50)
    fire = Fire(100, var.HEIGHT - var.BLOCK_SIZE - 64, 16, 32)
    enemy = Enemy(200, var.HEIGHT - var.BLOCK_SIZE - 64, 32, 32)

    # creating blocks for vertical collision
    blocks_floor = [Block(i * var.BLOCK_SIZE, var.HEIGHT - var.BLOCK_SIZE, var.BLOCK_SIZE)
                    for i in range(-var.WIDTH // var.BLOCK_SIZE, (var.WIDTH * 2) // var.BLOCK_SIZE)]

    # creating fire blocks on each terrain blocks
    fire_blocks = [Fire(x * var.BLOCK_SIZE, var.HEIGHT - var.BLOCK_SIZE - 64, 16, 36)
                   for x in range(-1000, len(blocks_floor), 5)]

    # creating fruit blocks
    fruit_blocks = [Fruit(x * var.BLOCK_SIZE, var.HEIGHT - var.BLOCK_SIZE - random.randint(100, 600), 32, 32,
                          var.ARRAY_OF_ALL_FRUITS[random.randint(0, len(var.ARRAY_OF_ALL_FRUITS) - 1)])
                    for x in range(-var.WIDTH // var.BLOCK_SIZE, (var.WIDTH * 2) // var.BLOCK_SIZE, 3)]

    # creating enemy blocks
    enemy_blocks = [Enemy(x * var.BLOCK_SIZE, var.HEIGHT - var.BLOCK_SIZE - random.randint(100, 600), 32, 32)
                    for x in range(-var.WIDTH // var.BLOCK_SIZE, (var.WIDTH * 2) // var.BLOCK_SIZE, 7)]

    # creating blocks for horizontal collision
    random_block = [Block(i * var.BLOCK_SIZE, random.randint(200, 400), var.BLOCK_SIZE)
                    for i in range(-var.WIDTH // var.BLOCK_SIZE, (var.WIDTH * 2) // var.BLOCK_SIZE, 4)]
    random_block_second = [Block(i * var.BLOCK_SIZE, random.randint(200, 400), var.BLOCK_SIZE)
                           for i in range(-var.WIDTH // var.BLOCK_SIZE, (var.WIDTH * 2) // var.BLOCK_SIZE, 9)]

    # list with blocks for horizontal and vertical collision
    objects_blocks = [*blocks_floor, *random_block, *random_block_second, fire, *fire_blocks,
                      *fruit_blocks, *enemy_blocks]

    offset_x = 0
    scroll_area_width = 400

    side_going_monster = 0

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

        player.loop(var.FPS)
        for fire in fire_blocks:
            fire.loop()
        for fruit in fruit_blocks:
            fruit.loop()
        for enemy in enemy_blocks:
            enemy.loop(var.ARRAY_OF_MONSTER_GOING[side_going_monster])

        objects_blocks = handle_move(player, objects_blocks)
        draw(window, background, bg_image, player, objects_blocks, offset_x)

        # scrolling backgrounds
        if ((player.rect.right - offset_x >= var.WIDTH - scroll_area_width and player.x_velocity > 0) or
                (player.rect.left - offset_x <= scroll_area_width and player.x_velocity < 0)):
            if player.acceleration_count == 0:
                offset_x += player.x_velocity
            else:
                offset_x += player.x_velocity * var.ACCELERATION_VELOCITY_RATIO

        side_going_monster += 1
        if side_going_monster > 3:
            side_going_monster = 0

    pygame.quit()
    quit()


if __name__ == '__main__':
    main(window)
