import pygame
import random
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, groups, obstacles):
        super().__init__(groups)
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(topleft=(PLAYER_START_X, PLAYER_START_Y))
        
        # Movement
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2()
        self.speed = PLAYER_SPEED
        self.obstacles = obstacles
        
        # Stats
        self.money = 0
        self.xp = 0
        self.trash_inventory = 0
        self.has_seeds = 0
        
    def input(self):
        keys = pygame.key.get_pressed()
        
        # Movement
        if keys[pygame.K_w]:
            self.direction.y = -1
        elif keys[pygame.K_s]:
            self.direction.y = 1
        else:
            self.direction.y = 0
            
        if keys[pygame.K_d]:
            self.direction.x = 1
        elif keys[pygame.K_a]:
            self.direction.x = -1
        else:
            self.direction.x = 0
            
    def move(self, dt):
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        
        self.pos += self.direction * self.speed * dt
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        
        # Bounds check
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT: self.rect.bottom = SCREEN_HEIGHT
        
        # Update pos after bounds check to sync
        self.pos.x = self.rect.x
        self.pos.y = self.rect.y

    def update(self, dt):
        self.input()
        self.move(dt)

class Trash(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.Surface((16, 16))
        self.image.fill(GREY)
        self.rect = self.image.get_rect(topleft=pos)

class Polluter(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacles):
        super().__init__(groups)
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=pos)
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2(random.choice([-1, 1]), random.choice([-1, 1]))
        self.speed = 100
        self.change_dir_timer = 0
        
    def move(self, dt):
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        self.pos += self.direction * self.speed * dt
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        
        # Bounce off walls
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.direction.x *= -1
            self.pos.x = self.rect.x # Reset pos to avoid stuck
        if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            self.direction.y *= -1
            self.pos.y = self.rect.y

    def update(self, dt):
        self.change_dir_timer += dt
        if self.change_dir_timer > 2: # Change direction every 2 seconds
            self.direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
            self.change_dir_timer = 0
        self.move(dt)

class Bin(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.Surface((40, 40))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(topleft=pos)

class Vendor(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.Surface((40, 40))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect(topleft=pos)

class Tree(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.Surface((20, 40))
        self.image.fill(DARK_GREEN)
        self.rect = self.image.get_rect(topleft=pos)
