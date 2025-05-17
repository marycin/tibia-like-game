import pygame

class Weapon:
    def __init__(self, name: str, damage: int, range_: int, image_path: str):
        self.name = name
        self.damage = damage
        self.range = range_
        self.image_original = pygame.image.load(image_path).convert_alpha()
        self.image = self.image_original
        self.angle = 0
        self.attacking = False
        self.attack_timer = 0

    def attack(self):
        self.attacking = True
        self.angle = 30  # Przechylenie o 30 stopni
        self.attack_timer = 20  # Liczba klatek, przez które atak trwa

    def update(self):
        if self.attacking:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.attacking = False
                self.angle = 0

        # Obróć grafikę na podstawie aktualnego kąta
        self.image = pygame.transform.rotate(self.image_original, self.angle)

    def draw(self, surface, x, y):
        if self.image:
            rect = self.image.get_rect(center=(x + 25, y + 25))  # dopasuj do gracza
            surface.blit(self.image, rect)
