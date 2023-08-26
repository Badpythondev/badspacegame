# classes.py
import pygame

class Button:
    def __init__(self, image, x, y, scale):
        self.x, self.y = x, y
        self.scale = scale
        self.image = image
        self.rect = image.get_rect()
        self.rect.topleft = (x, y)
        self.pressed = False
        self.height,self.width=image.get_width(),image.get_width()

    def draw(self, surface):
        pos=pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0]and not self.pressed:
                self.pressed=True
        if pygame.mouse.get_pressed()[0]==0:
            self.pressed=False
        scaled_image = pygame.transform.scale(self.image, (int(self.image.get_width() * self.scale), int(self.image.get_height() * self.scale)))
        surface.blit(scaled_image, (self.x, self.y))
