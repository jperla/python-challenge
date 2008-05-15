import os
import sys
import pygame
import spider

__VERSION__ = '1.0'
is_new_version_url = 'http://localhost/version.txt'

pygame.init()
pygame.font.init()

blue = (0, 0, 255)
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)

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
def blit_text(text,
              font=pygame.font.Font(None, 36),
              color=white,
              location=text_location):
    text_surface = font.render(text, 1, color)
    screen.blit(text_surface, location)

progress_bar_location = (text_location[0], text_location[1] + 50)
def blit_progress_bar(percentage,
                      location=progress_bar_location):
    #percentage happens to be exact number of pixels ! ;)
    border_size = 2
    progress_size = 100
    height = 20

    border = (location[0] - border_size, 
              location[1] - border_size,
              progress_size + border_size * 2,
              height + border_size * 2)
    pygame.draw.rect(screen, black, border)

    inside = (location[0], location[1], progress_size, height)
    pygame.draw.rect(screen, white, inside)

    progress = (location[0], location[1], percentage, height)
    pygame.draw.rect(screen, green, progress)


def is_version_up_to_date(version_a, version_b):
    #assumes they are floats
    return float(version_a) >= float(version_b)

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    screen.fill(blue)

    latest_version, new_version_url,_ = \
                                spider.get(is_new_version_url).split('\n')

    if is_version_up_to_date(__VERSION__, latest_version):
        progress = 100
        text = '%s%% - new: %s' % (progress , __VERSION__)
        blit_text(text)
        blit_image_to_display()
        blit_progress_bar(100)
    else:
        #update to the new version
        progress = 0
        text = '%s%% - old: %s' % (progress, __VERSION__)
        blit_progress_bar(0)
        blit_text(text)

    pygame.display.flip()


"""
GARBAGE TO Make it download more slowly:
"""
