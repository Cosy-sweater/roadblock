# buttons default sizes: 150x150, 450x150, 450x450, 150x70, 50x50
import sys
import json
from pathlib import Path
import warnings

import level_solver

import pygame
from pygame.locals import *

if __name__ != "__main__":
    sys.exit()

pygame.init()
pygame.font.init()

fps = 60
fpsClock = pygame.time.Clock()

width, height = 1920, 1080
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # , pygame.FULLSCREEN)

font1 = pygame.font.SysFont('Comic Sans MS', int(30 * screen.get_width() / width))
font2 = pygame.font.SysFont('Comic Sans MS', int(24 * screen.get_width() / width))

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
screen_w, screen_h = screen.get_size()
TILE_SIZE = 150 * round(screen_h / height, 1)


def close_app():
    pygame.quit()
    sys.exit()


def update_popups(clicked=False):
    [i.update(clicked=clicked) for i in popups]


def draw_popups():
    [i.draw() for i in popups]


def get_proportion(w: float = 1, h: float = 1, square: str = None):
    if not square:
        return w * round(screen_w / width, 1), h * round(screen_h / height, 1)
    else:
        if square.lower() == "h":
            return h * round(screen_h / height, 1), h * round(screen_h / height, 1)
        elif square.lower() == "w":
            return w * round(screen_w / width, 1), w * round(screen_w / width, 1)
        else:
            raise ValueError("Argument takes 'w' and 'h' values only")

def get_tutorial_step(n: int):
    tutorial_popups = [
        MiniPopup(title="123", subtext="312")
    ]
    popups.append(tutorial_popups[n - 1])


default_surf = pygame.Surface(get_proportion(w=1500, h=800))
default_surf.fill((44, 44, 44))
mini_surf = pygame.Surface(get_proportion(w=450, h=200))
mini_surf.fill((44, 44, 44))


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

def summon_hint_menu():
    global hints
    popups.append(Popup(
        title="Меню подсказок",
        text="123",
        buttons=[
            Button(text="1", size=(450, 450), command=hints.get_hint),
            Button(text="2", size=(450, 450), command=hints.solve)
        ],
        big_buttons=True,
        destroy_on_click=True
    ))


def show_menu():
    global curent_page, prev_page

    def set_page(n):
        global curent_page, prev_page
        curent_page, prev_page = n, curent_page

    def unlock_all():
        saved_data["max_level"] = 60
        save_data()

    exit_button = Button(command=close_app, position=get_proportion(screen_w - 50, height - 50),
                         size=get_proportion(50, 50),
                         color=(255, 0, 0), text="X")
    play_button = Button(size=get_proportion(450, 150),
                         position=(screen_w / 2 - 175 * get_proportion()[0], 170 * get_proportion()[1]),
                         text="Продолжить",
                         text_align="center",
                         command=start_level, command_args=[saved_data["max_level"]])
    levels_button = Button(size=get_proportion(450, 150),
                           position=(screen_w / 2 - 175 * get_proportion()[0], 370 * get_proportion()[1]),
                           text="Уровни",
                           text_align="сenter",
                           command=set_page, command_args=[2], get_answ=1)
    info_button = Button(size=get_proportion(450, 150),
                         position=(screen_w / 2 - 175 * get_proportion()[0], 570 * get_proportion()[1]), text="Инфо",
                         text_align="сenter")
    back_button = Button(size=get_proportion(50, 50, square="h"), position=(0, 0), text="<-", command=set_page,
                         command_args=[1])

    mute_button = Button(size=get_proportion(150, 150, square="h"),
                         position=(info_button.rect.left, 770 * get_proportion()[1]), text="M",
                         bool_state=saved_data["muted"])
    settings_button = Button(size=get_proportion(150, 150, square="h"),
                             position=(info_button.rect.right - 150 * get_proportion()[0], get_proportion()[1] * 770),
                             text="S", command=set_page, command_args=[3])

    level_buttons = LevelButtonsGroup()
    button_next = Button(command=level_buttons.next, position=(screen_w - 50, screen_h // 2), text=">")
    button_prev = Button(command=level_buttons.prev, position=(0, screen_h // 2), text="<")

    unlock_all_button = Button(size=get_proportion(450, 150),
                               position=(screen_w / 2 - 175 * get_proportion()[0], 300 * get_proportion()[1]),
                               text="Открыть все уровни", command=unlock_all)

    curent_page = 1
    prev_page = curent_page
    curent_levels_page = 1
    l1 = [play_button, levels_button, info_button, mute_button, settings_button]
    l2 = [level_buttons, button_prev, button_next]
    l2[0].draw()
    l3 = [unlock_all_button]

    while True:
        screen.fill((128, 128, 128))

        clicked = False
        if prev_page != curent_page:
            prev_page = curent_page

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicked = True
                    exit_button.update()
                    if not [i for i in popups if type(i) is Popup]:
                        play_button.update()
                        resp = levels_button.update()
                        info_button.update()
                        mute_button.update()
                        settings_button.update()
                        button_next.update()
                        button_prev.update()
                        back_button.update()
                        if resp == 1:
                            clicked = False

        # Update.
        update_popups(clicked)
        if curent_page == 1:
            [i.show() for i in l1]
        else:
            [i.hide() for i in l1]
        if curent_page == 2:
            [i.show() for i in l2]
        else:
            [i.hide() for i in l2]
        if curent_page == 3:
            [i.show() for i in l3]
            [i.update() for i in l3]
        else:
            [i.hide() for i in l3]
        l2[curent_levels_page - 1].update(clicked if curent_page == prev_page else False)

        # Draw.
        if curent_page == 1:
            [i.draw() for i in l1]
        elif curent_page == 2:
            [i.draw() for i in l2]
        elif curent_page == 3:
            [i.draw() for i in l3]

        back_button.draw()
        draw_popups()
        exit_button.draw()

        pygame.display.flip()
        fpsClock.tick(fps)

    # start_level(1)


def start_level(level=1):
    with open(f"{Path.cwd()}/levels/level_{level}.json", "r") as f:
        json_data = json.load(f)

    [i.remove() for i in popups]
    get_tutorial_step(1)

    def check_solved():
        if len(curent_tiles) != 36:
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
            raise FunctionExit
        else:
            if not path_rects:
                for tile in result[1]:
                    path_rects.append(PathRect(get_board_position(*tile[::-1])))

    global car_surf, car_list, hint_rects, hints
    house_list = []
    car_list = []
    path_rects = []
    hints = Hints(json_data["solution"])

    for i in json_data:
        if "house" in i:
            house_list.append(House(json_data[i], houses[i]))
    red_car = pygame.Rect(get_board_position(*json_data["car"]), [TILE_SIZE] * 2)

    car_surf = CarSurface()
    ocupied_tiles = [json_data["car"]]
    for i in house_list:
        ocupied_tiles.extend(i.board_tiles)

    for num, key in enumerate(cars):
        car_list.append(Car(cars[f'car{num + 1}'], num + 1, car_places[num]))

    submit_button = Button(command=check_solved, position=get_proportion(w=1600, h=450),
                           size=[100 * get_proportion()[0]] * 2)
    exit_button = Button(command=close_app, position=(screen_w - 50 * get_proportion()[0], 0),
                         size=[50 * get_proportion()[0]] * 2,
                         color=(255, 0, 0), text="X")
    hint_button = Button(position=get_proportion(w=0, h=540), command=summon_hint_menu)

    while True:
        curent_tiles = ocupied_tiles.copy()
        screen.fill((0, 0, 0))

        clicked = False

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEWHEEL:
                for car in car_list:
                    if car.is_picked:
                        car.rotate(event.y * -1 * (-1 if saved_data["rotation_inversion"] else 1))
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicked = True

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
        hints.update()

        if clicked:
            exit_button.update()
            if not popups:
                hint_button.update()
                try:
                    submit_button.update()
                except FunctionExit:
                    popups.extend(
                        [Popup(title="TeSt", buttons=[Button(text="123"), Button(text="123"), Button(text="123")])])
        update_popups(clicked)

        if len(curent_tiles) != 36:
            path_rects.clear()

        # Draw.
        #  bottom level
        for tile in grid:
            pygame.draw.rect(screen, (0, 255, 0), tile)
        pygame.draw.rect(screen, (255, 0, 0), red_car)
        [house.draw() for house in house_list]

        #  mid level
        hint_button.draw()
        [car.draw() for car in car_list]
        submit_button.draw()
        hints.draw()
        car_surf.draw()

        # top level
        last = None
        for car in car_list:  # отрисовка машин на верхнем слое только если они не размещены
            if not car.is_placed:
                car.draw()
            if car.is_picked:
                last = car
        last.draw() if last else None

        [i.draw() for i in path_rects]

        draw_popups()
        exit_button.draw()

        pygame.display.flip()
        fpsClock.tick(fps)


def get_board_position(x, y):
    return x * TILE_SIZE + board.topleft[0], y * TILE_SIZE + board.topleft[1]


def save_data():
    with open(f"{Path.cwd()}/data.json", "w") as f:
        json.dump(saved_data, f)


def read_data():
    global saved_data
    with open(f"{Path.cwd()}/data.json", "r") as f:
        saved_data = json.load(f)


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
        self.tiles = [get_board_position(i, j) for i, j in self.board_tiles]

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
            self.car_surf_rect.top += get_proportion(h=85)[1]
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
        self.rotation = 0
        self.grab_point = [0, 0]
        self.grabbed_rect = -1

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
                self.get_grab_pos()
                self.is_placed = False
                self.is_on_whiteboard = False
        else:
            if (not pygame.mouse.get_pressed()[0]) and (not self.is_on_whiteboard):
                self.is_picked = False
                self.is_placed = True
                # if self.main_rect.colliderect(ground) and car_surf.is_expended:
                #     self.is_on_whiteboard = True
                # else:
                #     self.is_on_whiteboard = False

        if self.is_picked:
            if self.grabbed_rect == -1:
                self.main_rect.center = pygame.mouse.get_pos()
                self.main_rect.x += self.grab_point[0]
                self.main_rect.y += self.grab_point[1]
            else:
                self.rects[self.grabbed_rect].center = pygame.mouse.get_pos()
                self.rects[self.grabbed_rect].x += self.grab_point[0]
                self.rects[self.grabbed_rect].y += self.grab_point[1]
                self.main_rect.center = self.rects[self.grabbed_rect].center
                item = self.data[self.grabbed_rect]
                exec(f'self.main_rect.{item[1]}=self.rects[self.grabbed_rect].{item[0]}')

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
        if self.main_rect.y <= screen_h + 100 and not car_surf.is_expended:
            self.main_rect.y += 85 * get_proportion()[1]
        else:
            self.main_rect.x, self.main_rect.y = car_surf.get_position_of(self.number)
            self.reset_rotation()

        self.update_rects()

    def draw(self):
        if self.car_pos == -1:
            pygame.draw.rect(screen, (30, 30, 120), self.main_rect)
        else:
            pygame.draw.rect(screen, (150, 150, 150), self.main_rect)
        for index, item in enumerate(self.rects):
            if index == self.car_pos and self.car_pos != -1:
                pygame.draw.rect(screen, (30, 30, 120), item)
            else:
                pygame.draw.rect(screen, (150, 150, 150), item)

    def place_closest(self):
        for tile in grid:
            if tile.collidepoint(self.main_rect.center):
                self.main_rect.center = tile.center
                self.check_boundary()
                return
        self.is_placed = False
        self.is_on_whiteboard = True

    def rotate(self, step: int):
        self.rotation += step
        self.rotation %= 4
        self.data = rotate(self.data, step)

        self.update_rects()

    def reset_rotation(self):
        self.rotation = 0
        self.data = cars[f'car{self.number}']

    def check_boundary(self):
        for rect in self.rects:
            if not rect.colliderect(board):
                self.is_placed, self.is_on_whiteboard = False, True

    def get_all_rects(self):
        return self.rects + [self.main_rect]

    def get_car_position(self, main_rect=False, fix_y=False, get_rotation=False):
        a = -1
        car = self.rects[self.car_pos] if self.car_pos != -1 else self.main_rect
        if main_rect:
            car = self.main_rect
        for tile in grid:
            if car.colliderect(tile):
                a = grid.index(tile)
        res = [a // 6, a % 6]
        if get_rotation:
            res.append(self.rotation)
        if fix_y:
            res[1] -= 1
        return res

    def get_grab_pos(self):
        self.grabbed_rect = -1
        for index, rect in enumerate(self.rects):
            if rect.collidepoint(pygame.mouse.get_pos()):
                self.grabbed_rect = index
        if self.grabbed_rect == -1:
            self.grab_point = [self.main_rect.center[0] - pygame.mouse.get_pos()[0],
                               self.main_rect.center[1] - pygame.mouse.get_pos()[1]]
        else:
            self.grab_point = [self.rects[self.grabbed_rect].center[0] - pygame.mouse.get_pos()[0],
                               self.rects[self.grabbed_rect].center[1] - pygame.mouse.get_pos()[1]]


class PathRect:
    def __init__(self, position=(0, 0), color: tuple = (255, 20, 20)):
        self.rect = pygame.Rect(position, [TILE_SIZE] * 2)
        self.surf = pygame.Surface([TILE_SIZE] * 2)
        self.surf.fill(color)
        self.surf.set_alpha(80)

    def draw(self):
        screen.blit(self.surf, self.rect)


class FunctionExit(Exception):
    pass


class Button:
    def __init__(self, position: tuple = (0, 0), size=(100, 100), get_ansf=False, locked=False, **kwargs):
        self.kwargs = kwargs.copy()
        self.is_hidden = False
        self.rect = pygame.Rect(position, size)
        self.rect_color = self.kwargs.get("color")
        self.text = self.kwargs.get("text")
        self.text_align = self.kwargs.get("text_align", "topleft")
        self.bool_state = self.kwargs.get("bool_state")
        self.get_ansf = get_ansf
        self.is_locked = locked
        if not self.rect_color:
            self.rect_color = (100, 255, 0)

        if self.text:
            self.text = font1.render(self.text, False, (0, 0, 0))

    def update(self):
        if self.is_hidden or self.is_locked:
            return
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if self.kwargs.get("command"):
                if self.kwargs.get("command_args"):
                    resp = self.kwargs["command"](*self.kwargs.get("command_args"))
                else:
                    resp = self.kwargs["command"]()
                if self.get_ansf:
                    if type(self.get_ansf) is bool:
                        return resp
                    else:
                        return self.get_ansf

    def hide(self):
        self.is_hidden = True

    def show(self):
        self.is_hidden = False

    def draw(self):
        if self.is_hidden:
            return
        pygame.draw.rect(screen, self.rect_color, self.rect)
        if self.text:
            screen.blit(self.text, self.get_text_position())

    def get_text_position(self):
        x_d = self.text.get_width() / 2
        y_d = self.text.get_height() / 2
        if self.text_align == "center":
            pos = list(self.rect.center)
            pos[0] -= x_d
            pos[1] -= y_d
        elif self.text_align in ["left", "right"]:
            pos = [eval(f'self.rect.{self.text_align}'), 0]
            pos[1] = self.rect.center[1] - y_d
            if self.text_align == "left":
                pos[0] += x_d
            else:
                pos[0] -= x_d
        else:
            self.text_align = "center"
            pos = self.get_text_position()
        return pos

    def switch(self):
        if self.bool_state is not None:
            self.bool_state = not self.bool_state

    def switch_lock(self):
        self.is_locked = not self.is_locked


class Popup:
    def __init__(self, surf=default_surf, title="", subtext="", buttons=[], big_buttons=False, destroy_on_click=False):
        self.title, self.subtext = title, subtext
        self.surf = surf
        self.buttons = buttons.copy()
        self.big_buttons = big_buttons
        self.destroy_on_click = destroy_on_click
        self.check_buttons()

        self.main_rect = self.surf.get_rect()
        self.main_rect.center = screen.get_rect().center
        self.main_rect.x -= screen_w
        self.is_shown = True
        self.not_expanded = True
        self.speed = get_proportion(w=200, h=90)

        self.title = font1.render(self.title, False, (0, 0, 0))
        self.subtext = self.subtext.split("\n")
        self.subtext = [font2.render(i, False, (0, 0, 0)) for i in self.subtext]
        self.remove_self = False

    def update(self, clicked=False):
        if self.main_rect.centerx < screen.get_rect().centerx:
            self.main_rect.centerx += self.speed[0]
            if self.main_rect.centerx > screen.get_rect().centerx:
                self.main_rect.centerx = screen.get_rect().centerx
            self.update_buttons()

            return
        if clicked:
            [i.update() for i in self.buttons]
            if self.destroy_on_click and any([i.rect.collidepoint(pygame.mouse.get_pos()) for i in self.buttons]):
                self.remove()

        if self.remove_self:
            self.main_rect.centery -= self.speed[1]
            self.update_buttons()
            if self.main_rect.bottom < 0:
                popups.remove(self)

    def draw(self):
        screen.blit(self.surf, self.main_rect)
        [button.draw() for button in self.buttons]
        t = self.title.get_rect()
        t.midtop = self.main_rect.midtop
        t[1] += 15
        screen.blit(self.title, t)
        for i in enumerate(self.subtext):
            t = i[1].get_rect()
            t.midtop = self.main_rect.midtop
            t[1] += 150 + 100 * i[0]
            screen.blit(i[1], t)

    def remove(self):
        self.remove_self = True

    def update_buttons(self):
        if len(self.buttons) == 3:
            if self.big_buttons:
                t = list(self.main_rect.bottomleft)
                t[0] += get_proportion(w=270)[0]
                t[1] -= get_proportion(h=370)[1]
                self.buttons[0].rect.center = t
                t = list(self.main_rect.bottomright)
                t[0] -= get_proportion(w=270)[0]
                t[1] -= get_proportion(h=370)[1]
                self.buttons[1].rect.center = t
                t = list(self.main_rect.midbottom)
                t[1] -= get_proportion(h=370)[1]
                self.buttons[2].rect.center = t
            else:
                t = list(self.main_rect.bottomleft)
                t[0] += get_proportion(w=300)[0]
                t[1] -= get_proportion(h=100)[1]
                self.buttons[0].rect.center = t
                t = list(self.main_rect.bottomright)
                t[0] -= get_proportion(w=300)[0]
                t[1] -= get_proportion(h=100)[1]
                self.buttons[1].rect.center = t
                t = list(self.main_rect.midbottom)
                t[1] -= get_proportion(h=100)[1]
                self.buttons[2].rect.center = t
        elif len(self.buttons) == 2:
            if self.big_buttons:
                t = list(self.main_rect.bottomleft)
                t[0] += get_proportion(w=420)[0]
                t[1] -= get_proportion(h=370)[1]
                self.buttons[0].rect.center = t
                t = list(self.main_rect.bottomright)
                t[0] -= get_proportion(w=420)[0]
                t[1] -= get_proportion(h=370)[1]
                self.buttons[1].rect.center = t
                t = list(self.main_rect.midbottom)
                t[1] -= get_proportion(h=370)[1]
            else:
                t = list(self.main_rect.bottomleft)
                t[0] += get_proportion(w=450)[0]
                t[1] -= get_proportion(h=100)[1]
                self.buttons[0].rect.center = t
                t = list(self.main_rect.bottomright)
                t[0] -= get_proportion(w=450)[0]
                t[1] -= get_proportion(h=100)[1]
                self.buttons[1].rect.center = t
                t = list(self.main_rect.midbottom)
                t[1] -= get_proportion(h=100)[1]

        else:
            pass

    def check_buttons(self):
        if len(self.buttons) > 3:
            raise AttributeError(f"buttons argument takes 3 or less arguments but {len(self.buttons)} were given")

class MiniPopup(Popup):
    def check_buttons(self):
        if len(self.buttons) > 1:
            raise AttributeError(f"buttons argument takes only one argument but {len(self.buttons)} were given")

    def __init__(self, *args, **kwargs):
        kwargs["surf"] = mini_surf
        kwargs["destroy_on_click"] = True

        super().__init__(*args, **kwargs)
        self.main_rect.top = 0
        self.main_rect.left = width
        self.speed = (15, 15)

    def update(self, clicked=False):
        if self.main_rect.left > width - self.main_rect.width and not self.remove_self:
            self.main_rect.left -= self.speed[0]
            if self.main_rect.left < width - self.main_rect.width:
                self.main_rect.left = width - self.main_rect.width
            self.update_buttons()

            return
        if clicked:
            [i.update() for i in self.buttons]
            if self.destroy_on_click and any([i.rect.collidepoint(pygame.mouse.get_pos()) for i in self.buttons]):
                self.remove()

        if self.remove_self:
            self.main_rect.x += self.speed[0]
            self.update_buttons()
            if self.main_rect.left > width:
                popups.remove(self)

    def update_buttons(self):
        if self.buttons:
            self.buttons[0].rect.bottomleft = self.main_rect.bottomleft
            self.buttons[0].rect.y -= 20
            self.buttons[0].rect.x += 20


class LevelButtonsGroup:
    def __init__(self):
        def get_button_position(n):
            return 350 * get_proportion()[0] + ((n - 1) % 15 % 4) * 360 * get_proportion()[0], 50 * get_proportion()[
                1] + (
                           (n - 1) % 15 // 4) * 270 * get_proportion()[1]

        self.bg_colors = [(117, 252, 19), (255, 235, 0), (221, 31, 10), (18, 47, 232)]
        self.levels = [
            Button(text=str(i), color=self.bg_colors[(i - 1) // 15], command=start_level,
                   position=get_button_position(i),
                   size=[150 * get_proportion()[0]] * 2,
                   command_args=(i,)) for i in range(1, 61)]
        self.frame = 0

        self.curent_page = 0

        self.bg_surf = pygame.Surface(screen.get_size())
        self.bg_surf.set_alpha(0)

    def update(self, clicked=False):
        self.bg_surf.fill(self.bg_colors[self.curent_page])
        if self.frame <= 150:
            self.frame += 6
        self.bg_surf.set_alpha(self.frame)
        [button.update() for button in
         self.levels[self.curent_page * 15:self.curent_page * 15 + 16]] if clicked else None

    def draw(self):
        screen.fill((128, 128, 128))
        screen.blit(self.bg_surf, (0, 0))
        [i.draw() for i in self.levels[self.curent_page * 15:self.curent_page * 15 + 15][::-1]]

    def hide(self):
        [button.hide() for button in self.levels]

    def show(self):
        [button.show() for button in self.levels]

    def next(self):
        self.curent_page += 1
        self.curent_page %= 4
        self.frame = 0

    def prev(self):
        self.curent_page -= 1
        if self.curent_page < 0:
            self.curent_page = 3
        self.frame = 0


class Hints:
    def __init__(self, data):
        self.ghost_car_data = None
        self.ghost_car_number = None
        self.data = data.copy()
        self.hint_rects = []
        self.ghost_car = None
        self.surf = pygame.Surface([TILE_SIZE] * 2)
        self.surf.fill((150, 255, 150))
        self.surf2 = self.surf.copy()
        self.surf.set_alpha(200)
        self.surf2.set_alpha(275)

    def get_hint(self):
        self.update()
        if self.ghost_car:
            return
        self.reset()
        for index, car in enumerate(car_list):
            c_data = self.data[f'car{index + 1}']
            if car.is_placed:
                if car.get_car_position(main_rect=True, fix_y=False, get_rotation=True) != c_data:
                    self.get_ghost_car(index + 1, c_data[-1], get_board_position(*c_data[:-1]), None)
                    break
        for index, car in enumerate(car_list):
            c_data = self.data[f'car{index + 1}']
            if not car.is_placed:
                self.get_ghost_car(index + 1, c_data[-1], get_board_position(*c_data[:-1]), None)
                break

    def get_ghost_car(self, number, rotation, position, old_position):
        if self.ghost_car_data:
            return
        center_rect = pygame.Rect(position, [TILE_SIZE] * 2)
        data = cars[f'car{number}']
        data = rotate(data, rotation)
        other_rects = [center_rect.copy() for i in range(len(data))]
        for index, item in enumerate(data):
            other_rects[index].x, other_rects[index].y = center_rect.x, center_rect.y
            exec(f'other_rects[index].{item[0]}=center_rect.{item[1]}')
        self.ghost_car, self.ghost_car_data, self.ghost_car_number = other_rects + [center_rect], self.data[
            f'car{number}'], number

    def update(self):
        if self.ghost_car and car_list[self.ghost_car_number - 1].is_placed:
            car = car_list[self.ghost_car_number - 1].get_car_position(main_rect=True, fix_y=False, get_rotation=True)
            if car == self.ghost_car_data:
                self.reset()
            else:
                if self.ghost_car_number == 2 and car is not None:
                    car[-1] += 2
                    car[-1] %= 4
                    if car == self.ghost_car_data:
                        self.reset()

    def draw(self):
        if self.ghost_car is None:
            return
        for i, rect in enumerate(self.ghost_car):
            if i == len(self.ghost_car) - 1:
                i = -1
            if i == car_places[self.ghost_car_number - 1]:
                screen.blit(self.surf2, rect)
            else:
                screen.blit(self.surf, rect)

    def solve(self):
        for index, car in enumerate(car_list):
            car.reset_rotation()
            car.is_picked = True
            car.rotate(self.data[f'car{index + 1}'][-1])
            car.main_rect.topleft = get_board_position(*self.data[f'car{index + 1}'][:-1])
            car.place_closest()
            car.is_placed = True
            car.is_on_whiteboard = False
            car.is_picked = False
            car.update_rects()

    def reset(self):
        self.ghost_car = None
        self.ghost_car_data = None
        self.ghost_car_number = None


read_data()

popups = [MiniPopup(title ="Title", buttons=[Button(text="123")])] # [Popup(title="TeSt", text="123", buttons=[Button(size=(450, 450), command=lambda *a: [i.remove() for i in popups]) for i in range(2)], big_buttons=True)]
grid = []
board = pygame.Rect((0, 0), (6 * TILE_SIZE, 6 * TILE_SIZE))
ground_pos = list(screen.get_rect().center)
ground_pos[1] -= 50
board.center = ground_pos
for x in range(6):
    for y in range(6):
        x_pos, y_pos = get_board_position(x, y)
        grid.append(pygame.Rect((x_pos, y_pos), [TILE_SIZE] * 2))

show_menu()
