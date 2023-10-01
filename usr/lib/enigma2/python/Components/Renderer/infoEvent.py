#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng...04.2020
# 07.2021 start edit lululla
# <widget render="infoEvent" source="session.Event_Now" position="0,500" size="800,20" font="Regular; 24" halign="left" valign="top" zPosition="2" foregroundColor="#000000" backgroundColor="#ffffff" transparent="1" />
# from Tools.Directories import resolveFilename, SCOPE_SKIN
from Components.Renderer.Renderer import Renderer
from Components.VariableText import VariableText
from Components.config import config
from enigma import eLabel, eTimer
import json
import os
import re
import six
import socket
import shutil
from six.moves.urllib.request import urlopen
from six.moves.urllib.parse import quote
global cur_skin, myz_skinz, tmdb_api


path_folder = "/tmp/poster/"
if os.path.isdir("/media/hdd"):
    path_folder = "/media/hdd/poster/"
elif os.path.isdir("/media/usb"):
    path_folder = "/media/usb/poster/"
else:
    path_folder = "/tmp/poster/"
if not os.path.isdir(path_folder):
    os.makedirs(path_folder)


tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
myz_skinz = False
cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
print('skin name  /usr/share/enigma2/', cur_skin)
try:
    if myz_skinz is False:
        myz_skin = "/usr/share/enigma2/%s/apikey" % cur_skin
        print('skinz namez', myz_skin)
        if os.path.exists(myz_skin):
            with open(myz_skin, "r") as f:
                tmdb_api = f.read()
                myz_skinz = True

except:
    myz_skinz = False
    tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
print('my apikey in use: ', tmdb_api)

try:
    folder_size = sum([sum([os.path.getsize(os.path.join(path_folder, fname)) for fname in files]) for path_folder, folders, files in os.walk(path_folder)])
    eventx = "%0.f" % (folder_size // (1024 * 1024.0))
    if eventx >= "5":
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


class infoEvent(Renderer, VariableText):

    def __init__(self):
        adsl = intCheck()
        if not adsl:
            return
        Renderer.__init__(self)
        VariableText.__init__(self)
        self.text = ''

    GUI_WIDGET = eLabel

    def changed(self, what):
        if what[0] == self.CHANGED_CLEAR:
            # self.text = ''
            return
        else:
            self.delay()

    def infos(self):
        if self.downloading:
            return
        self.downloading = True
        try:
            Title = ''
            ImdbRating = ''
            Rated = ''
            Cast = []
            Director = []
            Genres = []
            self.event = self.source.event
            if self.event:
                # evntNm = REGEX.sub('', self.event.getEventName()).strip()
                # evntNm = evntNm.replace('\xc2\x86', '').replace('\xc2\x87', '')
                # evntNm = evntNm.replace('FILM ', '').replace('FILM - ', '').replace('film - ', '').replace('TELEFILM ', '').replace('TELEFILM - ', '').replace('telefilm - ', '')
                
                self.evnt = self.event.getEventName()
                self.evntNm = REGEX.sub('', self.evnt).strip()
                self.evntNm = self.evntNm.replace('\xc2\x86', '').replace('\xc2\x87', '')
                
                # self.evntNm = evntNm
                if self.intCheck():
                    url = 'https://api.themoviedb.org/3/search/multi?api_key={}&query={}'.format(tmdb_api, quote(self.evntNm))
                    if six.PY3:
                        url = url.encode()
                    url2 = urlopen(url).read().decode('utf-8')
                    jurl = json.loads(url2)
                    if 'id' in jurl['results'][0]:
                        ids = jurl['results'][0]['id']
                    url3 = 'https://api.themoviedb.org/3/movie/{}?api_key={}&append_to_response=credits&language={}'.format(str(ids), tmdb_api, str(language))
                    if six.PY3:
                        url3 = url3.encode()
                    data = urlopen(url3).read().decode('utf-8')
                    data = json.loads(data)
                    # print('jurl2 data = ', data)
                    with open(("%surl_rate" % path_folder), "w") as f:
                        json.dump(data, f)
                    with open("%surl_rate" % path_folder) as json_file:
                        data = json.load(json_file)

                    if "original_title" in data and data['original_title']:
                        Title = data['original_title']
                        print('title = ', Title)
                    else:
                        if "title" in data and data['title']:
                            Title = data['title']
                            print('title = ', Title)

                    if "production_countries" in data and data['production_countries']:
                        production_countries = data['production_countries']
                        for pcountry in data["production_countries"]:
                            Country = (str(pcountry["name"]))
                        print('country = ', Country)
                    if "genres" in data and data["genres"]:
                        i = 0
                        for name in data["genres"]:
                            if "name" in name:
                                Genres.append(str(name["name"]))
                                print('genres = ', Genres)
                                i = i+1
                        Genres = " | ".join(map(str, Genres))
                        print('genre = ', Genres)
                    if "release_date" in data and data['release_date']:
                        Year = data['release_date']
                        print('year = ', Year)

                    if "vote_average" in data and data['vote_average']:
                        ImdbRating = data['vote_average']
                        print('imdrating = ', ImdbRating)
                    else:
                        ImdbRating = '0'
                        print('imdrating = ', ImdbRating)

                    if "vote_count" in data and data['vote_count']:
                        Rated = data['vote_count']
                        print('rated = ', Rated)
                    else:
                        Rated = '0'
                        print('rated = ', Rated)

                    if "credits" in data and data["credits"]:
                        if "cast" in data["credits"]:
                            i = 0
                            for actor in data["credits"]["cast"]:
                                if "name" in actor:
                                    Cast.append(str(actor["name"]))
                                    print('actor= ', Cast)
                                    i = i+1
                            Cast = ", ".join(map(str, Cast[:3]))
                            print('actor = ', Cast)
                    if "credits" in data and "crew" in data["credits"]:
                        z = 0
                        for actor in data["credits"]["crew"]:
                            if "job" in actor:
                                Director = (str(actor["name"]) + ',')
                                print('director = ', Director)
                                z = z+1
                    if Title and Title != "N/A":
                        with open("/tmp/rating", "w") as f:
                            f.write("%s\n%s" % (ImdbRating, Rated))
                        self.text = "Title : %s" % str(Title)  # .encode('utf-8').decode('utf-8')
                        self.text += "\nYear : %s" % str(Year)  # .encode('utf-8').decode('utf-8')
                        self.text += "\nCountry : %s" % str(Country)  # .encode('utf-8').decode('utf-8')
                        self.text += "\nGenre : %s" % str(Genres)  # .encode('utf-8').decode('utf-8')
                        self.text += "\nDirector : %s" % str(Director)  # .encode('utf-8').decode('utf-8')
                        self.text += "\nCast : %s" % str(Cast)  # .encode('utf-8').decode('utf-8')
                        self.text += "\nRated : %s" % str(Rated)  # .encode('utf-8').decode('utf-8')
                        self.text += "\nImdb : %s" % str(ImdbRating)  # .encode('utf-8').decode('utf-8')
                        print("text= ", self.text)
                    else:
                        if os.path.exists("/tmp/rating"):
                            os.remove("/tmp/rating")
                            print('/tmp/rating removed')
                            self.downloading = False
                        return self.text
                else:
                    self.downloading = False
                    return self.text

        except:
            if os.path.exists("/tmp/rating"):
                os.remove("/tmp/rating")
            return self.text

    def delay(self):
        self.downloading = False
        self.timer = eTimer()
        try:
            self.timer.callback.append(self.infos)
        except:
            self.timer_conn = self.timer.timeout.connect(self.infos)
        self.timer.start(150, False)
