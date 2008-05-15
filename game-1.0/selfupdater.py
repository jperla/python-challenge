import os
import sys
import pygame

import spider
import downloadprogress


class SelfUpdater(object):
    def __init__(self, version, is_new_version_url):
        #can make these private later, with getters/setters if needed
        self.version = version
        self.is_new_version_url = is_new_version_url

__VERSION__ = '1.0'
is_new_version_url = 'http://localhost/version.txt'

blue = (0, 0, 255)
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)

size = (width, height) = (800, 600)
screen = pygame.display.set_mode(size)


downloading = False
progress = 50
text = 'gar'
everything_works = True


def get_image_to_display():
    image_to_display = pygame.image.load('ball.bmp')
    return image_to_display


image_location = (width / 5, height / 5)
def blit_image_to_display(image=get_image_to_display(),
                          location=image_location):
    screen.blit(image, location)



text_location = (width / 2, height / 2)
def blit_text(text,
              font=pygame.font.Font(None, 22),
              color=white,
              location=text_location):
    text_surface = font.render(text, 1, color)
    screen.blit(text_surface, location)

progress_bar_location = (text_location[0], text_location[1] + 50)
def blit_progress_bar(percentage,
                      location=progress_bar_location):
    #percentage happens to be exact number of pixels ! ;)
    progress_size = 100
    border_size = 2
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


def do_cool_stuff():
    blit_image_to_display()

def show_everything():
    global everything_works

    screen.fill(blue)
    blit_progress_bar(progress)
    blit_text(text)
    if everything_works:
        do_cool_stuff()
    pygame.display.flip()
    

def watch_progress(total_to_download, 
                   total_downloaded,
                   total_to_upload,
                   total_uploaded):
    global progress, text
    print total_downloaded #DEBUG: jperla: 
    if total_to_download == 0 or total_to_download == 0.0:
        progress = 0
    else:
        progress = int(float(total_downloaded) / total_to_download * 100.0)
    text = '%s%% - downloading... - old: %s' % (progress, __VERSION__)
    show_everything()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    latest_version, new_version_url,_ = \
                                spider.get(is_new_version_url).split('\n')

    if is_version_up_to_date(__VERSION__, latest_version):
        progress = 100
        text = '%s%% - new: %s' % (progress , __VERSION__)
        evyerthing_works = True
        show_everything()
    else:
        everything_wokrs = False
        progress = 0
        text = 'Old version. Updating to new version: %s' % latest_version
        show_everything()
        #update to the new version
        if not downloading:
            downloading = True
            temp_file_location = 'temp.tar.gz'
            downloadprogress.download_with_progress(new_version_url,
                                                    temp_file_location,
                                                    watch_progress)
            downloading = False

"""
GARBAGE TO Make it download more slowly:
"""
