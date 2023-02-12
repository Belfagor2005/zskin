#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng...07.2021
# russian and py3 support by sunriser...
# 07.2021 start edit lululla

# <ePixmap pixmap="/usr/share/enigma2/ZSkin-FHD/menu/panels/nocover.png" position="1090,302" size="270,395" />
# <widget position="1095,310" render="ZChannel" size="260,379" source="ServiceEvent" zPosition="10" />
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, ePicLoad, eTimer
from Components.AVSwitch import AVSwitch
from Components.config import config
import re
import json
import os
import socket
import shutil
import sys


global cur_skin, my_cur_skin, apikey, path_folder


PY3 = sys.version_info.major >= 3
try:
    from urllib.error import URLError, HTTPError
    from urllib.request import urlopen
    from urllib.parse import quote
except:
    from urllib2 import URLError, HTTPError
    from urllib2 import urlopen
    from urllib import quote
# w92
# w154
# w185
# w342
# w500
# w780
# original
formatImg = 'w185'
apikey = "3c3efcf47c3577558812bb9d64019d65"
omdb_api = "cb1d9f55"
thetvdbkey = 'D19315B88B2DE21F'
my_cur_skin = False
cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
path_folder = "/tmp/poster/"
if os.path.isdir("/media/hdd"):
    path_folder = "/media/hdd/poster/"
elif os.path.isdir("/media/usb"):
    path_folder = "/media/usb/poster/"
else:
    path_folder = "/tmp/poster/"
if not os.path.isdir(path_folder):
    os.makedirs(path_folder)

try:
    if my_cur_skin is False:
        myz_skin = "/usr/share/enigma2/%s/apikey" % cur_skin
        # print('skinz namez', myz_skin)
        omdb_skin = "/usr/share/enigma2/%s/omdbkey" % cur_skin
        # print('skinz namez', omdb_skin)
        thetvdb_skin = "/usr/share/enigma2/%s/thetvdbkey" % (cur_skin)
        # print('skinz namez', thetvdb_skin)
        if os.path.exists(myz_skin):
            with open(myz_skin, "r") as f:
                apikey = f.read()
        if os.path.exists(omdb_skin):
            with open(omdb_skin, "r") as f:
                omdb_api = f.read()
        if os.path.exists(thetvdb_skin):
            with open(thetvdb_skin, "r") as f:
                thetvdbkey = f.read()
except:
    my_cur_skin = False

try:
    folder_size = sum([sum(map(lambda fname: os.path.getsize(os.path.join(path_folder, fname)), files)) for path_folder, folders, files in os.walk(path_folder)])
    ozposter = "%0.f" % (folder_size/(1024*1024.0))
    if ozposter >= "5":
        shutil.rmtree(path_folder)
except:
    pass

try:
    from Components.config import config
    language = config.osd.language.value
    language = language[:-3]
except:
    language = 'en'
    pass
print('language: ', language)


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


def cleantitle(text):
    import unicodedata
    text = text.replace('\xc2\x86', '')
    text = text.replace('\xc2\x87', '')
    text = REGEX.sub('', text)
    text = re.sub(r"[-,!/\.\":]", ' ', text)  # replace (- or , or ! or / or . or " or :) by space
    text = re.sub(r'\s{1,}', ' ', text)  # replace multiple space by one space
    text = text.strip()
    try:
        text = unicode(text, 'utf-8')
    except NameError:
        pass
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
    text = text.lower()
    return str(text)


class ZChannel(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        if not intCheck:
            return
        self.timerchan = eTimer()

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if not self.instance:
            return
        if self.timerchan:
            self.timerchan.stop()
        if what[0] == self.CHANGED_CLEAR:
            print('what[0] == self.CHANGED_CLEAR')
            self.instance.hide()
        if what[0] != self.CHANGED_CLEAR:
            print('what[0] != self.CHANGED_CLEAR')
            self.instance.hide()
            self.delay()

    def delay(self):
        self.downloading = False
        self.event = self.source.event
        if self.event: # and self.instance:
            print('self.event and self.instance', self.event)
            self.evnt = self.event.getEventName().encode('utf-8')
            self.evntNm = cleantitle(self.evnt)
            print('clean event Zchannel: ', self.evntNm)
            self.pstrNm = "{}{}.jpg".format(path_folder, quote(self.evntNm))
            if os.path.exists(self.pstrNm):
                # self.downloading = True
                self.showPoster()
            else:
                try:
                    self.timerchan.callback.append(self.info)
                except:
                    self.timerchan_conn = self.timerchan.timeout.connect(self.info)
                self.timerchan.start(150, True)

    def showPoster(self):
        size = self.instance.size()
        self.picload = ePicLoad()
        sc = AVSwitch().getFramebufferScale()
        # if self.picload:
        self.picload.setPara([size.width(), size.height(), sc[0], sc[1], 0, 1, '#00000000'])
        if os.path.exists('/var/lib/dpkg/status'):
            self.picload.startDecode(self.pstrNm, False)
        else:
            self.picload.startDecode(self.pstrNm, 0, 0, False)
        ptr = self.picload.getData()
        if ptr is not None:
            self.instance.setPixmap(ptr)
            self.instance.show()
        # del self.picload

    def info(self):
        # if self.downloading:
            # return
        try:
            url = 'http://api.themoviedb.org/3/search/tv?api_key={}&query={}'.format(apikey, quote(self.evntNm))
            if PY3:
                url = url.encode()
            url2 = urlopen(url).read().decode('utf-8')
            jurl = json.loads(url2)
            if 'results' in jurl:
                if 'id' in jurl['results'][0]:
                    ids = jurl['results'][0]['id']
                    url_2 = 'http://api.themoviedb.org/3/tv/{}?api_key={}&language={}'.format(str(ids), apikey, str(language))
                    if PY3:
                        url_2 = url_2.encode()
                    url_3 = urlopen(url_2).read().decode('utf-8')
                    data2 = json.loads(url_3)
                    with open(("%surl_rate" % path_folder), "w") as f:
                        json.dump(data2, f)
                    poster = data2['poster_path']
                    if poster:
                        self.url_poster = "http://image.tmdb.org/t/p/{}{}".format(formatImg, str(poster))  # w185 risoluzione poster
                        self.savePoster()
                self.timerchan.stop()
        except:
            try:
                url = 'http://api.themoviedb.org/3/search/movie?api_key={}&query={}'.format(apikey, quote(self.evntNm))
                if PY3:
                    url = url.encode()
                url2 = urlopen(url).read().decode('utf-8')
                jurl = json.loads(url2)
                if 'results' in jurl:
                    if 'id' in jurl['results'][0]:
                        ids = jurl['results'][0]['id']
                        url_2 = 'http://api.themoviedb.org/3/movie/{}?api_key={}&language={}'.format(str(ids), apikey, str(language))
                        if PY3:
                            url_2 = url_2.encode()
                        url_3 = urlopen(url_2).read().decode('utf-8')
                        data2 = json.loads(url_3)
                        with open(("%surl_rate" % path_folder), "w") as f:
                            json.dump(data2, f)
                        poster = data2['poster_path']
                        if poster:
                            self.url_poster = "http://image.tmdb.org/t/p/{}{}".format(formatImg, str(poster))
                            self.savePoster()
                self.timerchan.stop()
            except:
                self.timerchan.stop()

    def savePoster(self):
        import requests
        with open(self.pstrNm, 'wb') as f:
            f.write(requests.get(self.url_poster, stream=True, allow_redirects=True).content)
            f.close()
            self.downloading = True
        if os.path.exists(self.pstrNm):
            self.showPoster()
