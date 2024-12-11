#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng...04.2020, 11.2020, 06.2021
# file by sunriser 07.2021
# <widget source="session.Event_Now" render="ZEvent"/>
# <widget source="session.Event_Next" render="ZEvent"/>
# <widget source="Event" render="ZEvent"/>
# edit by lululla 07.2022
# recode from lululla 2023
from __future__ import absolute_import
from Components.Renderer.Renderer import Renderer
from Components.VariableText import VariableText
from Components.config import config
from enigma import eEPGCache
from enigma import eLabel
from time import gmtime
import NavigationInstance
import json
import os
import socket
import sys
import re
from .Converlibr import convtext
global my_cur_skin


PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    from urllib.request import urlopen
    from urllib.parse import quote
    from _thread import start_new_thread

else:
    from urllib2 import URLError, HTTPError
    from urllib2 import urlopen
    from urllib import quote
    from thread import start_new_thread


tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
omdb_api = "cb1d9f55"
# thetvdbkey = 'D19315B88B2DE21F'
thetvdbkey = "a99d487bb3426e5f3a60dea6d3d3c7ef"
fanart_api = "6d231536dea4318a88cb2520ce89473b"
epgcache = eEPGCache.getInstance()
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


def OnclearMem():
    try:
        os.system('sync')
        os.system('echo 1 > /proc/sys/vm/drop_caches')
        os.system('echo 2 > /proc/sys/vm/drop_caches')
        os.system('echo 3 > /proc/sys/vm/drop_caches')
    except:
        pass


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


class ZEvent(Renderer, VariableText):

    def __init__(self):
        Renderer.__init__(self)
        VariableText.__init__(self)
        self.adsl = intCheck()
        if not self.adsl:
            print("Connessione assente, modalità offline.")
            return
        else:
            print("Connessione rilevata.")
        self.text = ""

    GUI_WIDGET = eLabel

    def changed(self, what):
        if what[0] == self.CHANGED_CLEAR:
            return self.text
        if what[0] != self.CHANGED_CLEAR:
            if self.instance:
                self.instance.hide()
            self.showInfos()

    def showInfos(self):
        self.event = self.source.event
        if not self.event:
            return
        self.evnt = self.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '').rstrip()
        self.evntNm = convtext(self.evnt)
        self.evntNm = str(self.evntNm) 
        self.infos_file = "%s/%s.txt" % (path_folder, self.evntNm)
        self.dwn_infos = "%s/%s.zstar.txt" % (path_folder, self.evntNm)
        if not os.path.exists(self.infos_file) or os.stat(self.infos_file).st_size <= 1:
            return None
        self.setRating(self.infos_file)

    def downloadInfos(self):
        # Rimuove il file se esiste ed è vuoto
        if os.path.exists(self.infos_file) and os.stat(self.infos_file).st_size < 1:
            os.remove(self.infos_file)
            print("Zchannel as been removed %s successfully" % self.evntNm)

        # Costruisce l'URL per la ricerca delle informazioni sulla TV
        url = 'http://api.themoviedb.org/3/search/tv?api_key={}&query={}'.format(str(tmdb_api), quote(self.evntNm))
        try:
            # Richiede i dati JSON
            if PY3:
                url = url.encode()
                url2 = urlopen(url).read()
            else:
                url2 = urlopen(url).read().decode('utf-8')
            jurl = json.loads(url2)

            # Verifica che ci siano risultati
            if 'results' in jurl and len(jurl['results']) > 0 and 'id' in jurl['results'][0]:
                ids = jurl['results'][0]['id']

                # Richiede i dettagli per l'ID trovato
                url = 'http://api.themoviedb.org/3/tv/{}?api_key={}&language={}'.format(str(ids), str(tmdb_api), str(lng))
                try:
                    if PY3:
                        url = url.encode()
                        url = urlopen(url).read()
                    else:
                        url = urlopen(url).read().decode('utf-8')
                except Exception as e:
                    print("Errore nella richiesta zevent, tentativo con il film: %s" % str(e))

                    url = 'http://api.themoviedb.org/3/search/movie?api_key={}&query={}'.format(str(tmdb_api), quote(self.evntNm))
                    if PY3:
                        url = url.encode()
                        url = urlopen(url).read()
                    else:
                        url = urlopen(url).read().decode('utf-8')

                # Salva i dati ottenuti
                data2 = json.loads(url)
                with open(self.infos_file, "w") as f:
                    json.dump(data2, f)

                # Passa i dati per impostare il rating
                self.setRating(self.infos_file)
        except Exception as e:
            print("Errore durante il download delle informazioni: %s" % str(e))

    def filterSearch(self):
        try:
            sd = "%s\n%s\n%s" % (self.event.getEventName(), self.event.getShortDescription(), self.event.getExtendedDescription())
            w = ["t/s", "Т/s", "SM", "SM", "d/s", "D/s", "stagione", "Sig.", "episodio", "serie TV", "serie"]
            for i in w:
                if i in sd:
                    self.srch = "tv"
                    break
                else:
                    self.srch = "multi"
            yr = [_y for _y in re.findall(r'\d{4}', sd) if '1930' <= _y <= '%s' % gmtime().tm_year]
            return '%s' % yr[-1] if yr else None
        except:
            pass

    def epgs(self):
        try:
            events = None
            ref = NavigationInstance.instance.getCurrentlyPlayingServiceReference().toString()
            events = epgcache.lookupEvent(['IBDCT', (ref, 0, -1, -1)])
            for i in range(9):
                titleNxt = events[i][4]
                self.evntNm = convtext(titleNxt)
                self.infos_file = "{}/{}".format(path_folder, self.evntNm)
                if not os.path.exists(self.infos_file):
                    self.downloadInfos()
        except:
            pass

    def dwn(self):
        start_new_thread(self.epgs, ())

    def setRating(self, data):
        try:
            self.text = ''
            self.infos_file = data
            if os.path.exists(self.infos_file) and os.stat(self.infos_file).st_size > 1:
                if PY3:
                    with open(self.dataNm) as f:
                        data = json.load(f)
                else:
                    myFile = open(self.dataNm, 'r')
                    myObject = myFile.read()
                    u = myObject.decode('utf-8-sig')
                    data = u.encode('utf-8')
                    # data.encoding
                    # data.close()
                    data = json.loads(myObject, 'utf-8')
                with open(self.infos_file) as f:
                    # data = json.load(f)
                    Title = ''
                    imdbRating = ''
                    Country = ''
                    Year = ''
                    Rated = ''
                    Genre = []
                    Awards = ''
                    Cast = []
                    Director = []
                    Genres = []
                    Writer = ''
                    Actors = []
                    if "title" in data and data["title"]:
                        Title = str(data["title"])
                    elif "original_name" in data and data["original_name"]:
                        Title = str(data["original_name"])
                    elif "original_title" in data and data["original_title"]:
                        Title = str(data["original_title"])
                    # elif "name" in data:
                        # Title = str(data["name"])

                    if Title and Title != 'null' or Title is not None or Title != "N/A":
                        print('ZEvent title 2 is ', Title)
                    if 'imdbrating' in data and data["imdbRating"]:
                        imdbRating = str(data["imdbRating"])
                    elif 'popularity' in data and data["popularity"]:
                        imdbRating = str(data["popularity"])
                    if 'country' in data and data["Country"]:
                        Country = str(data["Country"])
                    elif 'original_language' in data and data["original_language"]:
                        Country = str(data["original_language"])
                    if 'year' in data and data["Year"]:
                        Year = str(data["Year"])
                    elif 'first_air_date' in data and data["first_air_date"]:
                        Year = str(data["first_air_date"])
                    if 'rated' in data and data["Rated"]:
                        Rated = str(data["Rated"])
                    elif 'vote_average' in data and data['vote_average']:
                        Rated = str(data['vote_average'])
                    else:
                        Rated = 0
                    if 'genres' in data and data["genres"]:
                        i = 0
                        for name in data["genres"]:
                            if "name" in name:
                                Genres.append(str(name["name"]))
                                i += 1
                        Genre = " | ".join(map(str, Genres))
                        # Genre = str(data["Genre"])
                    if 'awards' in data and data["Awards"]:
                        Awards = str(data["Awards"])

                    if "credits" in data and data["credits"]:
                        if "cast" in data["credits"]:
                            i = 0
                            for actor in data["credits"]["cast"]:
                                if "name" in actor:
                                    Cast.append(str(actor["name"]))
                                    i += 1
                            Actors = ", ".join(map(str, Cast[:3]))

                    # elif 'actors' in data and data["Actors"]:
                        # Actors = str(data["Actors"])

                    # if 'director' in data and data["Director"]:
                        # Director = str(data["Director"])

                    if "credits" in data and "crew" in data["credits"]:
                        z = 0
                        for actor in data["credits"]["crew"]:
                            if "job" in actor:
                                Director = (str(actor["name"]) + ',')
                                z += 1
                    else:
                        if "created_by" in data and "name" in data["created_by"]:
                            z = 0
                            for actor in data["created_by"]["name"]:
                                Director = (str(actor["name"]) + ',')
                                z += 1

                    if 'writer' in data and data["Writer"]:
                        Writer = str(data["Writer"])

                    with open("/tmp/rating", "w") as f:
                        f.write("%s\n%s" % (imdbRating, Rated))
                    self.text = "Title: %s" % str(Title)  # .encode('utf-8').decode('utf-8')
                    self.text += "\nYear: %s" % str(Year)  # .encode('utf-8').decode('utf-8')
                    self.text += "\nCountry: %s" % str(Country)  # .encode('utf-8').decode('utf-8')
                    self.text += "\nGenre: %s" % str(Genre)  # .encode('utf-8').decode('utf-8')
                    self.text += "\nDirector: %s" % str(Director)  # .encode('utf-8').decode('utf-8')
                    self.text += "\nAwards: %s" % str(Awards)  # .encode('utf-8').decode('utf-8')
                    self.text += "\nWriter: %s" % str(Writer)  # .encode('utf-8').decode('utf-8')
                    self.text += "\nCast: %s" % str(Actors)  # .encode('utf-8').decode('utf-8')
                    self.text += "\nRated: %s" % str(Rated)  # .encode('utf-8').decode('utf-8')
                    self.text += "\nImdb: %s" % str(imdbRating)  # .encode('utf-8').decode('utf-8')
                    # print("ZEvent text= ", self.text)
                    self.text = "Anno: %s\nNazione: %s\nGenere: %s\nRegista: %s\nAttori: %s" % (Year, Country, Genre, Director, Actors)
                    self.instance.show()
        except Exception as e:
            print('error Exception data  ', e)
