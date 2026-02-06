import tkinter as tk
import random
import math
from settings import *
from sprites import Entity, Player, Trash, Polluter, Bin, Vendor, Tree, Wall

class Game:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(TITLE)
        self.root.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, bg=WHITE)
        self.canvas.pack()

        self.setup_game()
        self.setup_ui()
        self.setup_input()
        
        self.game_over = False
        self.update_loop()
        self.root.mainloop()

    def setup_game(self):
        self.player = Player(self.canvas)
        self.bin = Bin(self.canvas, 100, 100)
        self.vendor = Vendor(self.canvas, 900, 100)
        
        self.trash_list = []
        self.polluters = []
        self.trees = []
        self.walls = []
        
        self.create_map()
        for _ in range(5):
            self.spawn_polluter()
            
    def setup_ui(self):
        self.ui_money = self.canvas.create_text(10, 10, anchor="nw", text="", font=("Arial", 14, "bold"))
        self.ui_inv = self.canvas.create_text(10, 35, anchor="nw", text="", font=("Arial", 14, "bold"))
        self.ui_health = self.canvas.create_text(10, 60, anchor="nw", text="", font=("Arial", 14, "bold"), fill="red")
        
        help_text = "WASD: Move | E: Interact (Pickup/Bin) | F: Shop/Plant | Click: Attack"
        self.ui_help = self.canvas.create_text(10, SCREEN_HEIGHT - 30, anchor="nw", text=help_text, font=("Arial", 12))

    def setup_input(self):
        # We bind to <KeyPress> and <KeyRelease> globally to capture WASD regardless of active widget
        self.root.bind_all("<KeyPress>", self.on_key_press)
        self.root.bind_all("<KeyRelease>", self.on_key_release)
        self.canvas.bind("<Button-1>", self.handle_attack)
        
        self.keys = {'w': False, 's': False, 'a': False, 'd': False}

    def on_key_press(self, event):
        # Normalize keysym to lowercase to handle CapsLock
        key = event.keysym.lower()
        if key in self.keys:
            self.keys[key] = True
        elif key == 'f':
            self.handle_f_action()
        elif key == 'e':
            self.handle_e_action()

    def on_key_release(self, event):
        key = event.keysym.lower()
        if key in self.keys:
            self.keys[key] = False

    def create_map(self):
        self.walls.append(Wall(self.canvas, 400, 300, 200, 150))
        self.walls.append(Wall(self.canvas, 700, 50, 150, 200))
        self.walls.append(Wall(self.canvas, 100, 500, 200, 100))

    def spawn_polluter(self):
        for _ in range(10):
            x = random.randint(0, SCREEN_WIDTH - 30)
            y = random.randint(0, SCREEN_HEIGHT - 30)
            valid = True
            for w in self.walls:
                if w.check_collision_rect(x, x+30, y, y+30):
                    valid = False; break
            if valid:
                self.polluters.append(Polluter(self.canvas, x, y))
                break

    def handle_e_action(self):
        if self.game_over: return
        # Pickup
        if self.player.trash_inventory < MAX_INVENTORY:
            closest = None
            min_dist = 50
            for t in self.trash_list:
                dist = self.player.distance_to(t)
                if dist < min_dist:
                    closest = t; min_dist = dist
            
            if closest:
                closest.delete()
                self.trash_list.remove(closest)
                self.player.trash_inventory += 1
                return

        # Deposit
        if self.player.distance_to(self.bin) < 80:
            if self.player.trash_inventory > 0:
                self.player.money += self.player.trash_inventory * TRASH_VALUE
                self.player.xp += self.player.trash_inventory
                self.player.trash_inventory = 0

    def handle_f_action(self):
        if self.game_over: return
        # Vendor
        if self.player.distance_to(self.vendor) < 80:
            if self.player.money >= SEED_COST:
                self.player.money -= SEED_COST
                self.player.has_seeds += 1
                return

        # Plant
        if self.player.has_seeds > 0:
            collides = False
            for w in self.walls:
                 if w.check_collision_rect(self.player.x, self.player.x+20, self.player.y, self.player.y+40):
                     collides = True
            if not collides:
                self.trees.append(Tree(self.canvas, self.player.x, self.player.y))
                self.player.has_seeds -= 1

    def handle_attack(self, event):
        if self.game_over: return
        px, py = self.player.get_center()
        mx, my = event.x, event.y
        slash = self.canvas.create_line(px, py, mx, my, fill="yellow", width=5)
        self.root.after(100, lambda: self.canvas.delete(slash))
        
        limit = 100
        to_remove = []
        for p in self.polluters:
            if self.player.distance_to(p) < limit:
                p.delete()
                to_remove.append(p)
                self.player.xp += 5
        for p in to_remove: self.polluters.remove(p)

    def update_loop(self):
        if self.game_over: return

        # Player Move
        dx, dy = 0, 0
        if self.keys['w']: dy = -1
        if self.keys['s']: dy = 1
        if self.keys['a']: dx = -1
        if self.keys['d']: dx = 1
        
        if dx!=0 and dy!=0: dx*=0.707; dy*=0.707
        self.player.move(dx, dy, self.walls)
        
        # Polluters
        for p in self.polluters:
            p.update(self.walls)
            if random.random() < 0.005 and len(self.trash_list) < 50:
                 tx, ty = p.x, p.y
                 free = True
                 for w in self.walls:
                     if w.check_collision_rect(tx, tx+16, ty, ty+16): free = False
                 if free: self.trash_list.append(Trash(self.canvas, tx, ty))

            # Damage check
            if p.attack_cooldown == 0 and self.player.distance_to(p) < 40:
                self.player.health -= ENEMY_DAMAGE
                p.attack_cooldown = ENEMY_DAMAGE_COOLDOWN
                self.canvas.itemconfig(self.player.id, fill="red" if not self.player.image else "") 
                # Note: if image is used, fill config might not work or just be ignored, 
                # to flash image we would need screen flash or something, but this is fine.
                if not self.player.image:
                    self.root.after(100, lambda: self.canvas.itemconfig(self.player.id, fill=GREEN))
                
                if self.player.health <= 0:
                    self.game_over_screen()
                    return

        # Pop
        if len(self.polluters) < 5 and random.random() < 0.005: self.spawn_polluter()
            
        # UI
        self.canvas.itemconfig(self.ui_money, text=f"Money: ${self.player.money}")
        self.canvas.itemconfig(self.ui_inv, text=f"Bag: {self.player.trash_inventory}/{MAX_INVENTORY} | Seeds: {self.player.has_seeds}")
        self.canvas.itemconfig(self.ui_health, text=f"Health: {self.player.health}/{PLAYER_MAX_HEALTH}")

        self.root.after(16, self.update_loop)

    def game_over_screen(self):
        self.game_over = True
        self.canvas.create_text(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, text="GAME OVER", font=("Arial", 40, "bold"), fill="red")

if __name__ == "__main__":
    Game()
