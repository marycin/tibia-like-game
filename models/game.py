import sys
import os
import pygame

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.network_client import NetworkClient
from server.action import Action
from server.action_type import ActionType
from models.player import Player

ASSET_BACKGROUND = os.path.join("assets", "background.jpg")
ASSET_PLAYER = os.path.join("assets", "player.png") 

class Game:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.__width = width
        self.__height = height

        self.__screen = pygame.display.set_mode((self.__width, self.__height))
        pygame.display.set_caption("Multiplayer Tibia-like Game")

        self.__background_original = pygame.image.load(ASSET_BACKGROUND).convert()
        self.__background = pygame.transform.scale(self.__background_original, (self.__width, self.__height))

        init_x = self.__width // 2
        init_y = self.__height // 2
        self.__player = Player(init_x, init_y)

        self.__clock = pygame.time.Clock()
        self.__running = True

        self.__other_players = {}  # player_id -> (x, y)
        self.__my_id = None

        self._enemy_sprite = pygame.transform.scale(
            pygame.image.load(os.path.join("assets", "player.png")).convert_alpha(),
            (50, 50)
        )
        self._font = pygame.font.SysFont("Arial", 16)

        self.__network = NetworkClient(
            "ws://localhost:8765",
            self.__on_action_received,
            self.__on_system_message
        )

        if not self.__network.wait_until_connected():
            print("Połączenie z serwerem nie powiodło się.")
            sys.exit(1)

    def __on_action_received(self, data):
        action = Action.from_dict(data)
        if action.player_id == self.__my_id:
            return  # Ignoruj swoje wiadomości
        self.__other_players[action.player_id] = action.field

    def __on_system_message(self, msg):
        print(f"SYSTEM MSG: {msg}")
        if msg.startswith("JOIN:"):
            new_id = int(msg.split(":")[1])
            if self.__my_id is None:
                self.__my_id = new_id
                print(f"My player_id = {self.__my_id}")
        elif msg.startswith("LEAVE:"):
            left_id = int(msg.split(":")[1])
            if left_id in self.__other_players:
                del self.__other_players[left_id]

    def __handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__running = False

    def __update(self):
        keys = pygame.key.get_pressed()
        self.__player.move(keys, self.__width, self.__height)
        self.__player.update()

        action = Action(
            type=ActionType.MOVE,
            field=(self.__player.x, self.__player.y)
        )
        self.__network.send_action(action)

    def __draw(self):
        self.__screen.blit(self.__background, (0, 0))
        self.__player.draw(self.__screen)

        for player_id, pos in self.__other_players.items():
            # Rysuj sprite
            self.__screen.blit(self._enemy_sprite, (pos[0], pos[1]))
            label = self._font.render(f"Player {player_id}", True, (255, 255, 255))
            label_rect = label.get_rect(center=(pos[0] + 25, pos[1] - 10))
            self.__screen.blit(label, label_rect)

        pygame.display.update()

    def run(self):
        while self.__running:
            self.__clock.tick(60)
            self.__handle_events()
            self.__update()
            self.__draw()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
