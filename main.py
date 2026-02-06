import pygame
import sys
import random
from settings import *
from sprites import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20)
        
        # Sprite Groups
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.trash_group = pygame.sprite.Group()
        self.polluters = pygame.sprite.Group()
        self.interactables = pygame.sprite.Group() 
        self.trees = pygame.sprite.Group()
        
        self.setup()

    def setup(self):
        # Create Player
        self.player = Player([self.all_sprites], self.obstacles)
        
        # Create Bin
        self.bin = Bin((100, 100), [self.all_sprites, self.obstacles, self.interactables])
        
        # Create Vendor
        self.vendor = Vendor((900, 100), [self.all_sprites, self.obstacles, self.interactables])
        
        # Create Initial Polluters
        for _ in range(3):
            pos = (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
            Polluter(pos, [self.all_sprites, self.polluters], self.obstacles)

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.events()
            self.update(dt)
            self.draw()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    self.handle_interaction()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left Click
                    self.handle_attack()

    def handle_interaction(self):
        # 1. Try to pickup trash
        # Check collision with trash (using a slightly larger rect for reach)
        # Simple distance check is often better
        closest_trash = None
        min_dist = 50 # Interaction range
        
        for trash in self.trash_group:
            dist = pygame.math.Vector2(self.player.rect.center).distance_to(trash.rect.center)
            if dist < min_dist:
                closest_trash = trash
                min_dist = dist
        
        if closest_trash:
            closest_trash.kill()
            self.player.trash_inventory += 1
            return # Action taken

        # 2. Try to interact with Bin
        dist_to_bin = pygame.math.Vector2(self.player.rect.center).distance_to(self.bin.rect.center)
        if dist_to_bin < 60:
            if self.player.trash_inventory > 0:
                reward = self.player.trash_inventory * TRASH_VALUE
                self.player.money += reward
                self.player.xp += self.player.trash_inventory # 1 XP per trash
                self.player.trash_inventory = 0
            return

        # 3. Try to interact with Vendor
        dist_to_vendor = pygame.math.Vector2(self.player.rect.center).distance_to(self.vendor.rect.center)
        if dist_to_vendor < 60:
            if self.player.money >= SEED_COST:
                self.player.money -= SEED_COST
                self.player.has_seeds += 1
            return

        # 4. Try to plant tree
        if self.player.has_seeds > 0:
            # Check if space is empty (simplified check)
            pos = self.player.rect.center
            Tree(pos, [self.all_sprites, self.trees, self.obstacles])
            self.player.has_seeds -= 1

    def handle_attack(self):
        # Attack logic - remove polluters in range
        attack_range = 60
        for polluter in self.polluters:
            dist = pygame.math.Vector2(self.player.rect.center).distance_to(polluter.rect.center)
            if dist < attack_range:
                polluter.kill()
                self.player.xp += 5 # XP reward for stopping polluter

    def update(self, dt):
        self.all_sprites.update(dt)
        
        # Polluters spawn trash randomly
        for polluter in self.polluters:
            if random.random() < 0.01: # 1% chance per frame per polluter (approx once every 1.5s at 60fps)
                if len(self.trash_group) < 50: # Limit max trash
                    Trash(polluter.rect.topleft, [self.all_sprites, self.trash_group])

        # Spawn new polluters if all gone (optional, keep game going)
        if len(self.polluters) == 0:
             if random.random() < 0.005:
                 pos = (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
                 Polluter(pos, [self.all_sprites, self.polluters], self.obstacles)

    def draw(self):
        self.screen.fill(WHITE)
        self.all_sprites.draw(self.screen)
        self.draw_ui()
        pygame.display.flip()

    def draw_ui(self):
        # Simple HUD
        ui_texts = [
            f"Money: ${self.player.money}",
            f"XP: {self.player.xp}",
            f"Trash: {self.player.trash_inventory}",
            f"Seeds: {self.player.has_seeds}",
            "WASD: Move | F: Interact/Plant | Click: Attack"
        ]
        
        for i, text in enumerate(ui_texts):
            surface = self.font.render(text, True, BLACK)
            self.screen.blit(surface, (10, 10 + i * 25))

if __name__ == '__main__':
    game = Game()
    game.run()
