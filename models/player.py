import pygame
import os
from models.weapon import Weapon

ASSET_PATH = os.path.join("assets", "rapier.png")

class Player:
    def __init__(self, x, y, size=50, speed=5, color=(255, 0, 0)):
        self.__x = x
        self.__y = y
        self.__size = size
        self.__speed = speed
        self.__color = color
        self.weapon = self._equip_default_weapon()  # Dodano przypisanie broni

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
        return Weapon(name="Rapier", damage=10, range_=1, image_path=ASSET_PATH)

    def attack(self):
        self.weapon.attack()

    def update(self):
        self.weapon.update()

    def move(self, keys, boundary_width, boundary_height):
        if keys[pygame.K_LEFT]:
            self.__x -= self.__speed
        if keys[pygame.K_RIGHT]:
            self.__x += self.__speed
        if keys[pygame.K_UP]:
            self.__y -= self.__speed
        if keys[pygame.K_DOWN]:
            self.__y += self.__speed

        self.__x = max(0, min(boundary_width - self.__size, self.__x))
        self.__y = max(0, min(boundary_height - self.__size, self.__y))

    def draw(self, surface):
        pygame.draw.rect(surface, self.__color, (self.__x, self.__y, self.__size, self.__size))
        self.weapon.draw(surface, self.__x - 20, self.__y)
