import sys
import json

import level_solver

import pygame
from pygame.locals import *

pygame.init()

fps = 60
fpsClock = pygame.time.Clock()

width, height = 1920, 1080
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # , pygame.FULLSCREEN)

houses = {"house1": [[0, 0], [-1, 0], [1, 0]],
          "house2": [[0, 0], [0, -1], [1, -1], [0, 1]],
          "house3": [[0, 0], [0, -1], [-1, -1], [0, 1]],
          "house4": [[0, 0], [0, 1], [1, 0]]}
cars = {"car1": [("left", "right"), ("right", "left"), ("top", "bottom")],  # T
        "car2": [("left", "right"), ("right", "left")],  # I
        "car3": [("top", "bottom"), ("bottom", "top"), ("bottomleft", "topright")],  # Г
        "car4": [("top", "bottom"), ("bottom", "top"), ("topleft", "bottomright")],  # Г(обр.)
        "car5": [("top", "bottom"), ("right", "left")],  # угол ц.
        "car6": [("bottom", "top"), ("left", "right")]}  # угол 2
car_places = [2, -1, 1, 1, -1, 0]
next_sides_c = ["left", "top", "right", "bottom"]
next_sides_e = ["topleft", "topright", "bottomright", "bottomleft"]
screen_w, screen_h = pygame.display.get_surface().get_size()
TILE_SIZE = 150 * (screen_w / width)


def rotate(data, step=1):
    res = []
    for i in data:
        i = list(i)
        if i[0] in next_sides_c:
            temp = [(next_sides_c.index(j) + step) % 4 for j in i]
            temp = next_sides_c[temp[0]], next_sides_c[temp[1]]
        else:
            temp = [(next_sides_e.index(j) + step) % 4 for j in i]
            temp = next_sides_e[temp[0]], next_sides_e[temp[1]]
        res.append(temp)

    return res


def show_menu():
    start_level(1)


def start_level(level=1):
    def check_solved():
        global popup
        if len(curent_tiles) != 36 and False:
            popup = Popup()
            return

        maze_walls = ocupied_tiles.copy()[1:]
        for car in car_list:
            maze_walls.append(car.get_car_position())

        maze = [[None for j in range(6)] for i in range(6)]
        for row in range(6):
            for column in range(6):
                if [row, column] in maze_walls:
                    maze[column][row] = "w"
                else:
                    maze[column][row] = "c"
        a = ocupied_tiles[0]
        maze[a[1]][a[0]] = "r"

        result = level_solver.run(maze)
        if not result[0]:
            sys.exit("Победа")

    global car_surf, car_list
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

    for num, key in enumerate(cars):
        car_list.append(Car(cars[f'car{num + 1}'], num + 1, car_places[num]))

    submit_button = Btn(command=check_solved, position=(1600, screen_h / 2 - 90), size=(100, 100))
    exit_button = Btn(command=sys.exit, position=(1820, 0), size=(100, 100), color=(255, 0, 0))

    while True:
        curent_tiles = ocupied_tiles.copy()
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEWHEEL:
                [car.rotate(event.y * -1) for car in car_list]  # * settings["rotation_direction"]

        # Update.
        car_surf.update()
        for car in car_list:
            car_tiles = car.update()
            if car_tiles is None:
                return car
            flag = False
            for i in car_tiles:
                if i in curent_tiles and car.is_placed:
                    car.is_placed = False
                    car.move_to_board()
                    flag = True
            if not flag:
                curent_tiles.extend(car_tiles)

        submit_button.update()
        exit_button.update()

        # Draw.
        #  bottom level
        for tile in grid:
            pygame.draw.rect(screen, (0, 255, 0), tile)
        pygame.draw.rect(screen, (255, 0, 0), red_car)
        [house.draw() for house in house_list]

        #  mid level
        [car.draw() for car in car_list]
        submit_button.draw()
        car_surf.draw()

        # top level
        last = None
        for car in car_list:  # отрисовка машин на верхнем слое только если они не размещены
            if not car.is_placed:
                car.draw()
            if car.is_picked:
                last = car
        last.draw() if last else None

        if "popup" in globals():
            popup.update()

        exit_button.draw()

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
        self.car_surf_rect = pygame.Rect((0, screen_h - 90), (screen_w, screen_h))
        self.surf = pygame.Surface((self.car_surf_rect.width, self.car_surf_rect.height))
        self.surf.fill((255, 255, 255))

        self.cars_poss = [[200, 100], [200, 500], [600, 320], [1000, 260], [1600, 100], [1400, 500]]
        self.cars_poss = [[i[0] * (screen_w / width), i[1] * (screen_h / height)] for i in self.cars_poss]
        self.move_limit = screen_h // 3
        self.bottom_border = 90 * (screen_h / height)

        self.is_expended = False

    def update(self):
        if self.car_surf_rect.collidepoint(pygame.mouse.get_pos()):
            if self.car_surf_rect.top > self.move_limit:
                self.car_surf_rect.top -= 80
            if self.car_surf_rect.top < self.move_limit:
                self.car_surf_rect.top = self.move_limit
            self.is_expended = True
        else:
            self.is_expended = False
            self.car_surf_rect.top += 85
            if self.car_surf_rect.top > screen_h - self.bottom_border:
                self.car_surf_rect.top = screen_h - self.bottom_border

    def draw(self):
        screen.blit(self.surf, self.car_surf_rect)

    def get_position_of(self, number):
        res = self.cars_poss[number - 1].copy()
        res[1] += self.car_surf_rect.top
        return res


class Car:
    def __init__(self, data, number, car_pos):
        self.number, self.data, self.car_pos = number, data, car_pos
        self.is_placed = False
        self.is_picked = False
        self.is_on_whiteboard = True

        self.rects = [pygame.Rect((0, 0), [TILE_SIZE] * 2) for _ in range(len(data))]
        self.main_rect = pygame.Rect(car_surf.get_position_of(self.number), [TILE_SIZE] * 2)

        self.update_rects()

    def update(self):
        if (self.main_rect.collidepoint(pygame.mouse.get_pos()) or any(
                i.collidepoint(pygame.mouse.get_pos()) for i in self.rects)) and pygame.mouse.get_pressed()[0]:
            if self.is_placed and car_surf.car_surf_rect.collidepoint(pygame.mouse.get_pos()):
                return []
            if not any(map(lambda n: n.is_picked, car_list)):
                self.is_picked = True
                self.is_placed = False
                self.is_on_whiteboard = False
        else:
            if (not pygame.mouse.get_pressed()[0]) and (not self.is_on_whiteboard):
                self.is_picked = False
                self.is_placed = True
                if self.main_rect.colliderect(ground) and car_surf.is_expended and not self.is_placed:
                    self.is_on_whiteboard = True
                else:
                    self.is_on_whiteboard = False

        if self.is_picked:
            self.main_rect.center = pygame.mouse.get_pos()

        if self.is_placed:
            self.place_closest()
            self.update_rects()
            for i in car_list:
                if i.is_placed and i.number != self.number:
                    for j in self.get_all_rects():
                        if (any(j.colliderect(k) for k in i.get_all_rects())) and self.number != i.number:
                            self.move_to_board()

        if self.is_on_whiteboard:
            self.move_to_board()

        self.update_rects()

        res = []  # add main_rect
        if not self.is_placed:
            return res
        for rect in self.rects + [self.main_rect]:
            for tile in grid:
                if rect.colliderect(tile):
                    res.append(grid.index(tile))
        res = list(map(lambda n: [n // 6, n % 6], res))
        return res

    def update_rects(self):
        for index, item in enumerate(self.data):
            self.rects[index].x, self.rects[index].y = self.main_rect.x, self.main_rect.y
            exec(f'self.rects[index].{item[0]}=self.main_rect.{item[1]}')

    def move_to_board(self):
        self.is_on_whiteboard = True
        self.is_placed = False
        # self.main_rect.x, self.main_rect.y = car_surf.get_position_of(self.number) если сломаются анимации
        if self.main_rect.y <= screen_h + 100 and not car_surf.is_expended:
            self.main_rect.y += 85
        else:
            self.main_rect.x, self.main_rect.y = car_surf.get_position_of(self.number)
            self.reset_rotation()

        self.update_rects()

    def draw(self):
        if self.car_pos == -1:
            pygame.draw.rect(screen, (30, 30, 120), self.main_rect)
        else:
            pygame.draw.rect(screen, (50, 120, 255), self.main_rect)
        for index, item in enumerate(self.rects):
            if index == self.car_pos and self.car_pos != -1:
                pygame.draw.rect(screen, (30, 30, 120), item)
            else:
                pygame.draw.rect(screen, (50, 120, 255), item)

    def place_closest(self):
        for tile in grid:
            if tile.collidepoint(self.main_rect.center):
                self.main_rect.center = tile.center
                self.check_boundary()
                return
        self.is_placed = False
        self.is_on_whiteboard = True

    def rotate(self, step):
        if self.is_picked:
            self.data = rotate(self.data, step)

        self.update_rects()

    def reset_rotation(self):
        self.data = cars[f'car{self.number}']

    def check_boundary(self):
        for rect in self.rects:
            if not rect.colliderect(ground):
                self.is_placed, self.is_on_whiteboard = False, True

    def get_all_rects(self):
        return self.rects + [self.main_rect]

    def get_car_position(self):
        a = -1
        car = self.rects[self.car_pos] if self.car_pos != -1 else self.main_rect
        for tile in grid:
            if car.colliderect(tile):
                a = grid.index(tile)
        res = [a // 6, a % 6]
        return res


class Btn:
    def __init__(self, position=(0, 0), size=(50, 50), **kwargs):
        self.rect = pygame.Rect(position, size)
        self.kwargs = kwargs
        self.rect_color = self.kwargs.get("color")
        if not self.rect_color:
            self.rect_color = (100, 255, 0)

    def update(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            if self.kwargs.get("command"):
                self.kwargs["command"]()

    def draw(self):
        pygame.draw.rect(screen, self.rect_color, self.rect)


class Popup:
    def __init__(self, title="title", text="text", **kwargs):
        self.title, self.text = title, text
        self.kwargs = kwargs

        self.is_shown = True
        self.not_expanded = True
        self.curent_frame = 0

        # self.temp = pygame.Rect()

    def update(self):
        if self.not_expanded:
            self.curent_frame += 1

        if not self.is_shown:
            del self


if __name__ == "__main__":
    grid = []
    ground = pygame.Rect((0, 0), (6 * TILE_SIZE, 6 * TILE_SIZE))
    ground_pos = list(screen.get_rect().center)
    ground_pos[1] -= 50
    ground.center = ground_pos
    for x in range(6):
        for y in range(6):
            x_pos, y_pos = get_ground_position(x, y)
            grid.append(pygame.Rect((x_pos, y_pos), [TILE_SIZE] * 2))

    show_menu()
