import re
import os
import commands
import sys
import tempfile
import logging
import urllib2

from functools import partial

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
        #Yes, I know commands is old.  But this works right now
        #and I don't want to move this all to subprocess.
        logging.debug(commands.getoutput('tar xzvf %s' % temp_filename))
        logging.debug(commands.getoutput('mv %s %s' % (filename, 
                                            os.path.abspath(os.path.pardir))))
        #TODO: jperla: why need to remove when already moved???
        logging.debug(commands.getoutput('rm -rf %s' % filename))
        logging.debug(commands.getoutput('rm -f %s' % temp_filename))

        #wow THIS IS UGLY, there's got to be a better way!
        new_version_path = '%s' % (os.path.pardir+'/'+filename)
        logging.debug('evaluating %s' % new_version_path)

        sys.path.insert(0, new_version_path)
        from main import main_entry
        logging.debug('new version to boot into: %s' % main_entry.version)
        assert(float(main_entry.version) > float(self.version)) ##DEBUG:  

        new_update_succeeded = partial(self.update_succeeded, 
                                   os.getcwd(),
                                   os.path.abspath(os.path.pardir)+'/'+filename)
        new_update_failed = partial(self.update_failed, 
                                 os.path.abspath(os.path.pardir)+'/'+filename)
        main_entry.update_success = new_update_succeeded
        main_entry.update_failure = new_update_failed

        #TODO: jperla: run this in new thread?
        main_entry.run()

    def update_succeeded(self, cwd, newdir):
        logging.debug(commands.getoutput('rm -rf %s' % cwd))
        logging.debug('newdir %s' % newdir)
        os.chdir(newdir)
        del(self)

    def update_failed(self, newdir):
        logging.debug(commands.getoutput('rm -rf %s' % newdir))
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


