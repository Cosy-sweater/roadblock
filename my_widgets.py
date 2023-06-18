# my widgets v1.0
import pygame

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

width, height = 1920, 1080
font1 = pygame.font.SysFont('Comic Sans MS', int(30 * screen.get_width() / width))
font2 = pygame.font.SysFont('Comic Sans MS', int(24 * screen.get_width() / width))
screen_w, screen_h = screen.get_size()


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

    def update(self, clicked=True):
        if self.is_hidden or self.is_locked:
            return
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if not clicked:
                pass
            else:
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


def InOutEase(step: float, last_value: int):
    # 0.02 => 100
    from math import cos, pi
    t = 0
    while t < 2:
        t += step
        yield round(-(cos(pi * t) - 1) / 2 * last_value, 1)


def OutEase(step: float, last_value: int):
    from math import sin, pi
    t = 0
    c = 0
    while c < 1:
        t += step
        c = sin(t * pi / 2)
        yield c


# import time
# a = InOutEase(0.02, 500)
# while True:
#     print(next(a))
#     time.sleep(0.1)
