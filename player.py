import pygame
from os import walk
from os.path import join

GRAVITY = 2500
JUMP_FORCE = -700
MOVE_SPEED = 500
ANIMATION_SPEED = 30
SCALE = 3


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)

        self.collision_sprites = collision_sprites
        self.flash_timer = 0

        # animations
        self.animations = self.load_animations()
        self.state = "idle"
        self.facing = "right"
        self.frame_index = 0

        self.image = self.animations["idle-right"][0]
        self.rect = self.image.get_rect(topleft=pos)

        # hitbox
        self.hitbox = self.rect.copy()
        self.hitbox.top +=60
        self.hitbox.width = int(self.rect.width * 0.4)
        self.prev_hitbox = self.hitbox.copy()

        # movement
        self.direction = pygame.Vector2()
        self.velocity_y = 0
        self.on_ground = False

    # ------------------ ASSET LOADING ------------------

    def load_animations(self):
        animations = {}
        base_path = join("", "assets", "images", "player")

        for state in ["idle", "left", "right"]:
            for direction in ["l", "r"]:
                key = f"{state}-{'left' if direction == 'l' else 'right'}"
                path = join(base_path, f"{state}-{direction}")
                frames = []

                for _, _, files in walk(path):
                    for file in sorted(files, key=lambda x: int(x.split(".")[0])):
                        image = pygame.image.load(join(path, file)).convert_alpha()
                        image = pygame.transform.scale_by(image, SCALE)
                        frames.append(image)

                animations[key] = frames

        return animations

    # ------------------ INPUT ------------------

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = 0

        if keys[pygame.K_a]:
            self.direction.x = -1
            self.facing = "left"
        elif keys[pygame.K_d]:
            self.direction.x = 1
            self.facing = "right"
        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE]:
            self.velocity_y = JUMP_FORCE
            self.on_ground = False

    # ------------------ MOVEMENT ------------------

    def apply_gravity(self, dt):
        self.velocity_y += GRAVITY * dt
        self.hitbox.y += self.velocity_y * dt

    def move_horizontal(self, dt):
        self.hitbox.x += self.direction.x * MOVE_SPEED * dt

    def collisions(self, direction):
        for sprite in self.collision_sprites:
            if not sprite.hitbox.colliderect(self.hitbox):
                continue

            # ---------- HORIZONTAL ----------
            if direction == "horizontal":
                if self.hitbox.right > sprite.hitbox.left and self.prev_hitbox.right <= sprite.hitbox.left:
                    self.hitbox.right = sprite.hitbox.left

                elif self.hitbox.left < sprite.hitbox.right and self.prev_hitbox.left >= sprite.hitbox.right:
                    self.hitbox.left = sprite.hitbox.right

            # ---------- VERTICAL ----------
            else:
                # landing on top
                if self.hitbox.bottom > sprite.hitbox.top and self.prev_hitbox.bottom <= sprite.hitbox.top:
                    self.hitbox.bottom = sprite.hitbox.top
                    self.velocity_y = 0
                    self.on_ground = True

                # hitting head
                elif self.hitbox.top < sprite.hitbox.bottom and self.prev_hitbox.top >= sprite.hitbox.bottom:
                    self.hitbox.top = sprite.hitbox.bottom
                    self.velocity_y = 0

    # ------------------ ANIMATION ------------------
    def load_animations(self):
        animations = {}
        base = join("", "assets", "images", "player")

        animations["idle-left"] = self.load_folder(join(base, "idle-l"))
        animations["idle-right"] = self.load_folder(join(base, "idle-r"))
        animations["left"] = self.load_folder(join(base, "left"))
        animations["right"] = self.load_folder(join(base, "right"))

        return animations

    def load_folder(self, path):
        frames = []
        for _, _, files in walk(path):
            for file in sorted(files):
                img = pygame.image.load(join(path, file)).convert_alpha()
                img = pygame.transform.scale_by(img, SCALE)
                frames.append(img)
        return frames

    def animate(self, dt):
        if self.direction.x < 0:
            key = "left"
        elif self.direction.x > 0:
            key = "right"
        else:
            key = f"idle-{self.facing}"

        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index >= len(self.animations[key]):
            self.frame_index = 0

        self.image = self.animations[key][int(self.frame_index)]
        self.rect.center = self.hitbox.center
        if self.flash_timer > 0:
            img = self.image.copy()
            img.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
            self.image = img

    # ------------------ flash ------------------
    def flash(self, duration=250):
        self.flash_timer = duration

    # ------------------ UPDATE ------------------

    def update(self, dt):
        self.prev_hitbox = self.hitbox.copy()

        self.input()

        self.move_horizontal(dt)
        self.collisions("horizontal")
        self.flash_timer = max(0, self.flash_timer - dt * 1000)
        self.apply_gravity(dt)
        self.collisions("vertical")

        self.animate(dt)
