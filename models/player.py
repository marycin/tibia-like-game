import pygame
import os
from models.weapon import Weapon

ASSET_WEAPON = os.path.join("assets", "rapier.png")
ASSET_PLAYER = os.path.join("assets", "player.png") 

class Player:
    def __init__(self, x, y, size=50, speed=5):
        self.__x = x
        self.__y = y
        self.__size = size
        self.__speed = speed
        self.__facing = "right"
        self.__image_original = pygame.image.load(ASSET_PLAYER).convert_alpha()
        self.__image = pygame.transform.scale(self.__image_original, (self.__size, self.__size))
        self.weapon = self._equip_default_weapon()

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def size(self):
        return self.__size

    @property
    def color(self):
        return self.__color

    def _equip_default_weapon(self):
        return Weapon(name="Rapier", damage=10, range_=1, image_path=ASSET_WEAPON)

    def attack(self):
        self.weapon.attack()

    def update(self):
        self.weapon.update()

    def move(self, keys, boundary_width, boundary_height):
        if keys[pygame.K_LEFT]:
            self.__x -= self.__speed
            self.__facing = "left"
        if keys[pygame.K_RIGHT]:
            self.__x += self.__speed
            self.__facing = "right"
        if keys[pygame.K_UP]:
            self.__y -= self.__speed
        if keys[pygame.K_DOWN]:
            self.__y += self.__speed

        self.__x = max(0, min(boundary_width - self.__size, self.__x))
        self.__y = max(0, min(boundary_height - self.__size, self.__y))

    def draw(self, surface):
        surface.blit(self.__image, (self.__x, self.__y))
        self.weapon.draw(surface, self.__x, self.__y, self.__facing)
