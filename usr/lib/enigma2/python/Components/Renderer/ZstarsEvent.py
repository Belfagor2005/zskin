# #!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng
# v1 07.2020, 11.2021
# edit lululla 05-2022
# edit by lululla 07.2022
# recode from lululla 2023
# for channellist
# <widget source="ServiceEvent" render="ZstarsEvent" position="750,390" size="200,20" alphatest="blend" transparent="1" zPosition="3" />
# or
# <widget source="ServiceEvent" render="ZstarsEvent" pixmap="xtra/star.png" position="750,390" size="200,20" alphatest="blend" transparent="1" zPosition="3" />
# <ePixmap pixmap="ZSkin-FHD/icons/star.png" position="136,104" size="200,20" alphatest="blend" zPosition="10" transparent="1" />
# <widget source="session.Event_Now" render="ZstarsEvent" pixmap="ZSkin-FHD/icons/star.png" position="560,367" size="200,20" alphatest="blend" transparent="1" zPosition="3" />
# <ePixmap pixmap="ZSkin-FHD/icons/star.png" position="136,104" size="200,20" alphatest="blend" zPosition="10" transparent="1" />
# <widget source="session.Event_Next" render="ZstarsEvent" pixmap="ZSkin-FHD/icons//star.png" position="560,367" size="200,20" alphatest="blend" transparent="1" zPosition="3" />

from __future__ import print_function
from Components.Renderer.Renderer import Renderer
from Components.VariableValue import VariableValue
from Components.config import config
from enigma import eSlider
import json
import os
import socket
import sys
from .Converlibr import convtext, quoteEventName
global my_cur_skin


PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    from urllib.error import URLError, HTTPError
    from urllib.request import urlopen
else:
    from urllib2 import URLError, HTTPError
    from urllib2 import urlopen


formatImg = 'w185'
tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
omdb_api = "cb1d9f55"
# thetvdbkey = 'D19315B88B2DE21F'
thetvdbkey = "a99d487bb3426e5f3a60dea6d3d3c7ef"
fanart_api = "6d231536dea4318a88cb2520ce89473b"
my_cur_skin = False
cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')


def isMountedInRW(mount_point):
    with open("/proc/mounts", "r") as f:
        for line in f:
            parts = line.split()
            if len(parts) > 1 and parts[1] == mount_point:
                return True
    return False


path_folder = "/tmp/poster"
if os.path.exists("/media/hdd"):
    if isMountedInRW("/media/hdd"):
        path_folder = "/media/hdd/poster"
elif os.path.exists("/media/usb"):
    if isMountedInRW("/media/usb"):
        path_folder = "/media/usb/poster"
elif os.path.exists("/media/mmc"):
    if isMountedInRW("/media/mmc"):
        path_folder = "/media/mmc/poster"

if not os.path.exists(path_folder):
    os.makedirs(path_folder)


try:
    if my_cur_skin is False:
        skin_paths = {
            "tmdb_api": "/usr/share/enigma2/{}/apikey".format(cur_skin),
            "omdb_api": "/usr/share/enigma2/{}/omdbkey".format(cur_skin),
            "thetvdbkey": "/usr/share/enigma2/{}/thetvdbkey".format(cur_skin)
        }
        for key, path in skin_paths.items():
            if os.path.exists(path):
                with open(path, "r") as f:
                    value = f.read().strip()
                    if key == "tmdb_api":
                        tmdb_api = value
                    elif key == "omdb_api":
                        omdb_api = value
                    elif key == "thetvdbkey":
                        thetvdbkey = value
                my_cur_skin = True
except Exception as e:
    print("Errore nel caricamento delle API:", str(e))
    my_cur_skin = False


def checkRedirect(url):
    # print("*** check redirect ***")
    import requests
    from requests.adapters import HTTPAdapter, Retry
    hdr = {"User-Agent": "Enigma2 - Enigma2 Plugin"}
    content = None
    retries = Retry(total=1, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retries)
    http = requests.Session()
    http.mount("http://", adapter)
    http.mount("https://", adapter)
    try:
        r = http.get(url, headers=hdr, timeout=(10, 30), verify=False)
        r.raise_for_status()
        if r.status_code == requests.codes.ok:
            try:
                content = r.json()
            except Exception as e:
                print('checkRedirect error:', e)
        # return content
    except Exception as e:
        print('next ret: ', e)
    return content


try:
    lng = config.osd.language.value
    lng = lng[:-3]
except:
    lng = 'en'
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
    return True


class ZstarsEvent(VariableValue, Renderer):
    def __init__(self):
        Renderer.__init__(self)
        VariableValue.__init__(self)
        self.adsl = intCheck()
        if not self.adsl:
            print("Connessione assente, modalità offline.")
            return
        else:
            print("Connessione rilevata.")
        self.__start = 0
        self.__end = 100
        self.text = ""

    GUI_WIDGET = eSlider

    def changed(self, what):
        if what[0] == self.CHANGED_CLEAR:
            (self.range, self.value) = ((0, 1), 0)
            return
        if what[0] != self.CHANGED_CLEAR:
            print('zstar event B what[0] != self.CHANGED_CLEAR')
            if self.instance:
                self.instance.hide()
            self.infos()

    def infos(self):
        try:
            self.event = self.source.event
            if not self.event:
                return
            self.evnt = self.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '').rstrip()
            self.evntNm = convtext(self.evnt)
            self.dwn_infos = "%s/%s.zstar.txt" % (path_folder, self.evntNm)
            self.dataNm = "%s/%s.txt" % (path_folder, self.evntNm)
            # Controllo e utilizzo dei file locali
            for file_path in [self.dataNm, self.dwn_infos]:
                if os.path.exists(file_path) and os.stat(file_path).st_size > 0:
                    self.setRating(file_path)
                    return
            # Scaricamento dei dati online
            try:
                url = 'http://api.themoviedb.org/3/search/multi?api_key={}&query={}'.format(str(tmdb_api), quoteEventName(self.evntNm))
                if PY3:
                    url = url.encode()
                response = checkRedirect(url)
                if response and 'results' in response and len(response['results']) > 0:
                    ids = response['results'][0].get('id')
                    if ids:
                        for endpoint in ['movie', 'tv']:
                            try:
                                data_url = 'https://api.themoviedb.org/3/{}/{}?api_key={}&append_to_response=credits&language={}'.format(
                                    endpoint, str(ids), str(tmdb_api), str(lng))
                                if PY3:
                                    data_url = data_url.encode()
                                data = json.load(urlopen(data_url))
                                with open(self.dwn_infos, "w") as f:
                                    json.dump(data, f)
                                self.setRating(self.dwn_infos)
                                return
                            except Exception as e:
                                print("Errore durante il fetch di {}: {}".format(endpoint, str(e)))
                print("Nessun risultato trovato su TMDB")
            except Exception as e:
                print("Errore durante il fetch online: {}".format(str(e)))
        except Exception as e:
            print("Errore generale nella funzione infos: {}".format(str(e)))

    def setRating(self, file_path):
        try:
            # with open(file_path, "r", encoding="utf-8") as f:
            with open(file_path, "r") as f:
                data = json.load(f)
            ImdbRating = str(data.get("vote_average", data.get("imdbRating", "0")))
            print("zstar ImdbRating:", ImdbRating)
            if ImdbRating.isdigit() or ImdbRating.replace('.', '', 1).isdigit():
                rtng = int(float(ImdbRating) * 10)
            else:
                rtng = 0
            self.range = (0, 100)
            self.value = rtng
            self.instance.show()
        except Exception as e:
            print("Errore durante la funzione setRating:", str(e))

    def postWidgetCreate(self, instance):
        try:
            if instance is not None:
                instance.setRange(self.__start, self.__end)
        except Exception as e:
            print('error zstar=', e)

    def setRange(self, range):
        (self.__start, self.__end) = range
        if self.instance is not None:
            self.instance.setRange(self.__start, self.__end)

    def getRange(self):
        return self.__start, self.__end
    range = property(getRange, setRange)
