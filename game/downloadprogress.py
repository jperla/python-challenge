import tempfile
import spider
import pycurl

def _progress_example(download_t, download_d, upload_t, upload_d):
    print "Total to download", download_t
    print "Total downloaded", download_d

def download_with_progress(url, filename, progress_callback=None):
    c = pycurl.Curl()
    fp = open(filename, 'w')
    c.setopt(c.URL, url)
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.setopt(c.NOPROGRESS, 0)
    if progress_callback is not None:
        c.setopt(c.PROGRESSFUNCTION, progress_callback)
    c.setopt(pycurl.WRITEDATA, fp)
    c.perform()


#TODO: jperla: test this
