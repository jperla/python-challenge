# coding=utf-8
import logging

import os
import re
import urllib
import urllib2
import cookielib

import BeautifulSoup

import futures

import waiter

#session object 
class Session(object):
    def __init__(self):
        self._cookie_jar = cookielib.CookieJar()

    @property
    def cookie_processor(self):
        return urllib2.HTTPCookieProcessor( self._cookie_jar)

DEFAULT_USER_AGENT = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.4)  Gecko/20061201 Firefox/2.0.0.4 (Ubuntu-feisty)'

default_session = Session()

waiter = waiter.Waiter()
            
def _create_opener(session=default_session):
    if session is None:
        return urllib2.build_opener()
    else:
        return urllib2.build_opener(session.cookie_processor)

def _create_request(url, data):
    if data is None:
        request = urllib2.Request(url)
    else:
        request = urllib2.Request(url, urllib.urlencode(data))
    request.add_header('User-Agent', DEFAULT_USER_AGENT)
    return request

def get(url, data=None, session=default_session):
    """
    >>> html = get('http://www.google.com/')
    >>> html.startswith('<html><head>')
    True
    """
    request = _create_request(url, data)
    opener = _create_opener(session)
    html = None
    try: 
        return opener.open(request).read()
    except:
        #try once again
        try:
            return opener.open(request).read()
        except Exception, e:
            raise Exception('Could not open page, tried twice: %s' % url, e)

def get_in_parallel(urls):
    """
    >>> urls = ['http://www.google.com/', 'http://www.yahoo.com/']
    >>> htmls = get_in_parallel(urls)
    >>> print htmls[0][:12] #easier to debug when printing
    <html><head>
    >>> print htmls[1][:20]
    <!DOCTYPE HTML PUBLI
    """
    # pull down all feeds
    future_calls = [futures.Future(get, url) for url in urls]
    # block until they are all in
    # log all errors, but do not break
    htmls = []
    for future_obj in future_calls:
        try:
            page = future_obj()
            htmls.append(page)
        except Exception, e:
            logging.error(str(e))
    return htmls

def get_matches(html, regex):
    """
    >>> html = '<html><head></head><body>This is a test html.</body></head>'
    >>> print get_matches(html, '<(.*?)>')
    ['html', 'head', '/head', 'body', '/body', '/head']
    """
    p = re.compile(regex, re.M | re.S)
    return p.findall(html)

def get_match(html, regex):
    """
    >>> html = '<html><head></head><body>This is a test html.</body></head>'
    >>> print get_match(html, ' is(.*)test')
     a 
    >>> print get_match(html, 'ody>(.*)</bod')
    This is a test html.
    >>> print get_match(html, 'Th(.*?)s')
    i
    >>> print get_match(html, 'Th(.*)s')
    is is a te
    """
    matches = get_matches(html, regex)
    return matches[0] if len(matches) > 0 else None

def finds_match(html, regex):
    """
    >>> html = '<html><head></head><body>This is a test html.</body></head>'
    >>> print finds_match(html, ' is(.*)test')
    True
    >>> print finds_match(html, 'ody>(.*)</bod')
    True
    >>> print finds_match(html, 'nothing')
    False
    >>> print finds_match(html, 'That')
    False
    """
    matches = get_matches(html, regex)
    if len(matches) == 0:
        return False
    else:
        return True

def get_matches_in_url(url, regex, session=default_session):
    html = get(url)
    return get_matches(html, regex)

def get_match_in_url(url, regex, session=default_session):
    html = get(url)
    return get_match(html, regex)

def extract_links(html):
    """
    >>> html = '<a href="go">hey</a><br href="not" /><a href="w"></a>'
    >>> links = [str(link) for link in extract_links(html)] #unicode -> str
    >>> links
    ['go', 'w']
    >>> h = '<a href="javascript:poptastic(\\'event.php?eventID=922\\')"></a>'
    >>> l = [str(link) for link in extract_links(h)] #unicode -> str
    >>> l
    ['event.php?eventID=922']
    >>> h = "<a href='javascript:poptastic(\\"event.php?eventID=922\\")'></a>"
    >>> l = [str(link) for link in extract_links(h)] #unicode -> str
    >>> l #also works for double-quoted javascript
    ['event.php?eventID=922']
    >>> html = '<a name="bla" id="q">hello anchor</a>'
    >>> links = extract_links(html)
    >>> links
    []
    """
    a = BeautifulSoup.SoupStrainer('a')
    links = BeautifulSoup.BeautifulSoup(html, parseOnlyThese=a)
    hrefs = [link['href'] for link in links if link.has_key('href')]

    #also extract javascript popup shit
    def extract_js(link):
        if link.lower().startswith('javascript'):
            return get_match(link, r"\([\'\"](.*)[\'\"]\)")
        else:
            return link
    hrefs = [extract_js(href) for href in hrefs]

    return hrefs

def parse_domain(url):
    """
    >>> url = 'http://www.google.com/a/href/asdf/?id=3#cool'
    >>> print parse_domain(url)
    http://www.google.com
    """
    url = list(urllib2.urlparse.urlparse(url)[0:2]) + ['','','','']
    return urllib2.urlparse.urlunparse(url)

def absolute_from_relative(url, link):
    """
    >>> url = 'http://www.google.com/a/href/asdf/?id=3#cool'
    >>> link = '/relative/url/3?id=4#rocking'
    >>> print absolute_from_relative(url, link)
    http://www.google.com/relative/url/3?id=4#rocking
    >>> url = 'http://www.google.com/a/href/asdf?id=3#cool'
    >>> link = 'relative?id=4#rocking'
    >>> print absolute_from_relative(url, link)
    http://www.google.com/a/href/relative?id=4#rocking
    >>> url = 'http://www.google.com/a/href/asdf?id=3#cool'
    >>> link = '../relative?id=4#rocking'
    >>> print absolute_from_relative(url, link)
    http://www.google.com/a/relative?id=4#rocking
    """
    path = urllib2.urlparse.urlparse(url)[2]
    url = list(urllib2.urlparse.urlparse(parse_domain(url)))
    url[2] = path
    link_parsed = urllib2.urlparse.urlparse(link)

    if link_parsed[2].startswith('/'):
        url[2] = link_parsed[2] #path
    elif link_parsed[2].startswith('../'):
        without_dots = link_parsed[2][3:]
        #keep parts of same path, starting from parent
        url[2] = get_match(url[2], r'^(.*?/?)[^/]*/[^/]*$') + without_dots
    else:
        #keep parts of same path
        url[2] = get_match(url[2], r'^(.*?/?)[^/]*$') + link_parsed[2]

    url[4] = link_parsed[4] #args
    url[5] = link_parsed[5] #anchor
    return urllib2.urlparse.urlunparse(tuple(url))


def clean_html_entities(html):
    #http://www.asciitable.com/
    #http://www.w3schools.com/tags/ref_entities.asp

    # ISO 8859-1 Character Entities
    char_maps = {
        'À' : "&Agrave;", 'Á' : "&Aacute;", 'Â' : "&Acirc;", 
        'Ã' : "&Atilde;", 'Ä' : "&Auml;", 'Å' : "&Aring;",
        'Æ' : "&AElig;", 'Ç' : "&Ccedil;",
        'È' : "&Egrave;", 'É' : "&Eacute;", 'Ê' : "&Ecirc;", 'Ë' : "&Euml;",
        'Ì' : "&Igrave;", 'Í' : "&Iacute;", 'Î' : "&Icirc;", 'Ï' : "&Iuml;",
        'Ð' : "&ETH;", 'Ñ' : "&Ntilde;",
        'Ò' : "&Ograve;", 'Ó' : "&Oacute;", 'Ô' : "&Ocirc;", 
        'Õ' : "&Otilde;", 'Ö' : "&Ouml;", 'Ø' : "&Oslash;",
        'Ù' : "&Ugrave;", 'Ú' : "&Uacute;", 'Û' : "&Ucirc;", 'Ü' : "&Uuml;",
        'Ý' : "&Yacute;",
        'Þ' : "&THORN;", 'ß' : "&szlig;",
        'à' : "&agrave;", 'á' : "&aacute;", 'â' : "&acirc;", 
        'ã' : "&atilde;", 'ä' : "&auml;", 'å' : "&aring;",
        'æ' : "&aelig;", 'ç' : "&ccedil;",
        'è' : "&egrave;", 'é' : "&eacute;", 'ê' : "&ecirc;", 'ë' : "&euml;",
        'ì' : "&igrave;", 'í' : "&iacute;", 'î' : "&icirc;", 'ï' : "&iuml;",
        'ð' : "&eth;", 'ñ' : "&ntilde;",
        'ò' : "&ograve;", 'ó' : "&oacute;", 'ô' : "&ocirc;", 
        'õ' : "&otilde;", 'ö' : "&ouml;", 'ø' : "&oslash;",
        'ù' : "&ugrave;", 'ú' : "&uacute;", 'û' : "&ucirc;", 'ü' : "&uuml;",
        'ý' : "&yacute;", 'þ' : "&thorn;", 'ÿ' : "&yuml;", 
        '&' : '&amp;', "'" : '&#039;', '"' : '&quot;', };

    for char in char_maps.keys():
        html = html.replace(char_maps[char], char)
    return html

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
