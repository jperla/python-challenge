import sys
import pygame

__VERSION__ = '1.0'

pygame.init()
pygame.font.init()

blue = (0, 0, 255)
white = (255, 255, 255)

size = (width, height) = (800, 600)
screen = pygame.display.set_mode(size)

def get_image_to_display():
    image_to_display = pygame.image.load('ball.bmp')
    return image_to_display


image_location = (width / 5, height / 5)
def blit_image_to_display(image=get_image_to_display(),
                          location=image_location):
    screen.blit(image, location)


text_location = (width / 2, height / 2)
def blit_text_to_display(text='text' + __VERSION__,
                         font=pygame.font.Font(None, 36),
                         color=white,
                         location=text_location):
    text_surface = font.render(text, 1, color)
    screen.blit(text_surface, location)

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    screen.fill(blue)

    blit_image_to_display()
    blit_text_to_display()

    pygame.display.flip()

