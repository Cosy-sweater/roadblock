# buttons default sizes: 150x150, 450x150, 450x450, 150x70, 50x50
# max_level unsync bug
# sound credits: https://www.zapsplat.com
import sys
import json
import time
from pathlib import Path

import level_solver

import pygame
from pygame.locals import *
from easing_functions import *
import builtins
import webbrowser

if __name__ != "__main__":
    sys.exit()

pygame.init()
pygame.font.init()

fps = 60
fpsClock = pygame.time.Clock()

saved_data = {}
width, height = 1920, 1080
# screen = pygame.display.set_mode((600, 400))
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
builtins.screen_resolution = (screen.get_width(), screen.get_height())

font1 = pygame.font.SysFont('Comic Sans MS', int(30 * screen.get_width() / width))
font2 = pygame.font.SysFont('Comic Sans MS', int(24 * screen.get_width() / width))
font3 = pygame.font.SysFont('Comic Sans MS', int(28 * screen.get_width() / width))


class Volume:
    def __init__(self, a):
        self.volume = a
        self.old_volume = a

    def set(self, value):
        self.volume = value
        volume_slider.value = value
        volume_slider.set_slider_pos_to_value()
        set_volume(self.volume)

    def get(self):
        return self.volume

def save_data():
    saved_data["volume"] = global_volume.get()
    with open(f"{Path.cwd()}/data.json", "w") as f:
        json.dump(saved_data, f)


def read_data():
    global saved_data
    with open(f"{Path.cwd()}/data.json", "r") as f:
        saved_data = json.load(f)


global_volume = Volume(1.0)

sound_list = []
click_sound = [pygame.mixer.Sound(f"{Path.cwd()}/sounds/click_sound.mp3")]  # is pointer for using global volume
builtins.click_sound = click_sound

sound_list.append(click_sound)
from my_widgets import Button, Slider

levels_exist = 15
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


def close_app():
    save_data()
    pygame.quit()
    sys.exit()


def update_popups(clicked=False):
    [i.update(clicked=clicked) for i in popups]


def draw_popups():
    [i.draw() for i in popups]


def get_proportion(w: float = 1, h: float = 1, square: str = None, g_pow: float = 1, l_h_pow: float = 1,
                   l_w_pow: float = 0):
    if not square:
        return w * round(screen_w / width, 1) ** max(g_pow, l_w_pow), \
               h * round(screen_h / height, 1) ** max(g_pow, l_h_pow)
    else:
        if square.lower() == "h":
            return h * round(screen_h / height, 1) ** max(g_pow, l_w_pow), \
                   h * round(screen_h / height, 1) ** max(g_pow, l_h_pow)
        elif square.lower() == "w":
            return w * round(screen_w / width, 1) ** max(g_pow, l_w_pow), \
                   w * round(screen_w / width, 1) ** max(g_pow, l_h_pow)
        else:
            raise ValueError("Argument takes 'w' and 'h' values only")


TILE_SIZE = int(get_proportion(h=150, g_pow=1.2)[1])
w_pow, h_pow = 1.2, 1.2


def set_volume(value):
    for i in sound_list:
        i[0].set_volume(value)


def get_tutorial_step(n: int):
    button_next = Button(text="Далее", size=get_proportion(150, 70), command=get_tutorial_step, command_args=[n + 1])
    tutorial_popups = [
        Popup(title='Правила', subtext='''Задача игры состоит в том, чтобы не дать красной машине выбраться из двора
Для этого нужно расставить на поле шесть полицейских машин так, чтобы заблокировать ей выезд''',
              buttons=[button_next], destroy_on_click=True),

        MiniPopup(title="Поле", subtext='''На поле присутствуют красная машина,
дома, а также пустые поля для
размещения полицейских машин''', buttons=[button_next]),

        MiniPopup(title="Полицейские машины", subtext='''Чтобы посмотреть полицейские машины,
сдвиньте мышь в нижнюю часть экрана''', buttons=[button_next], destroy_on_event=lambda *_: car_surf.is_expended,
                  do_on_destroy=f'get_tutorial_step({n + 1})'),

        Popup(title="Полицейские машины",
              subtext='''Чтобы поставить полицейскую машинну на поле, нужно навести на неё мышь
и перетянуть её в нужную часть поля
        
Чтобы вращать машину, нужно вращать ролик мыши''',
              buttons=[button_next], destroy_on_click=True),

        Popup(title="Красная машины", subtext='''Красная машина может двигаться только по свободным клеткам
Она считается заблокированной тогда, когда не остаётся путей, ведущих к краю поля
            
Чтобы пройти уровень, нужно заблокировать красную машину,
разместив при этом все полицейские машины''',
              buttons=[button_next], destroy_on_click=True),

        Popup(title="Подсказки", subtext='''Если не получается пройти уровень, 
можно воспользоваться подсказкой
        
        Меню подсказок можно вызвать кнопкой слева''',
              buttons=[button_next], destroy_on_click=True),

        MiniPopup(title="Подсказки", subtext='''Если воспользоваться меню подсказок,
         то время прохождения уровня
          не будет засчитано''',
                  buttons=[
                      Button(text="Закончить", size=get_proportion(150, 70), command=lambda *_: None, command_args=[])],
                  destroy_on_click=True)
    ]
    if n > len(tutorial_popups):
        return
    popups.append(tutorial_popups[n - 1])


default_surf = pygame.Surface(get_proportion(w=1500, h=800))
default_surf.fill((44, 44, 44))
mini_surf = pygame.Surface(get_proportion(w=500, h=300))
mini_surf.fill((44, 44, 44))

lock_image = pygame.image.load(f'{Path.cwd()}/img/lock.png').convert_alpha()
lock_image = pygame.transform.scale(lock_image, get_proportion(150, 150, square="w"))


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
    popups.append(Popup(
        title="Меню подсказок",
        subtext="",
        buttons=[
            Button(text="1", size=get_proportion(450, 450, square="h"), command=hints.get_hint),
            Button(text="2", size=get_proportion(450, 450, square="h"), command=hints.solve)
        ],
        big_buttons=True,
        destroy_on_click=True
    ))


def get_time_of_levels():
    time_list = []
    for i in range(1, levels_exist + 1):
        with open(f'{Path.cwd()}/levels/level_{i}.json', "r") as f:
            time_list.append(json.load(f)["time"])
    time_list = time_list + [999.999] * (60 - levels_exist)
    return time_list

read_data()
volume_slider = Slider(title="Громкость", value=saved_data["volume"], variable=[global_volume],
                       position=get_proportion(width / 2 - 175, 700, l_h_pow=h_pow),
                       show_percent=True, size=get_proportion(450, 150))


def show_menu():
    global curent_page, prev_page, volume

    def set_page(n):
        global curent_page, prev_page
        nonlocal clicked
        clicked = False
        curent_page, prev_page = n, curent_page

    def unlock_all():
        saved_data["max_level"] = 60
        [i.remove() for i in popups]
        popups.append(
            MiniPopup(subtext="Все уровни теперь доступны",
                      buttons=[Button(text="OK", size=get_proportion(150, 70))])
        )
        save_data()

    def reset_data():
        global saved_data
        saved_data = {"rotation_inversion": False, "max_level": 1, "tutorial": True, "volume": 1}
        global_volume.set(1)
        volume_slider.set_slider_pos_to_value()
        [i.remove() for i in popups]
        popups.append(
            MiniPopup(subtext="Информация об игре\n и настройки сброшены",
                      buttons=[Button(text="OK", size=get_proportion(150, 70))])
        )
        save_data()

        for i in range(1, levels_exist + 1):
            with open(f'{Path.cwd()}/levels/level_{i}.json', "r") as f:
                saved = json.load(f)
                saved["time"] = 999.999
            with open(f'{Path.cwd()}/levels/level_{i}.json', "w") as f:
                json.dump(saved, f)

    exit_button = Button(command=close_app,
                         position=(screen_w - get_proportion(h=50)[1], screen_h - get_proportion(h=50)[1]),
                         size=get_proportion(50, 50, square="h"),
                         color=(255, 0, 0), text="X")
    play_button = Button(size=get_proportion(450, 150),
                         position=get_proportion(width / 2 - 175, 170, l_h_pow=h_pow),
                         text="Продолжить",
                         text_align="center",
                         command=start_level, command_args=[saved_data["max_level"]])
    levels_button = Button(size=get_proportion(450, 150),
                           position=get_proportion(width / 2 - 175, 370, l_h_pow=h_pow),
                           text="Уровни",
                           text_align="сenter",
                           command=set_page, command_args=[2], get_answ=1)
    info_button = Button(size=get_proportion(450, 150),
                         position=get_proportion(width / 2 - 175, 570, l_h_pow=h_pow), text="Инфо",
                         text_align="сenter", command=set_page, command_args=[4])
    back_button = Button(size=get_proportion(50, 50, square="h"), position=(0, 0), text="<-", command=set_page,
                         command_args=[1])

    settings_button = Button(size=get_proportion(450, 150),
                             position=get_proportion(width / 2 - 175, 770, l_h_pow=h_pow),
                             text="Настройки", command=set_page, command_args=[3])

    level_buttons = LevelButtonsGroup()
    button_next = Button(command=level_buttons.next, size=get_proportion(100, 100, square="w"),
                         position=(screen_w - get_proportion(w=100)[0], screen_h // 2), text=">")
    button_prev = Button(command=level_buttons.prev, size=get_proportion(100, 100, square="w"),
                         position=(0, screen_h // 2), text="<")

    unlock_all_button = Button(size=get_proportion(450, 150),
                               position=get_proportion(width / 2 - 175, 300, l_h_pow=h_pow),
                               text="Открыть все уровни", command=unlock_all, )
    reset_button = Button(size=get_proportion(450, 150),
                          position=get_proportion(width / 2 - 175, 500, l_h_pow=h_pow),
                          text="Сброс", command=reset_data, )

    curent_page = 1
    prev_page = curent_page
    curent_levels_page = 1
    l1 = [play_button, levels_button, info_button, settings_button]
    l2 = [level_buttons, button_prev, button_next]
    l2[0].draw()
    l3 = [unlock_all_button, reset_button, volume_slider]
    l4 = [Button(text="123", size=(100, 100), position=screen.get_rect().center)]

    while True:
        screen.fill((128, 128, 128))

        clicked = False
        if prev_page != curent_page:
            prev_page = curent_page

        try:
            for event in pygame.event.get():
                if event.type == QUIT or (
                        event.type == KEYDOWN and event.key == K_F4 and (event.key[K_LALT] or event.key[K_LALT])):
                    close_app()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        clicked = True
                        exit_button.update()
                        if not [i for i in popups if type(i) is Popup]:
                            play_button.update()
                            resp = levels_button.update()
                            info_button.update()
                            settings_button.update()
                            button_next.update()
                            button_prev.update()
                            back_button.update() if curent_page != 1 else None
                            if resp == 1:
                                clicked = False
                if event.type == pygame.KEYDOWN:
                    if curent_page == 2:
                        if event.key == pygame.K_LEFT:
                            level_buttons.prev()
                        if event.key == pygame.K_RIGHT:
                            level_buttons.next()
        except FunctionExit:
            popups.clear()

        # Update.
        try:
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
                [i.update(clicked) for i in l3]
            else:
                [i.hide() for i in l3]
            if curent_page == 4:
                [i.show() for i in l4]
                [i.update(clicked) for i in l4]
            else:
                [i.hide() for i in l4]
            l2[curent_levels_page - 1].update(clicked if curent_page == prev_page else False)
        except FunctionExit:
            popups.clear()

        # Draw.
        if curent_page == 1:
            [i.draw() for i in l1]
        elif curent_page == 2:
            [i.draw() for i in l2]
        elif curent_page == 3:
            [i.draw() for i in l3]
        elif curent_page == 4:
            [i.draw() for i in l4]

        if curent_page != 1:
            back_button.draw()
        draw_popups()
        exit_button.draw()

        pygame.display.flip()
        fpsClock.tick(fps)


def start_level(level=1):
    global saved_data

    read_data()
    with open(f"{Path.cwd()}/levels/level_{level}.json", "r") as f:
        json_data = json.load(f)

    popups.clear()

    if saved_data["tutorial"]:
        saved_data["tutorial"] = False
        save_data()
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
            with open(f"{Path.cwd()}/levels/level_{level}.json", "w") as f:
                t = round(time.perf_counter() - start_time, 1)
                json_data["time"] = min(t if start_time != -1 else 999.999, json_data["time"])
                json.dump(json_data, f)
            if not cheated:
                saved_data["max_level"] = max(level + 1, saved_data["max_level"])
                save_data()
            raise FunctionExit
        else:
            if not path_rects:
                for tile in result[1]:
                    path_rects.append(PathRect(get_board_position(*tile[::-1])))

    def end_gameloop():
        nonlocal game_loop
        game_loop = False
        raise FunctionExit

    global car_surf, car_list, hint_rects, hints, start_time, cheated
    house_list = []
    car_list = []
    path_rects = []
    hints = Hints(json_data["solution"])
    game_loop = True
    start_time = -1
    cheated = False
    flag2 = False

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

    submit_button = Button(command=check_solved, position=get_proportion(w=1800, h=450),
                           size=get_proportion(100, 100, square="h"))
    exit_button = Button(command=close_app,
                         position=(screen_w - get_proportion(h=50)[1], screen_h - get_proportion(h=50)[1]),
                         size=get_proportion(50, 50, square="h"),
                         color=(255, 0, 0), text="X")
    menu_button = Button(command=end_gameloop, position=(0, 0), size=get_proportion(50, 50, square="h"), text="<")

    hint_button = Button(position=get_proportion(w=0, h=450), size=get_proportion(100, 100, square="h"), command=summon_hint_menu)

    while game_loop:
        curent_tiles = ocupied_tiles.copy()
        screen.fill((0, 0, 0))

        clicked = False

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_F4 and (key[K_LALT] or key[K_LALT])):
                close_app()
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
            old = car.is_placed
            car_tiles = car.update()
            if car_surf.car_surf_rect.collidepoint(pygame.mouse.get_pos()) and car.is_placed and not old:
                car.move_to_board()
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
            if car.is_picked and start_time == -1 and not cheated:
                start_time = time.perf_counter()
        hints.update()

        menu_button.update(clicked)
        exit_button.update(clicked)
        if car_surf.car_surf_rect.collidepoint(pygame.mouse.get_pos()):
            clicked = False
        if not popups:
            hint_button.update(clicked)
            try:
                submit_button.update(clicked)
            except FunctionExit:
                popups.append(
                    Popup(title="TeSt", buttons=[
                        Button(text="M", command=end_gameloop, command_args=[]),
                        Button(text="N", command=start_level, command_args=[level + 1]) if level < 60 else None,
                        Button(text="R", command=start_level, command_args=[level])], destroy_on_click=True))
                flag2 = True
        update_popups(clicked)
        if popups:
            if popups[-1].remove_self and flag2:
                return

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
        menu_button.draw()

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

        self.cars_poss = [get_proportion(200, 100), get_proportion(200, 500), get_proportion(600, 320),
                          get_proportion(1000, 260), get_proportion(1600, 100), get_proportion(1400, 500)]
        self.cars_poss = list(map(list, self.cars_poss))
        self.move_limit = screen_h // 3
        self.bottom_border = 90 * (screen_h / height)

        self.is_expended = False

    def update(self):
        if self.car_surf_rect.collidepoint(pygame.mouse.get_pos()):
            if self.car_surf_rect.top > self.move_limit:
                self.car_surf_rect.top -= get_proportion(h=80)[1]
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


class Popup:
    def __init__(self, surf=default_surf, title: str = "", subtext="", buttons=None, big_buttons=False,
                 destroy_on_click=False,
                 destroy_on_event=lambda *_: False, do_on_destroy="pass", show_close_button=True):
        if buttons is None:
            buttons = []
        self.title, self.subtext = title, subtext
        self.text_title = title
        self.surf = surf
        self.buttons = buttons.copy()
        try:
            self.buttons.remove(None)
        except ValueError:
            pass
        self.big_buttons = big_buttons
        self.destroy_on_click = destroy_on_click
        self.check_buttons()
        self.destroy_on_event = destroy_on_event
        self.on_destroy_action = do_on_destroy

        self.main_rect = self.surf.get_rect()
        self.main_rect.center = screen.get_rect().center
        self.main_rect.x -= screen_w
        self.is_shown = True
        self.not_expanded = True
        self.speed = get_proportion(w=200, h=90)
        self.ease_duration = 0.3 * 60
        self.ease_clock = 0
        self.ease_clock2 = 0
        self.ease_generator_x = QuadEaseInOut(start=self.main_rect.centerx, end=screen.get_rect().centerx,
                                              duration=self.ease_duration)
        self.ease_generator_y = CubicEaseInOut(start=screen.get_rect().centery, end=-screen.get_rect().centery,
                                               duration=self.ease_duration)

        self.title = font1.render(self.title, False, (0, 0, 0))
        self.subtext = self.subtext.split("\n")
        if type(self) is Popup:
            self.subtext = [font3.render(i, False, (0, 0, 0)) for i in self.subtext]
        else:
            self.subtext = [font2.render(i, False, (0, 0, 0)) for i in self.subtext]

        self.remove_self = False
        self.close_button = Button(text="<", size=get_proportion(50, 50, square="h"), position=(-200, -200), command=self.remove)
        self.show_close_button = show_close_button

    def update(self, clicked=False):
        if self.main_rect.centerx < screen.get_rect().centerx:
            self.main_rect.centerx = self.ease_generator_x.ease(self.ease_clock)
            self.ease_clock += 1
            self.update_buttons()

            return
        [i.update(clicked) for i in self.buttons]
        if clicked:
            if self.destroy_on_click:
                if any([i.rect.collidepoint(pygame.mouse.get_pos()) for i in self.buttons]):
                    self.remove()
                if self.close_button.rect.collidepoint(pygame.mouse.get_pos()):
                    click_sound[0].play()
                    self.remove()

        if self.destroy_on_event():
            exec(self.on_destroy_action)
            self.remove_self = True

        if self.remove_self:
            self.main_rect.centery = self.ease_generator_y.ease(self.ease_clock2)
            self.ease_clock2 += 1
            self.update_buttons()
            if self.main_rect.bottom < 0:
                if self in popups:
                    popups.remove(self)

    def draw(self):
        screen.blit(self.surf, self.main_rect)
        [button.draw() for button in self.buttons]
        if type(self) == Popup:
            t = self.title.get_rect()
            t.midtop = self.main_rect.midtop
            t[1] += 15
            screen.blit(self.title, t)
            for i in enumerate(self.subtext):
                t = i[1].get_rect()
                t.midtop = self.main_rect.midtop
                t[1] += 150 + 100 * i[0]
                screen.blit(i[1], t)
        else:
            t = self.title.get_rect()
            t.midtop = self.main_rect.midtop
            t[1] += 15
            screen.blit(self.title, t)
            for i in enumerate(self.subtext):
                t = i[1].get_rect()
                t.midtop = self.main_rect.midtop
                t[1] += 75 + 40 * i[0]
                screen.blit(i[1], t)
        self.close_button.draw()

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
            t = list(self.main_rect.midbottom)
            t[1] -= get_proportion(h=100)[1]
            self.buttons[0].rect.center = t
        if self.show_close_button:
            self.close_button.rect.topleft = self.main_rect.topleft

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
        if kwargs.get("show_close_button") is None:
            kwargs["show_close_button"] = False

        super().__init__(*args, **kwargs)
        self.main_rect.top = 0
        self.main_rect.left = screen_w
        self.speed = (15, 15)
        self.ease_duration = 0.5 * 60
        self.ease_generator_x = QuadEaseInOut(start=screen_w + self.main_rect.width,
                                              end=screen_w - self.main_rect.width,
                                              duration=self.ease_duration)
        self.update_buttons()

    def update(self, clicked=False):
        if self.main_rect.left > width - self.main_rect.width and not self.remove_self:
            self.ease_clock += 1
            self.main_rect.left = self.ease_generator_x.ease(self.ease_clock)
            self.update_buttons()

            return
        if clicked:
            [i.update() for i in self.buttons]
            if self.destroy_on_click and (any([i.rect.collidepoint(pygame.mouse.get_pos()) for i in
                                               self.buttons]) or
                                          self.close_button.rect.collidepoint(pygame.mouse.get_pos())):
                self.remove()

        if self.destroy_on_event():
            if not self.remove_self:
                exec(self.on_destroy_action)
                self.remove_self = True
                self.ease_clock = self.ease_duration

        if self.remove_self:
            self.ease_clock -= 1
            self.main_rect.left = self.ease_generator_x.ease(self.ease_clock)
            self.update_buttons()
            if self.main_rect.left > width:
                popups.remove(self)

    def update_buttons(self):
        if self.buttons:
            self.buttons[0].rect.bottomleft = self.main_rect.bottomleft
            self.buttons[0].rect.y -= 20
            self.buttons[0].rect.x += 20
        if self.show_close_button:
            self.close_button.rect.topleft = self.main_rect.topleft


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

        self.max_level_old = -1

    def update(self, clicked=False):
        self.bg_surf.fill(self.bg_colors[self.curent_page])
        if self.frame <= 150:
            self.frame += 6
        self.bg_surf.set_alpha(self.frame)
        [button.update(clicked) for button in
         self.levels[self.curent_page * 15:self.curent_page * 15 + 16]]
        if saved_data["max_level"] != self.max_level_old:
            for i in enumerate(self.levels):
                if i[0] + 1 > saved_data["max_level"]:
                    i[1].is_locked = True
                else:
                    i[1].is_locked = False
            self.max_level_old = saved_data["max_level"]

    def draw(self):
        screen.fill((128, 128, 128))
        screen.blit(self.bg_surf, (0, 0))
        buttons_to_draw = [i for i in self.levels[self.curent_page * 15:self.curent_page * 15 + 15][::-1]]
        [i.draw() for i in buttons_to_draw]
        for i in buttons_to_draw:
            if i.is_locked:
                screen.blit(lock_image, i.rect)
        t = [i for i in get_time_of_levels()[self.curent_page * 15:self.curent_page * 15 + 15][::-1]]
        for i in enumerate(t):
            pos = list(buttons_to_draw[i[0]].rect.midbottom)
            pos[1] -= get_proportion(h=10)[1]
            text = font2.render(str(i[1]) if i[1] != 999.999 else "", False, (0, 0, 0))
            a = text.get_rect()
            a.midtop = pos
            screen.blit(text, a)

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
        global start_time, cheated
        cheated = True
        start_time = -1
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
        global start_time, cheated
        cheated = True
        start_time = -1
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
global_volume.set(saved_data["volume"])

popups = []
grid = []
board = pygame.Rect((0, 0), (6 * TILE_SIZE, 6 * TILE_SIZE))
ground_pos = list(screen.get_rect().center)
ground_pos[1] -= get_proportion(h=50)[1]
board.center = ground_pos
for x in range(6):
    for y in range(6):
        x_pos, y_pos = get_board_position(x, y)
        grid.append(pygame.Rect((x_pos, y_pos), [TILE_SIZE] * 2))

show_menu()
