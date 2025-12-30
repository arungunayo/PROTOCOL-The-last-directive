from settings import *

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)


class Decoration(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)

    @classmethod
    def from_tmx(cls, obj, groups):
        if not obj.image:
            return None

        image = obj.image

        if getattr(obj, "flipped_horizontally", False):
            image = pygame.transform.flip(image, True, False)
        if getattr(obj, "flipped_vertically", False):
            image = pygame.transform.flip(image, False, True)

        if obj.rotation:
            image = pygame.transform.rotate(image, -obj.rotation)

        if obj.width and obj.height:
            image = pygame.transform.scale(
                image,
                (int(obj.width), int(obj.height))
            )

        return cls((obj.x, obj.y), image, groups)
class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, rect, groups):
        super().__init__(groups)
        self.rect = rect
        self.hitbox = self.rect.copy()
