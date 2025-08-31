from fps import blit_fps

import pygame
import sys
import time
import os

pygame.init()

screen = pygame.display.set_mode((900, 450), pygame.RESIZABLE)
screen_width, screen_height = pygame.display.get_surface().get_size()
pygame.display.set_caption("Mansion Escape")
hitboxes = False
font = pygame.font.Font(None, 20)
clock = pygame.time.Clock()

gravity = 9.8 * 100  # 100px = 1meter
borders = []


def resource_path(relative_path):
    """Функция для получения абсолютного пути к файлам (учитывает как режим разработки, так и работу через PyInstaller)"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))  # Проверка, что мы не в PyInstaller
    return os.path.join(base_path, relative_path)


coin_image = pygame.image.load(resource_path('images/coin.png'))

player_states = {
    'static': pygame.image.load(resource_path('images/coin.png')),
}


def limit(min_value, inp_value, max_value):
    return max(min_value, min(inp_value, max_value))


def start():
    global borders
    borders = [
        {
            'position': [100, 290, 150, 10],
            'condition': 'static',
            'color': 'grey'
        }, {
            'position': [300, 190, 150, 10],
            'condition': 'static',
            'color': 'grey'
        }, {
            'position': [650, 400, 50, 50],
            'condition': 'static',
            'color': 'grey'
        }, {
            'position': [300 + (150 - 20) / 2, 130, 15, 20],
            'condition': 'coin',
            'color': 'yellow',
            'image': coin_image
        }, {
            'position': [300 + (150 - 20) / 2, 445, 20, 5],
            'condition': 'kill',
            'color': 'red'
        }, {
            'position': [320, 160, 20, 20],
            'condition': 'teleport',
            'color': 'violet'
        }, {
            'position': [900 - 5, 450 - 35, 5, 20],
            'condition': 'cloner',
            'color': 'orange',
            'pressed': False,
            'index': 0
        }, {
            'position': [50, 445, 20, 5],
            'condition': 'button',
            'color': 'blue',
            'pressed': False,
            'index': 1,
        }, {
            'position': [50 + 50 + 20, 445, 20, 5],
            'condition': 'button',
            'color': 'blue',
            'pressed': False,
            'index': 2,
        }]
    Player.instances = []
    Player(bounce=0, k_friction=0.7, x=screen_width / 2)


class Player:
    instances = []

    def __init__(self, player_width=20, player_height=40, delta_shift=10, mass=1, bounce=0.7, velocity_y=0, velocity_x=0,
                 k_friction=0.1, x=screen_width / 2, y=screen_height / 2, speed=10, jump_height=500):
        self.player_width = player_width
        self.normal_player_height = player_height
        self.player_height = player_height
        self.delta_shift = delta_shift
        self.mass = mass
        self.bounce = bounce * -1
        self.velocity_y = velocity_y
        self.velocity_x = velocity_x
        self.k_friction = k_friction
        self.x = x
        self.y = y
        self.friction = k_friction * mass * gravity
        self.speed = speed
        self.jump_height = jump_height
        self.player_state = player_states['static']

        self.shift_pressed = False
        self.is_on_border = False

        Player.instances.append(self)

    def apply_friction(self, param):
        if param == 'x':
            if self.velocity_x > 0:
                self.velocity_x = max(0.0, self.velocity_x - self.friction * dt * self.mass)
            elif self.velocity_x < 0:
                self.velocity_x = min(0.0, self.velocity_x + self.friction * dt * self.mass)
        elif param == 'y':
            if self.velocity_y > 0:
                self.velocity_y = max(0.0, self.velocity_y - self.friction * dt * self.mass)
            elif self.velocity_y < 0:
                self.velocity_y = min(0.0, self.velocity_y + self.friction * dt * self.mass)

    def gravity_to_bottom(self):
        self.velocity_y += gravity * dt * self.mass
        self.y += self.velocity_y * dt
        self.x += self.velocity_x * dt

    def pushing_from_borders(self):
        if self.y + self.player_height >= screen_height:
            self.y = screen_height - self.player_height
            self.velocity_y *= self.bounce
        if self.y <= 0:
            self.y = 0
            self.velocity_y *= self.bounce
        if self.x + self.player_width >= screen_width:
            self.x = screen_width - self.player_width
            self.velocity_x *= self.bounce
        if self.x <= 0:
            self.x = 0
            self.velocity_x *= self.bounce

    def draw_player(self):
        player_rect = pygame.Rect([self.x * scale_width, self.y * scale_height, self.player_width * scale_width, self.player_height * scale_height])
        screen.blit(pygame.transform.scale(self.player_state, player_rect[2:]), player_rect[:2])

    def control(self):
        if keys[pygame.K_SPACE] and (self.is_on_floor() or self.is_on_border):
            self.velocity_y -= self.jump_height
        if keys[pygame.K_LSHIFT]:
            self.player_height = self.normal_player_height - self.delta_shift
            if not self.shift_pressed:
                self.y += self.delta_shift
            self.shift_pressed = True
        else:
            if self.shift_pressed:
                self.y -= self.delta_shift
            self.player_height = self.normal_player_height
            self.shift_pressed = False
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velocity_x -= self.speed
        else:
            self.apply_friction('x')
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velocity_x += self.speed
        else:
            self.apply_friction('x')

    def is_on_floor(self):
        if self.y + self.player_height >= screen_height:
            return True
        return False


start()

while True:
    keys = pygame.key.get_pressed()
    scale_width, scale_height = pygame.display.get_surface().get_size()[0] / 900, pygame.display.get_surface().get_size()[1] / 450
    screen.fill('black')
    dt = min(clock.tick(120) / 1000, 0.03)

    for player in Player.instances:
        if hitboxes:
            pygame.draw.rect(screen, 'red', [player.x - 1, player.y + 3, 1, player.player_height - 6])
            pygame.draw.rect(screen, 'red', [player.x + player.player_width, player.y + 3, 1, player.player_height - 6])
            pygame.draw.rect(screen, 'red', [player.x + 3, player.y - 1, player.player_width - 6, 1])
            pygame.draw.rect(screen, 'red', [player.x + 3, player.y + player.player_height, player.player_width - 6, 1])

            pygame.draw.rect(screen, 'grey', [0, 0, screen_width, screen_height], 1)

        player_left_rect = pygame.Rect([player.x - 1, player.y + 3, 1, player.player_height - 6])
        player_right_rect = pygame.Rect([player.x + player.player_width, player.y + 3, 1, player.player_height - 6])
        player_top_rect = pygame.Rect([player.x + 3, player.y - 1, player.player_width - 6, 1])
        player_bottom_rect = pygame.Rect([player.x + 3, player.y + player.player_height, player.player_width - 6, 1])

        player.is_on_border = False
        collision_sides = {
            "top": (player_top_rect, lambda b: setattr(player, 'y', b[1] + b[3] + 2)),
            "bottom": (player_bottom_rect, lambda b: (setattr(player, 'y', b[1] - player.player_height), setattr(player, 'is_on_border', True))),
            "left": (player_left_rect, lambda b: setattr(player, 'x', b[0] + b[2])),
            "right": (player_right_rect, lambda b: setattr(player, 'x', b[0] - player.player_width))
        }

        border_index = 0
        for border in borders:
            rect = border['position']
            border_type = border.get('condition', 'static')
            border_color = border.get('color', 'green')
            border_image = border.get('image', False)
            if hitboxes:
                pygame.draw.rect(screen, border_color, rect, 1)
            border_rect = pygame.Rect(rect)

            scaled_rect = [border['position'][i] * (scale_width if i % 2 == 0 else scale_height) for i in range(len(border['position']))]
            if not border_image:
                pygame.draw.rect(screen, border_color, scaled_rect)
            else:
                screen.blit(pygame.transform.scale(border_image, scaled_rect[2:]), scaled_rect[:2])

            for side, (player_rect, resolve_position) in collision_sides.items():
                if border_rect.colliderect(player_rect):
                    if border_type == 'coin':
                        borders.pop(border_index)
                        pass

                    if border_type == 'kill':
                        start()
                        continue

                    if border_type == 'cloner' and not border['pressed']:
                        Player(bounce=0, k_friction=0.7, x=screen_width / 6 * 5)
                        borders[border_index]['pressed'] = True
                        if border['index'] == 0:
                            borders[border_index]['position'] = [900 - 2, 450 - 35, 2, 20]
                        continue

                    if border_type == 'teleport':
                        player.x = screen_width / 6 * 5
                        continue

                    if (border.get('index', 'none') == 2 or border.get('index', 'none') == 1) and side in ['top', 'bottom'] and not border['pressed']:
                        borders[border_index]['position'][1] += 5 - 2
                        borders[border_index]['position'][3] = 2
                        borders[border_index]['pressed'] = True

                    if side in ['top', 'bottom']:
                        player.velocity_y = 0
                    else:
                        if border_type == 'movable':
                            push_speed = 120  # пикселей в секунду
                            if (player.velocity_x == 0 or (side == 'right' and player.velocity_x / abs(player.velocity_x) == -1) or
                                    (side == 'left' and player.velocity_x / abs(player.velocity_x) == 1)):
                                direction = 0
                                player.velocity_x *= 2
                            elif side == 'right':
                                direction = 1
                            else:
                                direction = -1
                            border['position'][0] += direction * push_speed * dt
                            border['position'][0] = limit(player.player_width, border['position'][0], screen_width - player.player_width - border['position'][2])
                            player.velocity_x *= 0.5
                        else:
                            if (player.velocity_x == 0 or (side == 'right' and player.velocity_x / abs(player.velocity_x) == 1) or
                                    (side == 'left' and player.velocity_x / abs(player.velocity_x) == -1)):
                                player.velocity_x = 0
                    resolve_position(rect)

            border_index += 1

        player.velocity_x = limit(-300, player.velocity_x, 300)
        player.control()
        player.gravity_to_bottom()
        player.pushing_from_borders()

    pressed_borders = 0
    for i in borders:
        if i.get('index', 'none') in [1, 2] and i['pressed']:
            pressed_borders += 1
    if pressed_borders == 2:
        borders[2]['condition'] = 'movable'
    else:
        for i in range(len(borders)):
            if borders[i].get('index', 'none') in [1, 2]:
                borders[i]['position'][1] = 445
                borders[i]['position'][3] = 5
                borders[i]['pressed'] = False

    for player in Player.instances:
        player.draw_player()

    blit_fps(screen, font)

    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            sys.exit()
        if keys[pygame.K_x]:
            if hitboxes:
                hitboxes = False
            else:
                hitboxes = True
            time.sleep(0.1)
