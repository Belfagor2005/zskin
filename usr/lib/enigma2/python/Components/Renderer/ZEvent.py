#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng...04.2020
# 07.2021 start edit lululla
# <widget render="ZEvent" source="session.Event_Now" position="0,500" size="800,20" font="Regular; 24" halign="left" valign="top" zPosition="2" foregroundColor="#000000" backgroundColor="#ffffff" transparent="1" />
# from Tools.Directories import resolveFilename, SCOPE_SKIN
from Components.Renderer.Renderer import Renderer
from Components.VariableText import VariableText
from enigma import eLabel
from enigma import eTimer
from Components.config import config
import re
import json
import os
import socket
import shutil
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


class ZEvent(Renderer, VariableText):
    def __init__(self):
        Renderer.__init__(self)
        VariableText.__init__(self)
        if not intCheck:
            return
        self.timer30 = eTimer()
        self.timer20 = eTimer()

    GUI_WIDGET = eLabel

    def changed(self, what):
        if self.timer20:
            self.timer20.stop()
        if self.timer30:
            self.timer30.stop()

        if what[0] == self.CHANGED_CLEAR:
            self.text = ''
            return
        # if what[0] != self.CHANGED_CLEAR:
            # self.instance.hide()
        try:
            self.timer20.callback.append(self.delay)
        except:
            self.timer20_conn = self.timer20.timeout.connect(self.delay)
        self.timer20.start(150, True)

    def infos(self):
        if self.downevent:
            return
        self.downevent = True
        try:
            self.text = ''
            Title = ''
            ImdbRating = '0'
            Rated = ''
            Country = ''
            Cast = []
            Director = []
            Genres = []
            self.evnt = ''
            self.evntNm = ''
            self.event = self.source.event
            if self.event and self.instance:
                self.evnt = self.event.getEventName().encode('utf-8')
                self.evntNm = REGEX.sub('', self.evnt).strip()
                self.evntNm = self.evntNm.replace('\xc2\x86', '').replace('\xc2\x87', '')
                print('clean event zinfo poster: ', self.evntNm)
                import requests
                try:
                    url = 'http://api.themoviedb.org/3/search/movie?api_key={}&query={}'.format(apikey, quote(self.evntNm))
                    if PY3:
                        url = url.encode()
                    Title = requests.get(url).json()['results'][0]['original_title']
                    ids = requests.get(url).json()['results'][0]['id']
                except:
                    pass

                try:
                    url3 = 'https://api.themoviedb.org/3/movie/{}?api_key={}&append_to_response=credits&language={}'.format(str(ids), apikey, str(language))
                    data2 = requests.get(url3, timeout=5)
                    if data2.status_code == 200:
                        with open(("%surl_rate" % path_folder), "w") as f:
                            json.dump(data2, f)

                        try:
                            Title = data2.json()['original_title']
                        except:
                            Title = data2.json()['title']

                        if "production_countries" in data2 and data2.json()['production_countries']:
                            production_countries = data2.json()['production_countries']
                            for pcountry in data2.json()["production_countries"]:
                                Country = (str(pcountry["name"]))

                        if "genres" in data2 and data2.json()["genres"]:
                            i = 0
                            for name in data2.json()["genres"]:
                                if "name" in name:
                                    Genres.append(str(name["name"]))
                                    i = i+1
                            Genres = " | ".join(map(str, Genres))

                        if "release_date" in data2 and data2.json()['release_date']:
                            Year = data2.json()['release_date']
                        if "vote_average" in data2 and data2.json()['vote_average']:
                            ImdbRating = data2.json()['vote_average']
                        elif "imdbRating" in data2 and data2.json()['imdbRating']:
                            ImdbRating = data2.json()['imdbRating']
                        else:
                            ImdbRating = '0'
                        if "vote_count" in data2 and data2.json()['vote_count']:
                            Rated = data2.json()['vote_count']
                        else:
                            Rated = '0'
                        if "credits" in data2 and data2.json()["credits"]:
                            if "cast" in data2.json()["credits"]:
                                i = 0
                                for actor in data2.json()["credits"]["cast"]:
                                    if "name" in actor:
                                        Cast.append(str(actor["name"]))
                                        i = i+1
                                Cast = ", ".join(map(str, Cast[:3]))
                        if "credits" in data2 and "crew" in data2.json()["credits"]:
                            z = 0
                            for actor in data2.json()["credits"]["crew"]:
                                if "job" in actor:
                                    Director = (str(actor["name"]) + ',')
                                    z = z + 1

                        if Title and Title != "N/A":
                            with open("/tmp/rating", "w") as f:
                                f.write("%s\n%s" % (ImdbRating, Rated))
                            self.text = "Title : %s" % str(Title)
                            self.text += "\nYear : %s" % str(Year)
                            self.text += "\nCountry : %s" % str(Country)
                            self.text += "\nGenre : %s" % str(Genres)
                            self.text += "\nDirector : %s" % str(Director)
                            self.text += "\nCast : %s" % str(Cast)
                            self.text += "\nImdb : %s" % str(ImdbRating)
                            self.text += "\nRated : %s" % str(Rated)
                            print("text= ", self.text)
                except:
                    pass

            else:
                self.downevent = False
                return ""
        except:
            if os.path.exists("/tmp/rating"):
                os.remove("/tmp/rating")
            return ""

    def delay(self):
        self.downevent = False
        try:
            self.timer30.callback.append(self.infos)
        except:
            self.timer30_conn = self.timer30.timeout.connect(self.infos)
        self.timer30.start(150, False)
