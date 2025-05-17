import pygame
import sys
import os
from models.player import Player

ASSET_BACKGROUND = os.path.join("assets", "background.jpg")

class Game:
    def __init__(self, width=800, height=600):
        self.__width = width
        self.__height = height

        self.__screen = pygame.display.set_mode((self.__width, self.__height))
        pygame.display.set_caption("tibia-like-game")

        # Poprawione ładowanie i skalowanie tła
        self.__background_original = pygame.image.load(ASSET_BACKGROUND).convert()
        self.__background = pygame.transform.scale(self.__background_original, (self.__width, self.__height))


        init_x = self.__width // 2
        init_y = self.__height // 2
        self.__player = Player(init_x, init_y)

        self.__clock = pygame.time.Clock()
        self.__running = True

    def run(self):
        while self.__running:
            self.__clock.tick(60)
            self.__handle_events()
            self.__update()
            self.__draw()
        
        pygame.quit()
        sys.exit()

    def __handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.__player.attack()  # Dodano atak

    def __update(self):
        keys = pygame.key.get_pressed()
        self.__player.move(keys, self.__width, self.__height)
        self.__player.update()  # Dodano aktualizację broni

    def __draw(self):
        # Poprawione rysowanie tła
        self.__screen.blit(self.__background, (0, 0))
        self.__player.draw(self.__screen)
        pygame.display.update()