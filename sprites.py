import random
import tkinter as tk
import os
from settings import *

# Cache for loaded images to prevent garbage collection
IMAGE_CACHE = {}

def load_image(canvas, file_name, width, height):
    """
    Attempts to load an image. Returns the image object if successful, else None.
    Uses a cache to store PhotoImage references.
    """
    if file_name in IMAGE_CACHE:
        return IMAGE_CACHE[file_name]
    
    path = os.path.join(os.getcwd(), file_name)
    if os.path.exists(path):
        try:
            # We use tk.PhotoImage. Note: It only supports GIF/PGM/PPM/PNG in newer Tkinter.
            # PNG support requires Tkinter 8.6+ (standard in Python 3.x).
            img = tk.PhotoImage(file=path)
            # Resize is tricky in pure Tkinter without PIL. we rely on sub-sampling or zooming.
            # For simplicity, we just use the image as is or try to scale if needed.
            # But robust resizing requires PIL. We'll simply use the image.
            # If the user provides an image, we assume it's roughly the right size or we let it be.
            IMAGE_CACHE[file_name] = img
            return img
        except Exception as e:
            print(f"Error loading image {file_name}: {e}")
            return None
    return None

class Entity:
    def __init__(self, canvas, x, y, size, color, image_file=None):
        self.canvas = canvas
        self.size = size
        self.x = x
        self.y = y
        self.marked_for_deletion = False
        
        # Try to load image
        self.image = None
        if image_file:
            self.image = load_image(canvas, image_file, size, size)
            
        if self.image:
            self.id = canvas.create_image(x, y, image=self.image, anchor="nw")
        else:
            self.id = canvas.create_rectangle(x, y, x + size, y + size, fill=color, outline="")

    def get_center(self):
        return (self.x + self.size / 2, self.y + self.size / 2)

    def distance_to(self, other):
        cx1, cy1 = self.get_center()
        cx2, cy2 = other.get_center()
        return ((cx1 - cx2)**2 + (cy1 - cy2)**2)**0.5
    
    def check_collision(self, new_x, new_y, walls):
        r_left = new_x
        r_right = new_x + self.size
        r_top = new_y
        r_bottom = new_y + self.size
        
        for wall in walls:
            if wall.check_collision_rect(r_left, r_right, r_top, r_bottom):
                return True
        return False

    def delete(self):
        self.canvas.delete(self.id)
        self.marked_for_deletion = True
        
    def move_visual(self):
        if self.image:
             self.canvas.coords(self.id, self.x, self.y)
        else:
             self.canvas.coords(self.id, self.x, self.y, self.x + self.size, self.y + self.size)

class Wall(Entity):
    def __init__(self, canvas, x, y, w, h):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.size = w # Hack for sort of compatibility
        
        # Wall image logic (tiling or stretching) - simplified to block for now unless wall.png exists
        # If wall.png exists, we might tile it? For now, stick to block to ensure size is correct.
        self.id = canvas.create_rectangle(x, y, x + w, y + h, fill=WALL_COLOR, outline="")

    def check_collision_rect(self, r_left, r_right, r_top, r_bottom):
        w_left = self.x
        w_right = self.x + self.width
        w_top = self.y
        w_bottom = self.y + self.height
        
        if (r_left < w_right and r_right > w_left and
            r_top < w_bottom and r_bottom > w_top):
            return True
        return False

class Player(Entity):
    def __init__(self, canvas):
        super().__init__(canvas, PLAYER_START_X, PLAYER_START_Y, PLAYER_SIZE, GREEN, "player.png")
        self.speed = PLAYER_SPEED
        self.money = 0
        self.trash_inventory = 0
        self.has_seeds = 0
        self.xp = 0
        self.health = PLAYER_MAX_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
    
    def move(self, dx, dy, walls):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed

        # Bounds
        if new_x < 0: new_x = 0
        if new_x > SCREEN_WIDTH - self.size: new_x = SCREEN_WIDTH - self.size
        if new_y < 0: new_y = 0
        if new_y > SCREEN_HEIGHT - self.size: new_y = SCREEN_HEIGHT - self.size

        # Collision X
        if dx != 0:
            collided = False
            r_left = new_x
            r_right = new_x + self.size
            r_top = self.y
            r_bottom = self.y + self.size
            for wall in walls:
                if wall.check_collision_rect(r_left, r_right, r_top, r_bottom):
                    collided = True; break
            if collided: new_x = self.x
            
        # Collision Y
        if dy != 0:
            collided = False
            r_left = new_x
            r_right = new_x + self.size
            r_top = new_y
            r_bottom = new_y + self.size
            for wall in walls:
                if wall.check_collision_rect(r_left, r_right, r_top, r_bottom):
                    collided = True; break
            if collided: new_y = self.y

        if new_x != self.x or new_y != self.y:
            self.x = new_x
            self.y = new_y
            self.move_visual()

class Trash(Entity):
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y, 16, TRASH_GREEN, "trash.png")

class Polluter(Entity):
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y, 30, RED, "enemy.png")
        self.dx = random.choice([-2, 2])
        self.dy = random.choice([-2, 2])
        self.change_dir_timer = 0
        self.attack_cooldown = 0

    def update(self, walls):
        self.change_dir_timer += 1
        if self.change_dir_timer > 60: 
            self.dx = random.choice([-2, 2])
            self.dy = random.choice([-2, 2])
            self.change_dir_timer = 0
            
        new_x = self.x + self.dx
        new_y = self.y + self.dy

        collided = False
        if new_x < 0 or new_x > SCREEN_WIDTH - self.size: collided = True
        if new_y < 0 or new_y > SCREEN_HEIGHT - self.size: collided = True
        
        if not collided:
             for wall in walls:
                 if wall.check_collision_rect(new_x, new_x+self.size, new_y, new_y+self.size):
                     collided = True; break
        
        if collided:
            self.dx *= -1; self.dy *= -1
        else:
            self.x = new_x
            self.y = new_y
            self.move_visual()
            
        if self.attack_cooldown > 0: self.attack_cooldown -= 1

class Bin(Entity):
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y, 40, BLUE, "bin.png")

class Vendor(Entity):
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y, 40, BROWN, "vendor.png")

class Tree(Entity):
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x; self.y = y; self.size = 20
        
        # Special case for Tree size/shape if no image
        image = load_image(canvas, "tree.png", 20, 40)
        self.image = image
        
        if image:
            self.id = canvas.create_image(x, y, image=image, anchor="nw")
        else:
            self.id = canvas.create_rectangle(x, y, x + 20, y + 40, fill=DARK_GREEN, outline="")
        self.marked_for_deletion = False
