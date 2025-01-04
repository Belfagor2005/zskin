#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng...07.2021
# russian and py3 support by sunriser...
# 07.2021 start edit lululla
# edit by lululla 07.2022
# recode from lululla 2023

from Components.AVSwitch import AVSwitch
from Components.Renderer.Renderer import Renderer
from Components.Sources.CurrentService import CurrentService
from Components.Sources.Event import Event
from Components.Sources.EventInfo import EventInfo
from Components.Sources.ServiceEvent import ServiceEvent
from Components.config import config
# from ServiceReference import ServiceReference
from enigma import ePixmap, ePicLoad
from enigma import getDesktop
import NavigationInstance
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


# w92
# w154
# w185
# w342
# w500
# w780
# original
formatImg = 'w185'
tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
omdb_api = "cb1d9f55"
# thetvdbkey = 'D19315B88B2DE21F'
thetvdbkey = "a99d487bb3426e5f3a60dea6d3d3c7ef"
fanart_api = "6d231536dea4318a88cb2520ce89473b"
my_cur_skin = False
cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
screenwidth = getDesktop(0).size()


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


def getScale():
    return AVSwitch().getFramebufferScale()


class ZChannel(Renderer):

    def __init__(self):
        Renderer.__init__(self)
        self.adsl = intCheck()
        if not self.adsl:
            print("Connessione assente, modalità offline.")
            return
        else:
            print("Connessione rilevata.")
        self.nxts = 0
        self.path = path_folder
        self.picload = ePicLoad()

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if what[0] == self.CHANGED_CLEAR:
            print('zchannel A what[0] == self.CHANGED_CLEAR')
            # return
        if what[0] != self.CHANGED_CLEAR:
            print('zchannel B what[0] != self.CHANGED_CLEAR')
            if self.instance:
                self.instance.hide()
            if not self.picload:
                self.picload = ePicLoad()
            try:
                self.picload.PictureData.get().append(self.DecodePicture)
            except:
                self.picload_conn = self.picload.PictureData.connect(self.DecodePicture)
            self.delay()

    def applySkin(self, desktop, parent):
        attribs = []
        for (attrib, value,) in self.skinAttributes:
            if attrib == "nexts":
                self.nxts = int(value)
            if attrib == "path":
                self.path = str(value)
            '''
            # if attrib == "size":
                # value = value.split(',')
                # width = value[0]
                # height = value[1]
            # else:
                # width = 213
                # height = 310
                # if screenwidth.width() > 1280:
                    # width = 288
                    # height = 414
            '''
            attribs.append((attrib, value))
        self.skinAttributes = attribs
        return Renderer.applySkin(self, desktop, parent)

    def delay(self):
        self.event = self.source.event
        if not self.event:
            return

        self.evnt = self.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '').rstrip()
        self.evntNm = convtext(self.evnt)
        self.evntNm = str(self.evntNm) 
        print('zchannel new self event name:', self.evntNm)
        poster = None
        self.dwn_infos = "%s/%s.zstar.txt" % (path_folder, self.evntNm)
        self.dataNm = "%s/%s.txt" % (path_folder, self.evntNm)
        self.pstrNm = "%s/%s.jpg" % (path_folder, self.evntNm)

        # Mostra il poster se esiste
        if os.path.exists(self.pstrNm):
            self.showPoster()
            return

        # Carica dati dai file disponibili
        poster = self._get_poster_from_file(self.dwn_infos) or self._get_poster_from_file(self.dataNm)
        if poster:
            self.url_poster = "http://image.tmdb.org/t/p/%s%s" % (formatImg, poster)
            self.savePoster()
            return

        # Scarica informazioni online se i file non sono utili
        self._fetch_online_data()

    def _get_poster_from_file(self, filename):
        """Carica il poster da un file JSON, se possibile."""
        if not os.path.exists(filename) or os.stat(filename).st_size <= 1:
            return None
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            return data.get("poster_path")
        except Exception as e:
            print("Errore nella lettura di %s: %s" % (filename, str(e)))
            return None

    def _fetch_online_data(self):
        """Scarica le informazioni online e salva il poster."""
        try:
            # Determina il servizio e il nome dell'evento
            service, servicetype = self._get_service()
            if not service or not servicetype:
                return
            # Rimuove file vuoti
            if os.path.exists(self.dataNm) and os.stat(self.dataNm).st_size < 1:
                os.remove(self.dataNm)
            # Richiesta API per TV
            url = 'http://api.themoviedb.org/3/search/tv?api_key=%s&query=%s' % (tmdb_api, quoteEventName(self.evntNm))
            data2 = self._fetch_api_data(url)
            # if data2 and 'results' in data2 and 'id' in data2['results'][0]:
                # ids = data2['results'][0]['id']
                # url = 'http://api.themoviedb.org/3/tv/%s?api_key=%s&language=%s' % (ids, tmdb_api, lng)
                # data2 = self._fetch_api_data(url)
            if data2 and 'results' in data2 and data2['results']:
                if 'id' in data2['results'][0]:
                    ids = data2['results'][0]['id']
                    url = 'http://api.themoviedb.org/3/tv/%s?api_key=%s&language=%s' % (ids, tmdb_api, lng)
                    data2 = self._fetch_api_data(url)
            # Richiesta API per film (fallback)
            # if not data2:
                # url = 'http://api.themoviedb.org/3/search/movie?api_key=%s&query=%s' % (tmdb_api, quoteEventName(self.evntNm))
                # data2 = self._fetch_api_data(url)
                # if data2 and 'results' in data2 and 'id' in data2['results'][0]:
                    # ids = data2['results'][0]['id']
                    # url = 'http://api.themoviedb.org/3/movie/%s?api_key=%s&language=%s' % (ids, tmdb_api, lng)
                    # data2 = self._fetch_api_data(url)
            if not data2:
                url = 'http://api.themoviedb.org/3/search/movie?api_key=%s&query=%s' % (tmdb_api, quoteEventName(self.evntNm))
                data2 = self._fetch_api_data(url)
                if data2 and 'results' in data2 and data2['results']:
                    if 'id' in data2['results'][0]:
                        ids = data2['results'][0]['id']
                        url = 'http://api.themoviedb.org/3/movie/%s?api_key=%s&language=%s' % (ids, tmdb_api, lng)
                        data2 = self._fetch_api_data(url)
            # Salva il poster, se disponibile
            if data2 and 'poster_path' in data2:
                poster = data2['poster_path']
                self.url_poster = "http://image.tmdb.org/t/p/%s%s" % (formatImg, poster)
                with open(self.dataNm, "w") as f:
                    json.dump(data2, f)
                self.savePoster()
        except Exception as e:
            print("Errore nel fetch online: %s" % str(e))
            if self.instance:
                self.instance.hide()

    def _fetch_api_data(self, url):
        """Effettua una richiesta API e restituisce i dati JSON."""
        try:
            response = urlopen(url)
            return json.load(response)
        except Exception as e:
            print("Errore API %s: %s" % (url, str(e)))
            return None

    def _get_service(self):
        """Ottiene il servizio corrente e il tipo di sorgente."""
        try:
            if isinstance(self.source, ServiceEvent):
                return self.source.getCurrentService(), "ServiceEvent"
            if isinstance(self.source, CurrentService):
                return self.source.getCurrentServiceRef(), "CurrentService"
            if isinstance(self.source, EventInfo):
                return NavigationInstance.instance.getCurrentlyPlayingServiceReference(), "EventInfo"
            if isinstance(self.source, Event):
                return NavigationInstance.instance.getCurrentlyPlayingServiceReference(), "Event"
        except Exception as e:
            print("Errore nel recupero del servizio: %s" % str(e))
        return None, None

    def showPoster(self):
        width = 213
        height = 310
        if screenwidth.width() > 1280:
            width = 360
            height = 520
        if self.instance:
            size = self.instance.size()
            width = size.width()
            height = size.height()
        sc = getScale()
        self.picload = ePicLoad()
        if self.picload:
            try:
                if self.picload.startDecode(self.pstrNm):
                    try:
                        self.picload.PictureData.get().append(self.DecodePicture)
                    except:
                        self.picload_conn = self.picload.PictureData.connect(self.DecodePicture)
                    self.picload.setPara([width, height, sc[0], sc[1], 0, 1, "FF000000"])
                    self.picload.startDecode(self.pstrNm)
            except Exception as e:
                print(e)

    # def showPoster(self):
        # width = 213
        # height = 310
        # if screenwidth.width() > 1280:
            # width = 360
            # height = 520
        # if self.instance:
            # size = self.instance.size()
            # width = size.width()
            # height = size.height()
        # sc = getScale()
        # self.picload.setPara([width, height, sc[0], sc[1], 0, 1, 'FF000000'])
        # try:
            # # Verifica se il percorso dell'immagine è valido
            # if not self.pstrNm or not os.path.exists(self.pstrNm):
                # print("Errore: file immagine non trovato:", self.pstrNm)
                # return
            # # Aggiungi un controllo per il tipo di self.pstrNm
            # print("Tipo di self.pstrNm:", type(self.pstrNm))
            # '''
            # if isinstance(self.pstrNm, bytes):
                # self.pstrNm = self.pstrNm.decode('utf-8')  # Converte bytes in stringa
            # elif isinstance(self.pstrNm, list):
                # self.pstrNm = self.pstrNm[0]  # Usa il primo elemento della lista se è una lista
            # elif not isinstance(self.pstrNm, str):
                # print("Errore: self.pstrNm non è un tipo gestibile.")
                # return
            # '''
            # # Verifica che self.pstrNm ora sia una stringa
            # if isinstance(self.pstrNm, unicode):  # Se è una stringa Unicode in Python 2
                # self.pstrNm = str(self.pstrNm)  # Converti in una stringa di byte (str in Python 2)
            # elif isinstance(self.pstrNm, str):
                # print("Percorso dell'immagine:", self.pstrNm)
            # else:
                # print("Errore: self.pstrNm non è ancora una stringa, ma è :", type(self.pstrNm))
                # return
            # # Decodifica l'immagine
            # if self.picload.startDecode(self.pstrNm):
                # # if not self.picload:
                    # # self.picload = ePicLoad()
                # try:
                    # self.picload.PictureData.get().append(self.DecodePicture)
                # except:
                    # self.picload_conn = self.picload.PictureData.connect(self.DecodePicture)
                # self.picload.setPara([width, height, sc[0], sc[1], 0, 1, "FF000000"])
                # self.picload.startDecode(self.pstrNm)
            # else:
                # print("Errore: non è stato possibile decodificare l'immagine.")
        # except Exception as e:
            # print("Errore in showPoster:", str(e))

    def DecodePicture(self, PicInfo=None):
        ptr = self.picload.getData()
        if ptr is not None:
            self.instance.setPixmap(ptr)
            self.instance.show()

    def savePoster(self):
        if not os.path.exists(self.pstrNm):
            data = urlopen(self.url_poster)
            with open(self.pstrNm, "wb") as local_file:
                local_file.write(data.read())
        if os.path.exists(self.pstrNm):
            if os.path.getsize(self.pstrNm) == 0:
                os.remove(self.pstrNm)
            else:
                print('poster downlaoded:', self.pstrNm)
                self.showPoster()
