import sys
import os
import pygame
import json
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.network_client import NetworkClient
from server.action import Action
from server.action_type import ActionType
from models.player import Player

ASSET_BACKGROUND = os.path.join("assets", "background.jpg")
ASSET_WEAPON = os.path.join("assets", "rapier.png")

class Game:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.__width = width
        self.__height = height

        self.__screen = pygame.display.set_mode((self.__width, self.__height))
        pygame.display.set_caption("Multiplayer Tibia-like Game")

        self.__background_original = pygame.image.load(ASSET_BACKGROUND).convert()
        self.__background = pygame.transform.scale(self.__background_original, (self.__width, self.__height))

        init_x = random.randint(50, self.__width - 100)
        init_y = random.randint(50, self.__height - 100)
        self.__player = Player(init_x, init_y)

        self._enemy_sprite = pygame.transform.scale(
            pygame.image.load(os.path.join("assets", "player.png")).convert_alpha(),
            (50, 50)
        )
        self._weapon_image = pygame.image.load(ASSET_WEAPON).convert_alpha()

        self._font = pygame.font.SysFont("Arial", 16)
        self.__clock = pygame.time.Clock()
        self.__running = True

        self._is_alive = True
        self._attack_range = 50

        self.__other_players = {}  # player_id -> {"pos": (x, y), "attack_timer": int, "facing": str, "alive": bool}
        self.__my_id = None

        self.__network = NetworkClient(
            "ws://localhost:8765",
            self.__on_action_received,
            self.__on_system_message
        )

        if not self.__network.wait_until_connected():
            print("Nie udało się połączyć z serwerem.")
            sys.exit(1)

    def __on_action_received(self, data):
        if data.get("type") == "PLAYER_DEAD":
            dead_id = data["player_id"]
            if dead_id in self.__other_players:
                self.__other_players[dead_id]["alive"] = False
            return

        action = Action.from_dict(data)
        if action.player_id == self.__my_id:
            return

        if action.player_id not in self.__other_players:
            self.__other_players[action.player_id] = {
                "pos": action.field,
                "attack_timer": 0,
                "facing": "right",
                "alive": True
            }

        if not self.__other_players[action.player_id]["alive"]:
            self.__other_players[action.player_id]["alive"] = True

        if action.type == ActionType.MOVE:
            old_pos = self.__other_players[action.player_id]["pos"]
            new_x = action.field[0]
            old_x = old_pos[0]
            facing = self.__other_players[action.player_id]["facing"]
            if new_x < old_x:
                facing = "left"
            elif new_x > old_x:
                facing = "right"

            self.__other_players[action.player_id]["pos"] = action.field
            self.__other_players[action.player_id]["facing"] = facing

        elif action.type == ActionType.ATTACK:
            self.__other_players[action.player_id]["attack_timer"] = 15

            attacker_x, attacker_y = action.field

            for pid, pdata in self.__other_players.items():
                if pid == action.player_id:
                    continue
                px, py = pdata["pos"]
                dx = abs(px - attacker_x)
                dy = abs(py - attacker_y)
                if dx + dy < self._attack_range and pdata["alive"]:
                    pdata["alive"] = False

            if self._is_alive:
                dx = abs(attacker_x - self.__player.x)
                dy = abs(attacker_y - self.__player.y)
                if dx + dy < self._attack_range:
                    print(f"Zostałeś trafiony przez gracza {action.player_id}")
                    self._is_alive = False

                    death_msg = {
                        "type": "PLAYER_DEAD",
                        "player_id": self.__my_id
                    }
                    self.__network.send_raw(death_msg)

    def __on_system_message(self, msg):
        print(f"SYSTEM MSG: {msg}")
        if msg.startswith("JOIN:"):
            new_id = int(msg.split(":")[1])
            if self.__my_id is None:
                self.__my_id = new_id
                print(f"My player_id = {self.__my_id}")
            else:
                spawn_x = random.randint(50, self.__width - 100)
                spawn_y = random.randint(50, self.__height - 100)
                self.__other_players[new_id] = {
                    "pos": (spawn_x, spawn_y),
                    "attack_timer": 0,
                    "facing": "right",
                    "alive": True
                }
        elif msg.startswith("LEAVE:"):
            left_id = int(msg.split(":")[1])
            if left_id in self.__other_players:
                del self.__other_players[left_id]

    def __handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__running = False

            elif event.type == pygame.KEYDOWN and self._is_alive:
                if event.key == pygame.K_SPACE:
                    self.__player.attack()
                    action = Action(
                        type=ActionType.ATTACK,
                        field=(self.__player.x, self.__player.y)
                    )
                    self.__network.send_action(action)

            elif event.type == pygame.MOUSEBUTTONDOWN and not self._is_alive:
                x, y = pygame.mouse.get_pos()
                if (self.__width//2 - 100) <= x <= (self.__width//2 + 100) and (self.__height//2) <= y <= (self.__height//2 + 50):
                    print("Gracz respawnuje się")
                    self._is_alive = True
                    respawn_x = random.randint(50, self.__width - 100)
                    respawn_y = random.randint(50, self.__height - 100)
                    self.__player.respawn(respawn_x, respawn_y)

    def __update(self):
        if self._is_alive:
            keys = pygame.key.get_pressed()
            self.__player.move(keys, self.__width, self.__height)
            self.__player.update()

            action = Action(
                type=ActionType.MOVE,
                field=(self.__player.x, self.__player.y)
            )
            self.__network.send_action(action)

        for data in self.__other_players.values():
            if data["attack_timer"] > 0:
                data["attack_timer"] -= 1

    def __draw(self):
        self.__screen.blit(self.__background, (0, 0))

        if self._is_alive:
            self.__player.draw(self.__screen)

        for player_id, data in self.__other_players.items():
            pos = data["pos"]
            facing = data.get("facing", "right")
            alive = data.get("alive", True)
            angle = 30 if data["attack_timer"] > 0 else 0
            flip = (facing == "right")
            offset_x = 60 if facing == "right" else -10

            self.__screen.blit(self._enemy_sprite, pos)

            nick_color = (255, 255, 255) if alive else (255, 0, 0)
            nick_text = f"Player {player_id}" if alive else f"Player {player_id} (dead)"
            label = self._font.render(nick_text, True, nick_color)
            label_rect = label.get_rect(center=(pos[0] + 25, pos[1] - 10))
            self.__screen.blit(label, label_rect)

            image = pygame.transform.rotate(self._weapon_image, angle)
            image = pygame.transform.flip(image, flip, False)
            sword_pos = (pos[0] + offset_x, pos[1] + 25)
            rect = image.get_rect(center=sword_pos)
            self.__screen.blit(image, rect)

        if not self._is_alive:
            overlay = pygame.Surface((self.__width, self.__height))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.__screen.blit(overlay, (0, 0))

            font_big = pygame.font.SysFont("Arial", 40)
            text = font_big.render("Zginąłeś!", True, (255, 0, 0))
            self.__screen.blit(text, (self.__width // 2 - 100, self.__height // 2 - 60))

            pygame.draw.rect(self.__screen, (0, 200, 0), (self.__width//2 - 100, self.__height//2, 200, 50))
            font_small = pygame.font.SysFont("Arial", 24)
            btn_text = font_small.render("Dołącz ponownie", True, (255, 255, 255))
            self.__screen.blit(btn_text, (self.__width//2 - 80, self.__height//2 + 10))

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
