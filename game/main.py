import logging
import pygame
import selfupdater

class GameSelfUpdater(selfupdater.SelfUpdater):
    pygame.init()
    pygame.font.init()

    def __init__(self):
        version = '1.0'
        is_new_version_url = 'http://localhost/version.txt'
        selfupdater.SelfUpdater.__init__(self, version, is_new_version_url)
        self.progress = 0
        self.text = 'initial progress bar text'

        #these would obviously be broken out into a utility library,
        #not be class methods
        self.blue = (0, 0, 255)
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.green = (0, 255, 0)

        self.size = (self.width, self.height) = (800, 480)
        self.screen = pygame.display.set_mode(self.size)

    def run_implementation(self):
        while True:
            logging.debug('version: %s' % self.version) #DEBUG: jperla: 
            if self.up_to_date:
                self.progress = 100
                self.text = 'new: %s' % (self.version)
            try:
                self.update_if_newer_version()
            except Exception, e:
                logging.error('Exception: %s' % e)
                self.text = 'Failed: could not update version'

            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()

            self.show_everything()

            self.executes_properly()
    
    def do_while_downloading(self, total_to_download, total_downloaded):
        percent = self._percentage_progress(total_to_download, total_downloaded)
        self.progress = int(percent)
        self.text = '%s%% - downloading... - old: %s' % (self.progress, 
                                                         self.version)
        self.show_everything()

    def get_image_to_display():
        image_to_display = pygame.image.load('ball.bmp')
        return image_to_display


    def blit_image_to_display(self, image=get_image_to_display()):
        self.screen.blit(image, (self.width / 5, self.height / 5))



    def blit_text(self, text, font=pygame.font.Font(None, 22)):
        color=self.white
        text_surface = font.render(text, 1, color)
        self.screen.blit(text_surface, (self.width / 2, self.height / 2))

    def blit_progress_bar(self, percentage):
        progress_bar_location = (self.width / 2, self.height / 2 + 50)
        location=progress_bar_location

        #percentage happens to be exact number of pixels ! ;)
        progress_size = 100
        border_size = 2
        height = 20

        border = (location[0] - border_size, 
                location[1] - border_size,
                progress_size + border_size * 2,
                height + border_size * 2)
        pygame.draw.rect(self.screen, self.black, border)

        inside = (location[0], location[1], progress_size, height)
        pygame.draw.rect(self.screen, self.white, inside)

        progress = (location[0], location[1], percentage, height)
        pygame.draw.rect(self.screen, self.green, progress)


    def do_cool_stuff(self):
        self.blit_image_to_display()

    def show_everything(self):
        self.screen.fill(self.blue)
        self.blit_progress_bar(self.progress)
        self.blit_text(self.text)
        if self.up_to_date:
            self.do_cool_stuff()
        pygame.display.flip()

logging.basicConfig(level=logging.DEBUG)

# This is where the selfupdater looks to find thew new version of the
# program to bootstrap into
# Maybe this should be __init__.py instead of main.py?

main_entry = GameSelfUpdater()

if __name__ == '__main__':
    main_entry.run()

