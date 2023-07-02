# my widgets v1.2
import traceback

import pygame
import builtins
import sys

pygame.init()
pygame.font.init()

if hasattr(builtins, "screen_resolution"):
    screen = pygame.display.set_mode(builtins.screen_resolution)
else:
    screen = pygame.display.set_mode((0, 0))

width, height = 1920, 1080
font1 = pygame.font.SysFont('Comic Sans MS', int(30 * screen.get_width() / width))
font2 = pygame.font.SysFont('Comic Sans MS', int(24 * screen.get_width() / width))
screen_w, screen_h = screen.get_size()


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


class Button:
    def __init__(self, position: tuple = (0, 0), size=(100, 100), get_ansf=False, locked=False, click_sound=None,
                 **kwargs):
        self.kwargs = kwargs.copy()
        self.is_hidden = False
        self.rect = pygame.Rect(position, size)
        self.rect_color = self.kwargs.get("color")
        self.text = self.kwargs.get("text")
        self.text_align = self.kwargs.get("text_align", "topleft")
        self.bool_state = self.kwargs.get("bool_state")
        self.get_ansf = get_ansf
        self.is_locked = locked
        self.mouse_hover = False
        self.image_size = 0
        if click_sound:
            self.click_sound = click_sound[0]
        elif hasattr(builtins, "click_sound"):
            self.click_sound = builtins.click_sound[0]
        else:
            self.click_sound = None
        if not self.rect_color:
            self.rect_color = (100, 255, 0)

        if self.text:
            self.text = font1.render(self.text, False, (0, 0, 0))

    def update(self, clicked=True):
        if self.is_hidden or self.is_locked:
            return
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if not clicked:
                self.mouse_hover = True
            else:
                if self.click_sound:
                    self.click_sound.play()
                if self.kwargs.get("command"):
                    if self.kwargs.get("command_args"):
                        if self.kwargs.get("command_args") == "bool":
                            resp = self.kwargs["command"](self.bool_state)
                        else:
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


class Slider:
    def __init__(self, position: tuple = (0, 0), size=(450, 150), variable=None, value_range: tuple = (0, 1),
                 click_sound=None, title: str = "", value=0, show_percent=False):
        self._value = value
        self.value_range = value_range
        self.variable = variable

        if type(variable) is not list:
            raise ValueError("Variable argument must be a list with one element containing a variable\nThis is used "
                             "to create a pointer")
        if len(variable) != 1:
            raise ValueError("Variable argument must be a list with one element containing a variable\nThis is used "
                             "to create a pointer")

        if click_sound:
            self.click_sound = click_sound[0]
        elif hasattr(builtins, "click_sound"):
            self.click_sound = builtins.click_sound[0]
        else:
            self.click_sound = None

        self.show_precent = show_percent
        self.rect = pygame.Rect(position, size)
        if self.show_precent:
            self.rect.height += get_proportion(h=50)[1]
        self.scrollbar = Scrollbar(direction="h", click_sound=self.click_sound,
                                   value_range=self.value_range, value=value,
                                   size=(size[0] - get_proportion(w=50)[0], get_proportion(h=25)[1]),
                                   pos=(self.rect.left + get_proportion(w=25)[0],
                                        self.rect.centery + get_proportion(h=10)[1]))
        self.scrollbar.set_slider_pos_to_value()

        self.title = title
        self.mouse_hover = False
        self.image_size = 0
        self.is_hidden = False

        self.is_held = False

        if self.title:
            self.title = font1.render(self.title, False, (0, 0, 0))

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.scrollbar.value = value
        self.scrollbar.set_slider_pos_to_value()

    def update(self, clicked=False):
        if self.is_hidden:
            return

        self.scrollbar.update(clicked)

        if hasattr(self.variable[0], "set"):
            self.variable[0].set(self.get_value())
        else:
            self.variable[0] = self.get_value()

    def draw(self):
        if self.is_hidden:
            return
        pygame.draw.rect(screen, (50, 255, 50), self.rect)
        self.scrollbar.draw()
        pos = self.title.get_rect()
        pos.centerx = self.rect.centerx
        pos.top = self.rect.top + 15
        screen.blit(self.title, pos)
        if self.show_precent:
            t = str(int(self.get_value() / self.value_range[1] * 100))
            t = font2.render(t, False, (0, 0, 0))
            t2 = t.get_rect()
            t2.bottom = self.rect.bottom - get_proportion(h=15)[1]
            t2.centerx = self.rect.centerx
            screen.blit(t, t2)

    def hide(self):
        self.is_hidden = True

    def show(self):
        self.is_hidden = False

    def get_value(self):
        return self.scrollbar.get_value()

    def set_slider_pos_to_value(self):
        self.scrollbar.set_slider_pos_to_value()


class Scrollbar:
    def horizontal_set_slider_pos_to_value(self):
        self.slider_rect.left = self.slider_base.left + (self.slider_base.width - self.slider_rect.width) / \
                                   (self.value_range[1] - self.value_range[0]) * self.value

    def vertical_set_slider_pos_to_value(self):
        self.slider_rect.top = self.slider_base.top + (self.slider_base.height - self.slider_rect.height) / \
                                   (self.value_range[1] - self.value_range[0]) * self.value

    def horizontal_get_value(self):
        return round(max(float(self.slider_rect.left - self.slider_base.left), 0.001) /
                     (self.slider_base.width - self.slider_rect.width) *
                     (self.value_range[1] - self.value_range[0]) + self.value_range[0], 3)

    def vertical_get_value(self):
        return round(max(float(self.slider_rect.top - self.slider_base.top), 0.001) /
                     (self.slider_base.height - self.slider_rect.height) *
                     (self.value_range[1] - self.value_range[0]) + self.value_range[0], 3)

    def __init__(self, variable=[0], value_range: tuple = (0, 1),
                 click_sound=None, value=0, direction: str = "v", size: tuple = None, pos: tuple = None):
        if click_sound is None:
            click_sound = []
        self.value = value
        self.value_range = value_range
        self.variable = variable

        self.slider_base = pygame.Rect((0, 0), get_proportion(25, 25))
        if size:
            self.slider_base.width, self.slider_base.height = size
        if pos:
            self.slider_base.topleft = pos

        self.slider_rect = pygame.Rect((0, 0), get_proportion(40, 40))
        self.slider_rect.centery = self.slider_base.centery

        if type(variable) is not list:
            raise ValueError("Variable argument must be a list with one element containing a variable\nThis is used "
                             "to create a pointer")
        elif len(variable) != 1:
            raise ValueError("Variable argument must be a list with one element containing a variable\nThis is used "
                             "to create a pointer")

        if direction.lower() == "v":
            self.direction = "v"
            self.set_slider_pos_to_value = self.vertical_set_slider_pos_to_value
            self.get_value = self.vertical_get_value

            if not size:
                self.slider_base.height = screen_h
            if not pos:
                self.slider_base.topright = screen_w, 0

            self.slider_rect.width = self.slider_base.width
            self.slider_rect.x = self.slider_base.x
        elif direction.lower() == "h":
            self.direction = "h"
            self.set_slider_pos_to_value = self.horizontal_set_slider_pos_to_value
            self.get_value = self.horizontal_get_value

            if not size:
                self.slider_base.width = screen_w
            if not pos:
                self.slider_base.bottomleft = 0, screen_h

            self.slider_rect.height = self.slider_base.height
            self.slider_rect.y = self.slider_base.y

        self.set_slider_pos_to_value()

        self.mouse_hover = False
        self.image_size = 0
        self.is_hidden = False

        self.is_held = False

        if click_sound:
            self.click_sound = click_sound
        elif hasattr(builtins, "click_sound"):
            self.click_sound = builtins.click_sound[0]
        else:
            self.click_sound = None

    def update(self, clicked=False):
        if self.is_hidden:
            return

        if clicked and self.slider_rect.collidepoint(pygame.mouse.get_pos()):
            self.is_held = True
        else:
            if not pygame.mouse.get_pressed()[0]:
                if self.is_held:
                    if self.click_sound:
                        self.click_sound.play()
                self.is_held = False

        if self.is_held:
            if self.direction == "h":
                self.slider_rect.centerx = pygame.mouse.get_pos()[0]

                self.slider_rect.left = max(self.slider_rect.left, self.slider_base.left)
                self.slider_rect.right = min(self.slider_rect.right, self.slider_base.right)
            else:
                self.slider_rect.centery = pygame.mouse.get_pos()[1]

                self.slider_rect.top = max(self.slider_rect.top, self.slider_base.top)
                self.slider_rect.bottom = min(self.slider_rect.bottom, self.slider_base.bottom)

        if hasattr(self.variable[0], "set"):
            self.variable[0].set(self.get_value())
        else:
            self.variable[0] = self.get_value()

    def draw(self):
        if self.is_hidden:
            return
        pygame.draw.rect(screen, (150, 255, 150), self.slider_base)
        pygame.draw.rect(screen, (250, 255, 250), self.slider_rect)

    def hide(self):
        self.is_hidden = True

    def show(self):
        self.is_hidden = False


if __name__ == "__main__":
    from pygame.locals import *
    fps = 60
    fpsClock = pygame.time.Clock()
    a = [0]
    old = a.copy()

    test = Slider(title="Громкость", value=1, variable=a,
                           position=get_proportion(width / 2 - 175, 700, l_h_pow=1.2),
                           show_percent=True, size=get_proportion(450, 150))
    while True:
        clicked = False
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True

        # Update.
        test.update(clicked)
        if a != old:
            old = a.copy()
            # print(a)

        # Draw.
        test.draw()

        pygame.display.flip()
        fpsClock.tick(fps)
