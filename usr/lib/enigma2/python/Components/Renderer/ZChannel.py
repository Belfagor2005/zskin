#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng...07.2021
# russian and py3 support by sunriser...
# 07.2021 start edit lululla

# <ePixmap pixmap="/usr/share/enigma2/ZSkin-FHD/menu/panels/nocover.png" position="1090,302" size="270,395" />
# <widget position="1095,310" render="ZChannel" size="260,379" source="ServiceEvent" zPosition="10" />
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, ePicLoad  # , eTimer
from Components.AVSwitch import AVSwitch
from Components.config import config
import re
import json
import os
import socket
import sys

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


def unicodify(s, encoding='utf-8', norm=None):
    if not isinstance(s, unicode):
        s = unicode(s, encoding)
    if norm:
        from unicodedata import normalize
        s = normalize(norm, s)
    return s


def cleantitle(text=''):
    try:
        print('text ->>> ', text)
        # import unicodedata
        if text != '' or text is not None or text != 'None':
            '''
            # text = text.replace('\xc2\x86', '')
            # text = text.replace('\xc2\x87', '')
            '''
            text = REGEX.sub('', text)
            text = re.sub(r"[-,!/\.\":]", '', text)  # replace (- or , or ! or / or . or " or :) by space
            text = re.sub(r'\s{1,}', ' ', text)  # replace multiple space by one space
            # text = text.strip()
            '''
            # try:
                # text = unicode(text, 'utf-8')
            # except Exception as e:
                # print('error name ',e)
                # pass
            # text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
            '''
            text = unicodify(text)
            text = text.lower()
        else:
            text = text
        return text
    except Exception as e:
        print('cleantitle error: ', e)
        pass


class ZChannel(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        adsl = intCheck()
        if not adsl:
            return
        # self.timerchan = eTimer()

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if not self.instance:
            return
        # if self.timerchan:
            # self.timerchan.stop()
        if what[0] == self.CHANGED_CLEAR:
            print('what[0] == self.CHANGED_CLEAR')
            self.instance.hide()
            # return

        if what[0] != self.CHANGED_CLEAR:
            print('what[0] != self.CHANGED_CLEAR')
            
            self.instance.hide()
            '''
            # self.delay()

    # def delay(self):
            # self.downloading = False
            '''
            self.event = self.source.event
            if self.event:  # and self.instance:
                print('self.event', self.event)
                self.evnt = self.event.getEventName().encode('utf-8')
                self.evntNm = cleantitle(self.evnt)
                print('clean event Zchannel: ', self.evntNm)
                self.pstrNm = "{}/{}.jpg".format(folder_poster, self.evntNm)
                if os.path.exists(self.pstrNm):
                    self.showPoster()
                else:
                    '''
                    try:
                        self.timerchan.callback.append(self.info)
                    except:
                        self.timerchan_conn = self.timerchan.timeout.connect(self.info)
                    self.timerchan.start(50, True)
                    '''
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
                                with open(("%s/url_rate" % folder_poster), "w") as f:
                                    json.dump(data2, f)
                                poster = data2['poster_path']
                                if poster:
                                    self.url_poster = "http://image.tmdb.org/t/p/{}{}".format(formatImg, str(poster))  # w185 risoluzione poster
                                    self.savePoster()
                                    return
                            # self.timerchan.stop()
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
                            # self.timerchan.stop()
                        except Exception as e:
                            print('error except zchannel ', e)
                            # self.timerchan.stop()

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
        del self.picload

    '''
    # def info(self):
        # # if self.downloading:
            # # return
        # try:
            # url = 'http://api.themoviedb.org/3/search/tv?api_key={}&query={}'.format(apikey, quote(self.evntNm))
            # if PY3:
                # url = url.encode()
            # url2 = urlopen(url).read().decode('utf-8')
            # jurl = json.loads(url2)
            # if 'results' in jurl:
                # if 'id' in jurl['results'][0]:
                    # ids = jurl['results'][0]['id']
                    # url_2 = 'http://api.themoviedb.org/3/tv/{}?api_key={}&language={}'.format(str(ids), apikey, str(language))
                    # if PY3:
                        # url_2 = url_2.encode()
                    # url_3 = urlopen(url_2).read().decode('utf-8')
                    # data2 = json.loads(url_3)
                    # with open(("%s/url_rate" % folder_poster), "w") as f:
                        # json.dump(data2, f)
                    # poster = data2['poster_path']
                    # if poster:
                        # self.url_poster = "http://image.tmdb.org/t/p/{}{}".format(formatImg, str(poster))  # w185 risoluzione poster
                        # self.savePoster()
                        # return
                # self.timerchan.stop()
        # except:
            # try:
                # url = 'http://api.themoviedb.org/3/search/movie?api_key={}&query={}'.format(apikey, quote(self.evntNm))
                # if PY3:
                    # url = url.encode()
                # url2 = urlopen(url).read().decode('utf-8')
                # jurl = json.loads(url2)
                # if 'results' in jurl:
                    # if 'id' in jurl['results'][0]:
                        # ids = jurl['results'][0]['id']
                        # url_2 = 'http://api.themoviedb.org/3/movie/{}?api_key={}&language={}'.format(str(ids), apikey, str(language))
                        # if PY3:
                            # url_2 = url_2.encode()
                        # url_3 = urlopen(url_2).read().decode('utf-8')
                        # data2 = json.loads(url_3)
                        # with open(("%s/url_rate" % folder_poster), "w") as f:
                            # json.dump(data2, f)
                        # poster = data2['poster_path']
                        # if poster:
                            # self.url_poster = "http://image.tmdb.org/t/p/{}{}".format(formatImg, str(poster))
                            # self.savePoster()
                            # return
                # self.timerchan.stop()
            # except Exception as e:
                # print('error except zchannel ', e)
                # self.timerchan.stop()
    '''

    def savePoster(self):
        import requests
        with open(self.pstrNm, 'wb') as f:
            f.write(requests.get(self.url_poster, stream=True, allow_redirects=True).content)
            f.close()
            # self.downloading = True
        if os.path.exists(self.pstrNm):
            self.showPoster()
        return
