import os
import sys
import pygame
import tempfile

import spider
import downloadprogress


class SelfUpdater(object):
    def __init__(self, version, is_new_version_url):
        #can make these private later, with getters/setters if needed
        self.version = version
        self.is_new_version_url = is_new_version_url
        self.up_to_date = True
        self.download_progress = None

    def run():
        #implement this in sublcasses
        #possibly raise error?
        while True:
            update_if_newer_version()

    def do_while_downloading(self, total_to_download, total_downloaded):
        #implement this in sublcasses
        #possibly raise error?
        pass

    def update_if_newer_version():
        latest_version, latest_version_url,_ = \
                                spider.get(is_new_version_url).split('\n')
        if self.is_newer_version(latest_version):
            self.up_to_date = false
            self.update_to_latest_version(latest_version_url)
        else:
            pass

    def update_to_latest_version_given_url(self, latest_version_url):
        #Assumes update is always a .tar.gz
        assert(latest_version_url.endswith('tar.gz'))
        #I know this is insecure.  A tedious to solve implementation detail.
        temp_filename = tempfile.mktemp('tar.gz')
        self.download_progress = 0
        downloadprogress.download_with_progress(latest_version_url,
                                                temp_filename,
                                                self.__watch_progress)
        self.update_to_latest_version_given_filename(temp_filename)

    def update_to_latest_version_given_filename(filename):
        #TODO: jperla: finish this!
        self.up_to_date = True
        self.download_progress = None
        self.version = '2.0'

    def is_newer_version(self, version_b):
        # Assumes version numbers are floats.
        # In real life, this is more complicated (i.e. v1.2.3),
        # but actually writing that out is boring
        return float(self.version) >= float(version_b)

    def _percentage_progress(self, total_to_download, total_downloaded):
        if total_to_download == 0 or total_to_download == 0.0:
            progress = 0
        else:
            progress = float(total_downloaded) / total_to_download * 100.0
        return progress

    def __watch_progress(total_to_download, 
                         total_downloaded,
                         total_to_upload,
                         total_uploaded):
        self.do_while_downloading(total_to_download, total_downloaded)


class SimpleSelfUpdater(SelfUpdater):
    def __init__(self, version, is_new_version_url):
        SelfUpdater.__init__(self, version, is_new_version_url)

    def run():
        while True:
            print self.version
            update_if_newer_version()
    
    def do_while_downloading(self, total_to_download, total_downloaded):
        print self._percentage_progress(total_to_download, total_downloaded)

__VERSION__ = '1.0'
is_new_version_url = 'http://localhost/version_test.txt'

updater = SimpleSelfUpdater(__VERSION__, is_new_version_url)

"""
GARBAGE TO Make it download more slowly:
"""
