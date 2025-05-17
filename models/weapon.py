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
        self.facing = "right"

    def attack(self):
        self.attacking = True
        self.angle = 30  # Przechylenie o 30 stopni
        self.attack_timer = 15  # Liczba klatek, przez które atak trwa

    def update(self):
        if self.attacking:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.attacking = False
                self.angle = 0

        # Obróć grafikę na podstawie aktualnego kąta
        self.image = pygame.transform.rotate(self.image_original, self.angle)

    def draw(self, surface, player_x, player_y, facing="right"):
        self.facing = facing  # zapamiętaj kierunek

        # Zmień pozycję miecza
        offset_x = 60 if facing == "right" else -10
        pos = (player_x + offset_x, player_y + 25)

        # Flipnij miecz, jeśli gracz patrzy w lewo
        image_to_draw = pygame.transform.flip(self.image, True, False) if facing == "right" else self.image

        # Oblicz środek obróconego obrazu
        rect = image_to_draw.get_rect(center=pos)
        surface.blit(image_to_draw, rect)
