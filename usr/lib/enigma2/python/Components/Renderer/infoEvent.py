#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng...04.2020
# 07.2021 start edit lululla
# <widget render="infoEvent" source="session.Event_Now" position="0,500" size="800,20" font="Regular; 24" halign="left" valign="top" zPosition="2" foregroundColor="#000000" backgroundColor="#ffffff" transparent="1" />
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
global cur_skin, myz_skinz, tmdb_api
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


tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
myz_skinz = False
cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
print('skin name  /usr/share/enigma2/', cur_skin)


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


path_folder = "/tmp/poster"
if os.path.exists("/media/hdd"):
    if not isMountReadonly("/media/hdd"):
        path_folder = "/media/hdd/poster"
elif os.path.exists("/media/usb"):
    if not isMountReadonly("/media/usb"):
        path_folder = "/media/usb/poster"
elif os.path.exists("/media/mmc"):
    if not isMountReadonly("/media/mmc"):
        path_folder = "/media/mmc/poster"

if not os.path.exists(path_folder):
    os.makedirs(path_folder)


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

try:
    folder_size = sum([sum(map(lambda fname: os.path.getsize(os.path.join(path_folder, fname)), files)) for folder_p, folders, files in os.walk(path_folder)])
    ozposter = "%0.f" % (folder_size / (1024 * 1024.0))
    if ozposter >= "5":
        shutil.rmtree(path_folder)
except:
    pass


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
            text = text.replace('PrimaTv', '').replace(' mag', '')
            text = unicodify(text)
            text = text.lower()
            print('ZstarsEvent text <<<- ', text)
        else:
            text = text
            print('ZstarsEvent text <<<->>> ', text)
        return text
    except Exception as e:
        print('cleantitle error: ', e)
        pass


class infoEvent(Renderer, VariableText):

    def __init__(self):
        adsl = intCheck()
        if not adsl:
            return
        Renderer.__init__(self)
        VariableText.__init__(self)
        self.timer = eTimer()
        self.downevent = False
        self.text = ''

    GUI_WIDGET = eLabel

    def changed(self, what):
        if what[0] == self.CHANGED_CLEAR:
            return
        else:
            self.delay()

    def delay(self):
        try:
            self.timer.callback.append(self.infos)
        except:
            self.timer_conn = self.timer.timeout.connect(self.infos)
        self.timer.start(150, False)

    def infos(self):
        if self.downloading:
            return
        try:
            Title = ''
            ImdbRating = '0'
            Rated = ''
            production_countries = ''
            Country = ''
            Cast = []
            Director = []
            Genres = []
            self.event = self.source.event
            if self.event:
                self.evnt = self.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '').encode('utf-8')
                self.evntNm = cleantitle(self.evnt)
                self.dataNm = "{}/{}.InfoEvent.txt".format(path_folder, self.evntNm)
                print('clean event InfoEvent: ', self.evntNm)
                if not os.path.exists(self.dataNm):
                    self.downloading = True
                    url = 'https://api.themoviedb.org/3/search/multi?api_key={}&query={}'.format(tmdb_api, quote(self.evntNm))
                    if PY3:
                        url = url.encode()
                    url2 = urlopen(url).read().decode('utf-8')
                    jurl = json.loads(url2)
                    if 'id' in jurl['results'][0]:
                        ids = jurl['results'][0]['id']
                        url3 = 'https://api.themoviedb.org/3/movie/{}?api_key={}&append_to_response=credits'.format(str(ids), tmdb_api)
                        if PY3:
                            url3 = url3.encode()
                        data = urlopen(url3).read().decode('utf-8')
                        data = json.loads(data)
                        with open(self.dataNm, "w") as f:
                            json.dump(data, f)

                with open(self.dataNm) as json_file:
                    data = json.load(json_file)

                if "original_title" in data and data['original_title']:
                    Title = data['original_title']
                else:
                    if "title" in data and data['title']:
                        Title = data['title']

                if "production_countries" in data and data['production_countries']:
                    production_countries = data['production_countries']
                    for pcountry in data["production_countries"]:
                        Country = (str(pcountry["name"]))
                if "genres" in data and data["genres"]:
                    i = 0
                    for name in data["genres"]:
                        if "name" in name:
                            Genres.append(str(name["name"]))
                            i = i+1
                    Genres = " | ".join(map(str, Genres))
                if "release_date" in data and data['release_date']:
                    Year = data['release_date']

                if "vote_average" in data and data['vote_average']:
                    ImdbRating = data['vote_average']
                else:
                    ImdbRating = '0'

                if "vote_count" in data and data['vote_count']:
                    Rated = data['vote_count']
                else:
                    Rated = '0'

                if "credits" in data and data["credits"]:
                    if "cast" in data["credits"]:
                        i = 0
                        for actor in data["credits"]["cast"]:
                            if "name" in actor:
                                Cast.append(str(actor["name"]))
                                i = i+1
                        Cast = ", ".join(map(str, Cast[:3]))
                if "credits" in data and "crew" in data["credits"]:
                    z = 0
                    for actor in data["credits"]["crew"]:
                        if "job" in actor:
                            Director = (str(actor["name"]) + ',')
                            z += 1
                if Title and Title != "N/A":
                    with open("/tmp/rating", "w") as f:
                        f.write("%s\n%s" % (ImdbRating, Rated))
                    self.text = "Title: %s" % str(Title)
                    self.text += "\nYear: %s" % str(Year)
                    self.text += "\nCountry: %s" % str(Country)
                    self.text += "\nGenre: %s" % str(Genres)
                    self.text += "\nDirector: %s" % str(Director)
                    self.text += "\nCast: %s" % str(Cast)
                    self.text += "\nImdb: %s" % str(ImdbRating)
                    self.text += "\nRated: %s" % str(Rated)
                    print("text= ", self.text)
                    return self.text

        except:
            if os.path.exists("/tmp/rating"):
                os.remove("/tmp/rating")
            self.downevent = False
            return self.text
