import re
import os
import commands
import sys
import tempfile
import logging
import urllib2

import pygame

from functools import partial

import pygame

import spider
import downloadprogress


class SelfUpdater(object):
    def __init__(self, 
                 version, 
                 is_new_version_url, 
                 update_success=None,
                 update_failure=None):
        #can make these private later, with getters/setters if needed
        self.version = version
        self.is_new_version_url = is_new_version_url
        self.up_to_date = True
        self.download_progress = None
        self.update_success = update_success
        self.update_failure = update_failure

    def run_implementation(self):
        #implement this in sublcasses
        #possibly raise error?
        while True:
            self.update_if_newer_version()
            #went through a whole iteration just fine, it executes fine
            self.executes_properly()

    def do_while_downloading(self, total_to_download, total_downloaded):
        #implement this in sublcasses
        #possibly raise error?
        pass

    def run(self):
        try:
            self.run_implementation()
            #the run should be a while loop, so it must have executed improperly
            self.executes_improperly(Exception('stopped running main'))
        except Exception, e:
            self.executes_improperly(e)

    def executes_properly(self):
        if self.update_success is not None:
            self.update_success()
            self.update_success = None
            self.update_failure = None
            
    def executes_improperly(self, error=None):
        logging.error('Error-improperly run: %s' % error)
        if self.update_failure is not None:
            self.update_failure()
        else:
            raise Exception('Executed improperly somehow', error)

    def update_if_newer_version(self):
        latest_version, latest_version_url,_ = \
                                spider.get(self.is_new_version_url).split('\n')
        if self.__is_newer_version(latest_version):
            self.up_to_date = False
            self.update_to_latest_version_given_url(latest_version_url)

    def update_to_latest_version_given_url(self, latest_version_url):
        #Assumes update is always a .tar.gz
        assert(latest_version_url.endswith('.tar.gz'))

        #get the file name in the url
        filename = self.__get_filename_in_url(latest_version_url)

        #I know this is insecure.  A tedious to solve implementation detail.
        temp_filename = tempfile.mktemp('--%s.tar.gz' % filename)
        self.download_progress = 0
        downloadprogress.download_with_progress(latest_version_url,
                                                temp_filename,
                                                self.__watch_progress)
        self.update_to_latest_version_given_filename(temp_filename)

    def update_to_latest_version_given_filename(self, temp_filename):
        filename = self.__get_filename_in_temp_path(temp_filename)

        #assumes we want to put the tarfile in parent of current directory
        logging.debug(commands.getoutput('tar xzvf %s' % temp_filename))
        logging.debug(commands.getoutput('mv %s %s' % (filename, 
                                            os.path.abspath(os.path.pardir))))
        #TODO: jperla: why need to remove when already moved???
        logging.debug(commands.getoutput('rm -rf %s' % filename))
        logging.debug(commands.getoutput('rm -f %s' % temp_filename))

        #wow that's ugly, there's got to be a better way!
        file_to_evaluate = '%s' % (os.path.pardir+'/'+filename)
        logging.debug('evaluating %s' % file_to_evaluate)

        sys.path.insert(0, file_to_evaluate)
        #TODO: jperla: fix this terminology
        from selfupdater import selfupdater
        #TODO: jperla: i can't believe that this worked!

        new_update_succeeded = partial(self.update_succeeded, 
                                   os.getcwd(),
                                   os.path.abspath(os.path.pardir)+'/'+filename)
        new_update_failed = partial(self.update_failed, 
                                 os.path.abspath(os.path.pardir)+'/'+filename)
        selfupdater.update_success = new_update_succeeded
        selfupdater.update_failure = new_update_failed

        #TODO: jperla: run this in new thread?
        selfupdater.run()

    def update_succeeded(self, cwd, newdir):
        #TODO: jperla: make it actually remove
        logging.debug('remove %s' % cwd)
        logging.debug('newdir %s' % newdir)
        os.chdir(newdir)
        del(self)

    def update_failed(self, newdir):
        logging.debug('remove %s' % newdir)
        #continue since the other thing stopped

    def __get_filename_in_temp_path(self, path):
        """
        Turns '/tmp/SD234S--selfupdater-2.0.tar.gz' 
                into 'selfupdater-2.0'
        """
        filename = re.match(r'.*?--(.*)\.tar\.gz$', path).group(1)
        return filename

    def __get_filename_in_url(self, url):
        """
        Turns 'http://bla.com/foo/bar/selfupdater-2.0.tar.gz' 
            into 'selfupdater-2.0'
        """
        seek = urllib2.urlparse.urlparse(url)[2]
        filename = re.match(r'.*?([a-zA-Z0-9\-\.]*)\.tar\.gz$', seek).group(1)
        return filename

    def __is_newer_version(self, version_b):
        # Assumes version numbers are floats.
        # In real life, this is more complicated (i.e. v1.2.3),
        # but actually writing that out is boring
        return float(self.version) < float(version_b)

    def _percentage_progress(self, total_to_download, total_downloaded):
        if total_to_download == 0 or total_to_download == 0.0:
            progress = 0
        else:
            progress = float(total_downloaded) / total_to_download * 100.0
        return progress

    def __watch_progress(self, 
                         total_to_download, 
                         total_downloaded,
                         total_to_upload,
                         total_uploaded):
        self.do_while_downloading(total_to_download, total_downloaded)


class SimpleSelfUpdater(SelfUpdater):
    def __init__(self):
        version = '1.0'
        is_new_version_url = 'http://localhost/version_test.txt'
        SelfUpdater.__init__(self, version, is_new_version_url)

    def run_implementation(self):
        while True:
            try:
                self.update_if_newer_version()
            except Exception, e:
                logging.error('Exception: %s' % e)
            self.executes_properly()
    
    def do_while_downloading(self, total_to_download, total_downloaded):
        pass #self._percentage_progress(total_to_download, total_downloaded)




class GameSelfUpdater(SelfUpdater):
    pygame.init()
    pygame.font.init()

    downloading = False
    everything_works = True

    def __init__(self):
        version = '1.0'
        is_new_version_url = 'http://localhost/version.txt'
        SelfUpdater.__init__(self, version, is_new_version_url)
        self.progress = 0
        self.text = 'gar'

        self.blue = (0, 0, 255)
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.green = (0, 255, 0)


        self.size = (self.width, self.height) = (800, 480)
        self.screen = pygame.display.set_mode(self.size)

    def run_implementation(self):
        while True:
            print self.version #DEBUG: jperla: 
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
        #print self.progress #DEBUG: jperla: 
        self.text = '%s%% - downloading... - old: %s' % (self.progress, 
                                                         self.version)
        self.show_everything()

    def get_image_to_display():
        image_to_display = pygame.image.load('ball.bmp')
        return image_to_display


    def blit_image_to_display(self,
                              image=get_image_to_display(),
                              ):
        self.screen.blit(image, (self.width / 5, self.height / 5))



    def blit_text(self,
                  text,
                  font=pygame.font.Font(None, 22),
                  ):
        color=self.white
        text_surface = font.render(text, 1, color)
        self.screen.blit(text_surface, (self.width / 2, self.height / 2))

    def blit_progress_bar(self, 
                          percentage,
                          ):
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




selfupdater = GameSelfUpdater()
#selfupdater.run()

if __name__ == '__main__':
    selfupdater.run()

