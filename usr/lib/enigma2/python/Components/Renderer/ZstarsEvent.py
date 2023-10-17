#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng
# v1 07.2020, 11.2021
# for channellist
# <widget source="ServiceEvent" render="ZstarsEvent" position="750,390" size="200,20" alphatest="blend" transparent="1" zPosition="3" />
# or
# <widget source="ServiceEvent" render="ZstarsEvent" pixmap="xtra/star.png" position="750,390" size="200,20" alphatest="blend" transparent="1" zPosition="3" />
# edit lululla 05-2022
# <ePixmap pixmap="MetriXconfluencExp/star.png" position="136,104" size="200,20" alphatest="blend" zPosition="10" transparent="1" />
# <widget source="session.Event_Now" render="ZstarsEvent" pixmap="MetriXconfluencExp/star.png" position="560,367" size="200,20" alphatest="blend" transparent="1" zPosition="3" />
# <ePixmap pixmap="MetriXconfluencExp/star.png" position="136,104" size="200,20" alphatest="blend" zPosition="10" transparent="1" />
# <widget source="session.Event_Next" render="ZstarsEvent" pixmap="MetriXconfluencExp/star.png" position="560,367" size="200,20" alphatest="blend" transparent="1" zPosition="3" />

from __future__ import absolute_import
from Components.Renderer.Renderer import Renderer
from Components.VariableValue import VariableValue
from enigma import eSlider
from Components.config import config
from enigma import eTimer
import re
import json
import os
import socket
import sys


global cur_skin, my_cur_skin, tmdb_api
PY3 = (sys.version_info[0] == 3)
if PY3:
    PY3 = True
    unicode = str
    from urllib.error import URLError, HTTPError
    from urllib.request import urlopen
    from urllib.parse import quote
else:
    str = unicode
    from urllib2 import URLError, HTTPError
    from urllib2 import urlopen
    from urllib import quote


formatImg = 'w185'
tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
omdb_api = "cb1d9f55"
thetvdbkey = 'D19315B88B2DE21F'
# thetvdbkey = "a99d487bb3426e5f3a60dea6d3d3c7ef"
my_cur_skin = False
cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')


def isMountReadonly(mnt):
    mount_point = ''
    with open('/proc/mounts') as f:
        for line in f:
            line = line.split(',')[0]
            line = line.split()
            print('line ', line)
            try:
                device, mount_point, filesystem, flags = line
            except Exception as err:
                print("Error: %s" % err)
            if mount_point == mnt:
                return 'ro' in flags
    return "mount: '%s' doesn't exist" % mnt


path_folder = "/tmp/poster/"
if os.path.exists("/media/hdd"):
    if not isMountReadonly("/media/hdd"):
        path_folder = "/media/hdd/poster/"
elif os.path.exists("/media/usb"):
    if not isMountReadonly("/media/usb"):
        path_folder = "/media/usb/poster/"
elif os.path.exists("/media/mmc"):
    if not isMountReadonly("/media/mmc"):
        path_folder = "/media/mmc/poster/"

if not os.path.exists(path_folder):
    os.makedirs(path_folder)


try:
    from Components.config import config
    lng = config.osd.language.value
    lng = lng[:-3]
except:
    lng = 'en'
    pass
print('language: ', lng)


REGEX = re.compile(
        r'([\(\[]).*?([\)\]])|'
        r'(: odc.\d+)|'
        r'(\d+: odc.\d+)|'
        r'(\d+ odc.\d+)|(:)|'
        r'( -(.*?).*)|(,)|'
        r'!|'
        r'/.*|'
        r'\|\s[0-9]+\+|'
        r'[0-9]+\+|'
        r'\s\d{4}\Z|'
        r'([\(\[\|].*?[\)\]\|])|'
        r'(\"|\"\.|\"\,|\.)\s.+|'
        r'\"|:|'
        r'Премьера\.\s|'
        r'(х|Х|м|М|т|Т|д|Д)/ф\s|'
        r'(х|Х|м|М|т|Т|д|Д)/с\s|'
        r'\s(с|С)(езон|ерия|-н|-я)\s.+|'
        r'\s\d{1,3}\s(ч|ч\.|с\.|с)\s.+|'
        r'\.\s\d{1,3}\s(ч|ч\.|с\.|с)\s.+|'
        r'\s(ч|ч\.|с\.|с)\s\d{1,3}.+|'
        r'\d{1,3}(-я|-й|\sс-н).+|', re.DOTALL)


def intCheck():
    try:
        response = urlopen("http://google.com", None, 5)
        response.close()
    except HTTPError:
        return False
    except URLError:
        return False
    except socket.timeout:
        return False
    else:
        return True


def unicodify(s, encoding='utf-8', norm=None):
    if not isinstance(s, unicode):
        s = unicode(s, encoding)
    if norm:
        from unicodedata import normalize
        s = normalize(norm, s)
    return s


def cleantitle(text=''):
    try:
        print('ZstarsEvent text ->>> ', text)
        if text != '' or text is not None or text != 'None':
            text = REGEX.sub('', text)
            text = re.sub(r"[-,?!/\.\":]", '', text)  # replace (- or , or ! or / or . or " or :) by space
            text = re.sub(r'\s{1,}', ' ', text)  # replace multiple space by one space
            text = unicodify(text)
            text = text.lower()
            print('ZstarsEvent text <<<- ', text)
        else:
            text = str(text)
            print('ZstarsEvent text <<<->>> ', text)
        return text
    except Exception as e:
        print('cleantitle error: ', e)
        pass


class ZstarsEvent(VariableValue, Renderer):

    def __init__(self):
        adsl = intCheck()
        if not adsl:
            return
        Renderer.__init__(self)
        VariableValue.__init__(self)
        self.timer30 = eTimer()
        self.__start = 0
        self.__end = 100
        self.text = ''

    GUI_WIDGET = eSlider

    def changed(self, what):
        if not self.instance:
            print('zstar event not istance')
            return
        if what[0] == self.CHANGED_CLEAR:
            print('zstar event A what[0] == self.CHANGED_CLEAR')
            (self.range, self.value) = ((0, 1), 0)
            return
        if what[0] != self.CHANGED_CLEAR:
            print('zstar event B what[0] != self.CHANGED_CLEAR')
            self.instance.hide()
            try:
                self.timer30.callback.append(self.infos)
            except:
                self.timer30_conn = self.timer30.timeout.connect(self.infos)
            self.timer30.start(100, True)

    def infos(self):
        try:
            rtng = 0
            range = 0
            value = 0
            ImdbRating = "0"
            ids = ''
            self.event = self.source.event
            if self.event:  # and self.instance:
                self.evnt = self.event.getEventName().encode('utf-8')
                self.evntNm = cleantitle(self.evnt)
                print('clean zstar: ', self.evntNm)

                if not os.path.exists("%s%s" % (path_folder, self.evntNm)):
                    import requests
                    try:
                        url = 'http://api.themoviedb.org/3/search/movie?api_key={}&query={}'.format(str(tmdb_api), quote(self.evntNm))
                        if PY3:
                            url = url.encode()
                        print('url1:', url)
                        # Title = requests.get(url).json()['results'][0]['original_title']
                        ids = requests.get(url).json()['results'][0]['id']
                        # print('url1 ids:', ids)
                    except:
                        try:
                            url = 'http://api.themoviedb.org/3/search/multi?api_key={}&query={}'.format(str(tmdb_api), quote(self.evntNm))
                            if PY3:
                                url = url.encode()
                            # print('url2:', url)
                            ids = requests.get(url).json()['results'][0]['id']
                            # print('url2 ids:', ids)
                        except Exception as e:
                            print('no ids in zstar', e)

                    if ids != '':
                        try:
                            url3 = 'https://api.themoviedb.org/3/movie/{}?api_key={}&append_to_response=credits'.format(str(ids), str(tmdb_api))

                            data2 = requests.get(url3, timeout=10)
                            with open(("%s%s" % (path_folder, self.evntNm)), "w") as f:
                                json.dump(data2.json(), f)
                        except Exception as e:
                            print('pass: ', e)


                myFile = open(("%s%s" % (path_folder, self.evntNm)), 'r')
                myObject = myFile.read()
                u = myObject.decode('utf-8-sig')
                data = u.encode('utf-8')
                # data.encoding
                # data.close()
                data = json.loads(myObject, 'utf-8')
                if "vote_average" in data:
                    ImdbRating = data['vote_average']
                    print('ImdbRating vote average', ImdbRating)
                elif "imdbRating" in data:
                    print('ok vote imdbRating')
                    ImdbRating = data['imdbRating']
                else:
                    print('no vote starx')
                    ImdbRating = '0'
                print('ImdbRating: ', ImdbRating)
                if ImdbRating and ImdbRating != '0':
                    rtng = int(10 * (float(ImdbRating)))
                else:
                    rtng = 0
                range = 100
                value = rtng
                (self.range, self.value) = ((0, range), value)
                self.instance.show()

        except Exception as e:
            print('pass: ', e)

    def postWidgetCreate(self, instance):
        instance.setRange(self.__start, self.__end)

    def setRange(self, range):
        (self.__start, self.__end) = range
        if self.instance is not None:
            self.instance.setRange(self.__start, self.__end)

    def getRange(self):
        return self.__start, self.__end

    range = property(getRange, setRange)
