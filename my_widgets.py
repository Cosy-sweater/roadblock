# my widgets v1.1
import pygame
import builtins

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
    def set_slider_pos_to_value(self):
        self.slider_rect.centerx = self.slider_base.left + self.slider_base.width / \
                                   (self.value_range[1] - self.value_range[0]) * self.value

    def __init__(self, position: tuple = (0, 0), size=(450, 150), variable=None, value_range: tuple = (0, 1),
                 click_sound=None, title: str = "", value=0):
        self.value = value
        self.value_range = value_range
        self.variable = variable

        if type(variable) is not list:
            raise ValueError("Variable argument must be a list with one element containing a variable\nThis is used "
                             "to create a pointer")
        if len(variable) != 1:
            raise ValueError("Variable argument must be a list with one element containing a variable\nThis is used "
                             "to create a pointer")

        self.rect = pygame.Rect(position, size)
        self.slider_base = pygame.Rect((0, 0), (size[0] - 50, get_proportion(h=25)[1]))
        self.slider_base.centerx = self.rect.centerx
        self.slider_base.top = self.rect.centery + get_proportion(h=10)[1]
        self.slider_rect = pygame.Rect((0, 0), get_proportion(40, 40, square="h"))
        self.slider_rect.centery = self.slider_base.centery
        self.set_slider_pos_to_value()

        self.title = title
        self.mouse_hover = False
        self.image_size = 0
        self.is_hidden = False

        self.is_held = False

        if click_sound:
            self.click_sound = click_sound[0]
        elif hasattr(builtins, "click_sound"):
            self.click_sound = builtins.click_sound[0]
        else:
            self.click_sound = None

        if self.title:
            self.title = font1.render(self.title, False, (0, 0, 0))

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
            self.slider_rect.centerx = pygame.mouse.get_pos()[0]
        self.slider_rect.centerx = max(self.slider_rect.centerx, self.slider_base.left)
        self.slider_rect.centerx = min(self.slider_rect.centerx, self.slider_base.right)

        self.variable[0].set(self.get_value())

    def draw(self):
        if self.is_hidden:
            return
        pygame.draw.rect(screen, (50, 255, 50), self.rect)
        pygame.draw.rect(screen, (150, 255, 150), self.slider_base)
        pygame.draw.rect(screen, (250, 255, 250), self.slider_rect)
        pos = self.title.get_rect()
        pos.centerx = self.rect.centerx
        pos.top = self.rect.top + 15
        screen.blit(self.title, pos)

    def hide(self):
        self.is_hidden = True

    def show(self):
        self.is_hidden = False

    def get_value(self):
        return round(max(self.slider_rect.centerx - self.slider_base.left, 0.001) /
                     self.slider_base.width *
                     (self.value_range[1] - self.value_range[0]) + self.value_range[0], 3)
