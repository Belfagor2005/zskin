#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng...07.2021
# russian and py3 support by sunriser...
# 07.2021 start edit lululla
# edit by lululla 07.2022
# recode from lululla 2023
# eg:
# <ePixmap pixmap="/usr/share/enigma2/ZSkin-FHD/menu/panels/nocover.png" position="1090,302" size="270,395" />
# <widget position="1095,310" render="ZBanner" size="260,379" source="ServiceEvent" zPosition="10" />
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, ePicLoad
from Components.AVSwitch import AVSwitch
from Components.config import config
import re
import json
import os
import socket
import shutil
import sys

global cur_skin, my_cur_skin

PY3 = (sys.version_info[0] == 3)

if PY3:
    PY3 = True
    unicode = str
    from urllib.error import URLError, HTTPError
    from urllib.request import urlopen
    from urllib.parse import quote
else:
    from urllib2 import URLError, HTTPError
    from urllib2 import urlopen
    from urllib import quote


# isz = "w780"
# "backdrop_sizes": [
      # "w45",
      # "w92",
      # "w154",
      # "w185",
      # "w300",
      # "w500",
      # "w780",
      # "w1280",
      # "w1920",
      # "original"
    # ]
formatImg = 'w780'
tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
omdb_api = "cb1d9f55"
# thetvdbkey = 'D19315B88B2DE21F'
thetvdbkey = "a99d487bb3426e5f3a60dea6d3d3c7ef"
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


path_folder = "/tmp/backdrop"
if os.path.exists("/media/hdd"):
    if not isMountReadonly("/media/hdd"):
        path_folder = "/media/hdd/backdrop"
elif os.path.exists("/media/usb"):
    if not isMountReadonly("/media/usb"):
        path_folder = "/media/usb/backdrop"
elif os.path.exists("/media/mmc"):
    if not isMountReadonly("/media/mmc"):
        path_folder = "/media/mmc/backdrop"

if not os.path.exists(path_folder):
    os.makedirs(path_folder)


try:
    if my_cur_skin is False:
        myz_skin = "/usr/share/enigma2/%s/apikey" % cur_skin
        omdb_skin = "/usr/share/enigma2/%s/omdbkey" % cur_skin
        thetvdb_skin = "/usr/share/enigma2/%s/thetvdbkey" % (cur_skin)
        if os.path.exists(myz_skin):
            with open(myz_skin, "r") as f:
                tmdb_api = f.read()
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


def unicodify(s, encoding='utf-8', norm=None):
    if not isinstance(s, unicode):
        s = unicode(s, encoding)
    if norm:
        from unicodedata import normalize
        s = normalize(norm, s)
    return s


def convtext(text=''):
    try:
        if text != '' or text is not None or text != 'None':
            text = REGEX.sub('', text)
            text = re.sub(r"[-,?!/\.\":]", '', text)  # replace (- or , or ! or / or . or " or :) by space
            text = re.sub(r'\s{1,}', ' ', text)  # replace multiple space by one space
            text = text.replace('PrimaTv', '').replace(' mag', '')
            text = unicodify(text)
            text = text.lower()
        else:
            text = text
        return text
    except Exception as e:
        print('convtext error: ', e)
        pass


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


try:
    folder_size = sum([sum(map(lambda fname: os.path.getsize(os.path.join(path_folder, fname)), files)) for folder_p, folders, files in os.walk(path_folder)])
    ozposter = "%0.f" % (folder_size / (1024 * 1024.0))
    if ozposter >= "5":
        shutil.rmtree(path_folder)
except:
    pass


class ZBanner(Renderer):
    def __init__(self):
        adsl = intCheck()
        if not adsl:
            return
        Renderer.__init__(self)
        self.nxts = 0
        self.path = path_folder
        self.picload = ePicLoad()

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if not self.instance:
            print('not istance')
            return
        if what[0] == self.CHANGED_CLEAR:
            print('ZBanner A what[0] == self.CHANGED_CLEAR')
            return
        if what[0] != self.CHANGED_CLEAR:
            print('ZBanner B what[0] != self.CHANGED_CLEAR')
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
            self.evnt = self.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '').encode('utf-8')
            self.evntNm = convtext(self.evnt)
            self.dataNm = "{}/{}.txt".format(path_folder, self.evntNm)
            self.pstrNm = "{}/{}.jpg".format(path_folder, self.evntNm)
            if os.path.exists(self.pstrNm):
                self.showBackdrop()
            else:
                try:
                    if os.path.exists(self.dataNm):
                        os.remove(self.dataNm)
                        print("%s has been removed successfully" % self.evntNm)
                    url = 'http://api.themoviedb.org/3/search/tv?api_key={}&query={}'.format(tmdb_api, quote(self.evntNm))
                    if PY3:
                        url = url.encode()
                    url2 = urlopen(url).read().decode('utf-8')
                    jurl = json.loads(url2)
                    if 'results' in jurl:
                        if 'id' in jurl['results'][0]:
                            ids = jurl['results'][0]['id']
                            url_2 = 'http://api.themoviedb.org/3/tv/{}?api_key={}&language={}'.format(str(ids), tmdb_api, str(lng))
                            if PY3:
                                url_2 = url_2.encode()
                            url_3 = urlopen(url_2).read().decode('utf-8')
                            data2 = json.loads(url_3)
                            with open(self.dataNm, "w") as f:
                                json.dump(data2, f)
                            backdrop = data2['backdrop_path']
                            if backdrop:
                                self.url_backdrop = "http://image.tmdb.org/t/p/{}{}".format(formatImg, str(backdrop))  # w185 risoluzione backdrop
                                self.savePoster()
                                return
                    else:   
                        url = 'http://api.themoviedb.org/3/search/movie?api_key={}&query={}'.format(tmdb_api, quote(self.evntNm))
                        if PY3:
                            url = url.encode()
                        url2 = urlopen(url).read().decode('utf-8')
                        jurl = json.loads(url2)
                        if 'results' in jurl:
                            if 'id' in jurl['results'][0]:
                                ids = jurl['results'][0]['id']
                                url_2 = 'http://api.themoviedb.org/3/movie/{}?api_key={}&language={}'.format(str(ids), tmdb_api, str(lng))
                                if PY3:
                                    url_2 = url_2.encode()
                                url_3 = urlopen(url_2).read().decode('utf-8')
                                data2 = json.loads(url_3)
                                with open(self.dataNm, "w") as f:
                                    json.dump(data2, f)
                                backdrop = data2['backdrop_path']
                                if backdrop:
                                    self.url_backdrop = "http://image.tmdb.org/t/p/{}{}".format(formatImg, str(backdrop))
                                    self.savePoster()
                                    return
                    '''
                except:
                    try:
                        url = 'http://api.themoviedb.org/3/search/movie?api_key={}&query={}'.format(tmdb_api, quote(self.evntNm))
                        if PY3:
                            url = url.encode()
                        url2 = urlopen(url).read().decode('utf-8')
                        jurl = json.loads(url2)
                        if 'results' in jurl:
                            if 'id' in jurl['results'][0]:
                                ids = jurl['results'][0]['id']
                                url_2 = 'http://api.themoviedb.org/3/movie/{}?api_key={}&language={}'.format(str(ids), tmdb_api, str(lng))
                                if PY3:
                                    url_2 = url_2.encode()
                                url_3 = urlopen(url_2).read().decode('utf-8')
                                data2 = json.loads(url_3)
                                with open(self.dataNm, "w") as f:
                                    json.dump(data2, f)
                                backdrop = data2['backdrop_path']
                                if backdrop:
                                    self.url_backdrop = "http://image.tmdb.org/t/p/{}{}".format(formatImg, str(backdrop))
                                    self.savePoster()
                                    return
                    '''
                except Exception as e:
                    print('error except ZBanner ', e)

    def showBackdrop(self):
        if self.instance:
            size = self.instance.size()
            self.picload = ePicLoad()
            if self.picload:
                sc = AVSwitch().getFramebufferScale()
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
            f.write(requests.get(self.url_backdrop, stream=True, verify=False, allow_redirects=True).content)
            f.close()
        if os.path.exists(self.pstrNm):
            self.showBackdrop()
        return
