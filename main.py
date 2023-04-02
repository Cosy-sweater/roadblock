import sys
import json
from math import inf

import pygame
from pygame.locals import *

houses = {"house1": [[0, 0], [-1, 0], [1, 0]],
          "house2": [[0, 0], [0, -1], [1, -1], [0, 1]],
          "house3": [[0, 0], [0, -1], [-1, -1], [0, 1]],
          "house4": [[0, 0], [0, 1], [1, 0]]}
cars = {"car1": [("left", "right"), ("right", "left"), ("top", "bottom")],  # T
        "car2": [("top", "bottom"), ("bottom", "top")],  # I
        "car3": [[0, 0, False], [0, -1, True], [1, -1, False], [0, 1, False]],  # Г
        "car4": [[0, 0, False], [0, -1, False], [-1, -1, False], [0, 1, True]],  # Г(обр.)
        "car5": [[0, 0, True], [1, 0, False], [0, 1, False]],  # угол ц.
        "car6": [[0, 0, False], [1, 0, True], [0, 1, False]]}  # угол 2
TILE_SIZE = 150


def show_menu():
    start_level(1)


def start_level(level=1):
    global car_surf
    house_list = []
    car_list = []
    with open(f"levels/level_{level}.json", "r") as f:
        json_data = json.load(f)
    for i in json_data:
        if "house" in i:
            house_list.append(House(json_data[i], houses[i]))
    red_car = pygame.Rect(get_ground_position(*json_data["car"]), [TILE_SIZE] * 2)

    car_surf = CarSurface()
    ocupied_tiles = [json_data["car"]]
    for i in house_list:
        ocupied_tiles.extend(i.board_tiles)

    test = Car(cars["car2"], 1)

    while True:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == QUIT or pygame.mouse.get_pos() >= (1920 - 2, 1080 - 2):
                pygame.quit()
                sys.exit()

        # Update.
        car_surf.update()
        test.update()

        # Draw.
        for tile in grid:
            pygame.draw.rect(screen, (0, 255, 0), tile)
        pygame.draw.rect(screen, (255, 0, 0), red_car)
        [house.draw() for house in house_list]
        car_surf.draw()
        test.draw()

        pygame.display.flip()
        fpsClock.tick(fps)


def get_ground_position(x, y):
    return x * TILE_SIZE + ground.topleft[0], y * TILE_SIZE + ground.topleft[1]


class House:
    def __init__(self, pos, tiles):
        self.pos_x, self.pos_y, self.rotation = pos
        self.tiles = tiles

        if self.rotation == 3:
            self.tiles = [[j, -i] for i, j in self.tiles]
        if self.rotation == 2:
            self.tiles = [[-i, -j] for i, j in self.tiles]
        if self.rotation == 1:
            self.tiles = [[-j, i] for i, j in self.tiles]

        self.board_tiles = [[self.pos_x + i, self.pos_y + j] for i, j in self.tiles]
        self.tiles = [get_ground_position(i, j) for i, j in self.board_tiles]

        self.rects = []
        for tile in self.tiles:
            self.rects.append(pygame.Rect(tile, [TILE_SIZE] * 2))

    def draw(self):
        for rect in self.rects:
            pygame.draw.rect(screen, (0, 0, 255), rect)


class CarSurface:
    def __init__(self):
        self.car_surf_rect = pygame.Rect((0, height - 90), (width, height))
        self.surf = pygame.Surface((self.car_surf_rect.width, self.car_surf_rect.height))
        self.surf.fill((255, 255, 255))

        self.cars_poss = [[200, 100]]

    def update(self):
        if self.car_surf_rect.collidepoint(pygame.mouse.get_pos()):
            if self.car_surf_rect.top > height // 2:
                self.car_surf_rect.top -= 80
            if self.car_surf_rect.top < height // 2:
                self.car_surf_rect.top = height // 2
        else:
            self.car_surf_rect.top += 85
            if self.car_surf_rect.top > height - 90:
                self.car_surf_rect.top = height - 90

    def draw(self):
        screen.blit(self.surf, self.car_surf_rect)

    def get_position_of(self, number):
        res = self.cars_poss[number - 1].copy()
        res[1] += self.car_surf_rect.top
        return res


class Car:
    def __init__(self, data, number):
        self.number, self.data = number, data
        self.is_placed = False
        self.is_picked = False

        self.rects = [pygame.Rect((0, 0), [TILE_SIZE] * 2) for _ in range(len(data))]
        self.main_rect = pygame.Rect(car_surf.get_position_of(self.number), [TILE_SIZE] * 2)

        self.update_rects()

    def update(self):
        if (self.main_rect.collidepoint(pygame.mouse.get_pos()) or any(
                [i.collidepoint(pygame.mouse.get_pos()) for i in self.rects])) and pygame.mouse.get_pressed()[0]:
            self.main_rect.center = pygame.mouse.get_pos()
            self.is_picked = True
        else:
            if not pygame.mouse.get_pressed()[0]:
                self.is_picked = False
            else:
                self.main_rect.center = pygame.mouse.get_pos()
            if self.main_rect.colliderect(ground):
                self.is_placed = True
                self.is_picked = False
                return self.place_closest()
            else:
                self.is_placed = False

        if not self.is_placed and not self.is_picked:
            self.main_rect.x, self.main_rect.y = car_surf.get_position_of(self.number)

        self.update_rects()

    def update_rects(self):
        for index, item in enumerate(self.data):
            self.rects[index].x, self.rects[index].y = self.main_rect.x, self.main_rect.y
            exec(f'self.rects[index].{item[0]}=self.main_rect.{item[1]}')

    def draw(self):
        pygame.draw.rect(screen, (100, 0, 255), self.main_rect)
        for i in self.rects:
            pygame.draw.rect(screen, (50, 120, 255), i)

    def place_closest(self):
        cords = [inf] * 2
        for tile in grid:
            if self.main_rect.colliderect(tile) and (cords[0] ** 2 + cords[1] ** 2) ** 0.5:
                new_distance = (abs(self.main_rect.bottomright[0] - tile.bottomright[0]) ** 2 + abs(self.main_rect.bottomright[1] - tile.bottomright[1]) ** 2) ** 0.5
                old_distance = (cords[0] ** 2 + cords[1] ** 2) ** 0.5
                if new_distance < old_distance:
                    cords = tile.center
        self.main_rect.center = cords
        self.update_rects()
        return


pygame.init()

fps = 60
fpsClock = pygame.time.Clock()

width, height = 1920, 1080
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

grid = []
ground = pygame.Rect((0, 0), (6 * TILE_SIZE, 6 * TILE_SIZE))
ground_pos = list(screen.get_rect().center)
ground_pos[1] -= 50
ground.center = ground_pos
for x in range(6):
    for y in range(6):
        x_pos, y_pos = get_ground_position(x, y)
        grid.append(pygame.Rect((x_pos + 2, y_pos + 2), [TILE_SIZE - 4] * 2))

if __name__ == "__main__":
    show_menu()
