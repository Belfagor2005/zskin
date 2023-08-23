#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng...07.2021
# russian and py3 support by sunriser...
# 07.2021 start edit lululla

# <ePixmap pixmap="/usr/share/enigma2/ZSkin-FHD/menu/panels/nocover.png" position="1090,302" size="270,395" />
# <widget position="1095,310" render="ZChannel" size="260,379" source="ServiceEvent" zPosition="10" />
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, ePicLoad  # , eTimer
try:
    from Components.AVSwitch import AVSwitch as eAVSwitch
except Exception:
    from Components.AVSwitch import iAVSwitch as eAVSwitch
# from Components.AVSwitch import AVSwitch as eAVSwitch
from Components.config import config
import re
import json
import os
import socket
import sys
import shutil

# from enigma import loadJPG

global cur_skin, my_cur_skin, apikey

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


def isMountReadonly(mnt):
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


folder_poster = "/tmp/poster"
if os.path.exists("/media/hdd"):
    if not isMountReadonly("/media/hdd"):
        folder_poster = "/media/hdd/poster"
elif os.path.exists("/media/usb"):
    if not isMountReadonly("/media/usb"):
        folder_poster = "/media/usb/poster"
elif os.path.exists("/media/mmc"):
    if not isMountReadonly("/media/mmc"):
        folder_poster = "/media/mmc/poster"
else:
    folder_poster = "/tmp/poster"

if not os.path.exists(folder_poster):
    os.makedirs(folder_poster)
if not os.path.exists(folder_poster):
    folder_poster = "/tmp/poster"


try:
    if my_cur_skin is False:
        myz_skin = "/usr/share/enigma2/%s/apikey" % cur_skin
        omdb_skin = "/usr/share/enigma2/%s/omdbkey" % cur_skin
        thetvdb_skin = "/usr/share/enigma2/%s/thetvdbkey" % (cur_skin)
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
adsl = intCheck()


try:
    folder_size = sum([sum(map(lambda fname: os.path.getsize(os.path.join(folder_poster, fname)), files)) for folder_p, folders, files in os.walk(folder_poster)])
    ozposter = "%0.f" % (folder_size / (1024 * 1024.0))
    if ozposter >= "5":
        shutil.rmtree(folder_poster)
except:
    pass


def unicodify(s, encoding='utf-8', norm=None):
    if not isinstance(s, unicode):
        s = unicode(s, encoding)
    if norm:
        from unicodedata import normalize
        s = normalize(norm, s)
    return s


def cleantitle(text=''):
    try:
        print('ZChannel text ->>> ', text)
        if text != '' or text is not None or text != 'None':
            text = REGEX.sub('', text)
            text = re.sub(r"[-,!/\.\":]", '', text)  # replace (- or , or ! or / or . or " or :) by space
            text = re.sub(r'\s{1,}', ' ', text)  # replace multiple space by one space
            text = unicodify(text)
            text = text.lower()
            print('ZChannel text <<<- ', text)
        else:
            text = text
            print('ZChannel text <<<->>> ', text)
        return text
    except Exception as e:
        print('cleantitle error: ', e)
        pass


class ZChannel(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        if not adsl:
            return
        self.nxts = 0
        self.path = folder_poster
        self.picload = ePicLoad()

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if not self.instance:
            print('not istance')
            return
        if what[0] == self.CHANGED_CLEAR:
            print('what[0] == self.CHANGED_CLEAR')
            return
        if what[0] != self.CHANGED_CLEAR:
            print('what[0] != self.CHANGED_CLEAR')
            self.instance.hide()
            self.delay()

    def applySkin(self, desktop, parent):
        attribs = []
        for (attrib, value,) in self.skinAttributes:
            if attrib == "nexts":
                self.nxts = int(value)
            if attrib == "path":
                self.path = str(value)
            attribs.append((attrib, value))
        self.skinAttributes = attribs
        return Renderer.applySkin(self, desktop, parent)

    def delay(self):
        self.event = self.source.event
        if self.event:  # and self.instance:
            print('self.event', self.event)
            self.evnt = self.event.getEventName().encode('utf-8')
            self.evntNm = cleantitle(self.evnt)
            print('clean event Zchannel: ', self.evntNm)
            self.pstrNm = "{}/{}.jpg".format(folder_poster, self.evntNm)
            print('self.pstrNm: ', self.pstrNm)
            if os.path.exists(self.pstrNm):
                # from Tools.LoadPixmap import LoadPixmap
                # # self.instance.hide()
                # # self.instance.setPixmap(loadJPG(self.pstrNm))
                # pixmap = LoadPixmap(cached=True, path=self.pstrNm)
                # self.instance.setPixmap(pixmap)
                # self.instance.setScale(2)
                # self.instance.show()
                print('showposter')
                self.showPoster()
            else:
                try:
                    if os.path.exists("%s/url_rate" % folder_poster):
                        os.remove("%s/url_rate" % folder_poster)
                        print("%s has been removed successfully" %folder_poster)
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
                            with open(("%s/url_rate" % folder_poster), "w") as f:
                                json.dump(data2, f)
                            poster = data2['poster_path']
                            if poster:
                                self.url_poster = "http://image.tmdb.org/t/p/{}{}".format(formatImg, str(poster))  # w185 risoluzione poster
                                self.savePoster()
                                return
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
                                with open(("%s/url_rate" % folder_poster), "w") as f:
                                    json.dump(data2, f)
                                poster = data2['poster_path']
                                if poster:
                                    self.url_poster = "http://image.tmdb.org/t/p/{}{}".format(formatImg, str(poster))
                                    self.savePoster()
                                    return
                    except Exception as e:
                        print('error except zchannel ', e)

    def showPoster(self):
        if self.instance:
            size = self.instance.size()
            self.picload = ePicLoad()
            if self.picload:
                print('self.picload: loading')
                sc = eAVSwitch().getFramebufferScale()
                print('self.picload: loaded')
                self.picload.setPara([size.width(), size.height(), sc[0], sc[1], 0, 1, '#00000000'])
                if os.path.exists('/var/lib/dpkg/status'):
                    self.picload.startDecode(self.pstrNm, False)
                else:
                    self.picload.startDecode(self.pstrNm, 0, 0, False)
                ptr = self.picload.getData()
                if ptr is not None:
                    self.instance.setPixmap(ptr)
                    self.instance.show()
                del self.picload

    def savePoster(self):
        import requests
        with open(self.pstrNm, 'wb') as f:
            f.write(requests.get(self.url_poster, stream=True, verify=False, allow_redirects=True).content)
            f.close()
        if os.path.exists(self.pstrNm):
            self.showPoster()
        return
