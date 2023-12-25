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
from enigma import eLabel
from enigma import eTimer
from enigma import eEPGCache
from time import gmtime
import json
import os
import re
import socket
import sys
import unicodedata
import NavigationInstance

global my_cur_skin, path_folder


PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    unicode = str
    unichr = chr
    long = int
    from urllib.parse import quote
    from urllib.request import urlopen
    from _thread import start_new_thread
    from urllib.error import HTTPError, URLError
else:
    from urllib import quote
    from urllib2 import urlopen
    from thread import start_new_thread
    from urllib2 import HTTPError, URLError

tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
omdb_api = "679b0028"
# thetvdbkey = 'D19315B88B2DE21F'
thetvdbkey = "a99d487bb3426e5f3a60dea6d3d3c7ef"
epgcache = eEPGCache.getInstance()
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


def OnclearMem():
    try:
        os.system('sync')
        os.system('echo 1 > /proc/sys/vm/drop_caches')
        os.system('echo 2 > /proc/sys/vm/drop_caches')
        os.system('echo 3 > /proc/sys/vm/drop_caches')
    except:
        pass


def checkRedirect(url):
    # print("*** check redirect ***")
    import requests
    from requests.adapters import HTTPAdapter, Retry
    hdr = {"User-Agent": "Enigma2 - Enigma2 Plugin"}
    content = ""
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
                print(e)
        return content
    except Exception as e:
        print('next ret: ', e)
        return content


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
        r'\s\*\d{4}\Z|'
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


def transEpis(text):
    text = text.lower() + '+FIN'
    text = text.replace('  ', '+').replace(' ', '+').replace('&', '+').replace(':', '+').replace('_', '+').replace('u.s.', 'us').replace('l.a.', 'la').replace('.', '+').replace('"', '+').replace('(', '+').replace(')', '+').replace('[', '+').replace(']', '+').replace('!', '+').replace('++++', '+').replace('+++', '+').replace('++', '+')
    text = text.replace('+720p+', '++').replace('+1080i+', '+').replace('+1080p+', '++').replace('+dtshd+', '++').replace('+dtsrd+', '++').replace('+dtsd+', '++').replace('+dts+', '++').replace('+dd5+', '++').replace('+5+1+', '++').replace('+3d+', '++').replace('+ac3d+', '++').replace('+ac3+', '++').replace('+avchd+', '++').replace('+avc+', '++').replace('+dubbed+', '++').replace('+subbed+', '++').replace('+stereo+', '++')
    text = text.replace('+x264+', '++').replace('+mpeg2+', '++').replace('+avi+', '++').replace('+xvid+', '++').replace('+blu+', '++').replace('+ray+', '++').replace('+bluray+', '++').replace('+3dbd+', '++').replace('+bd+', '++').replace('+bdrip+', '++').replace('+dvdrip+', '++').replace('+rip+', '++').replace('+hdtv+', '++').replace('+hddvd+', '++')
    text = text.replace('+german+', '++').replace('+ger+', '++').replace('+english+', '++').replace('+eng+', '++').replace('+spanish+', '++').replace('+spa+', '++').replace('+italian+', '++').replace('+ita+', '++').replace('+russian+', '++').replace('+rus+', '++').replace('+dl+', '++').replace('+dc+', '++').replace('+sbs+', '++').replace('+se+', '++').replace('+ws+', '++').replace('+cee+', '++')
    text = text.replace('+remux+', '++').replace('+directors+', '++').replace('+cut+', '++').replace('+uncut+', '++').replace('+extended+', '++').replace('+repack+', '++').replace('+unrated+', '++').replace('+rated+', '++').replace('+retail+', '++').replace('+remastered+', '++').replace('+edition+', '++').replace('+version+', '++')
    text = text.replace('\xc3\x9f', '%C3%9F').replace('\xc3\xa4', '%C3%A4').replace('\xc3\xb6', '%C3%B6').replace('\xc3\xbc', '%C3%BC')
    text = re.sub('\\+tt[0-9]+\\+', '++', text)
    text = re.sub('\\+\\+\\+\\+.*?FIN', '', text)
    text = re.sub('\\+FIN', '', text)
    return text


def convtext(text=''):
    try:
        if text != '' or text is not None or text != 'None':
            print('original text: ', text)
            text = text.replace("\xe2\x80\x93", "").replace('\xc2\x86', '').replace('\xc2\x87', '')  # replace special
            text = text.lower()
            # if "dc's legends of tomorrow" in text:
                # text = "dc's legends of tomorrow"
            # if "casa a prima vista" in text:
                # text = "casa a prima vista"                
            # if "la ragazza e l'ufficiale" in text:
                # text = "la ragazza e l'ufficiale" 
            text = text.replace('studio aperto mag', 'Studio Aperto').replace('primatv', '').replace('1^tv', '')
            text = text.replace(' prima pagina', '').replace(' -20.30', '').replace(': parte 2', '').replace(': parte 1', '')
            if text.endswith("the"):
                text.rsplit(" ", 1)[0]
                text = text.rsplit(" ", 1)[0]
                text = "the " + str(text)
                print('the from last to start text: ', text)
            text = text + 'FIN'
            text = re.sub(' - [Ss][0-9]+[Ee][0-9]+.*?FIN', '', text)
            text = re.sub(' - [Ss][0-9] [Ee][0-9]+.*?FIN', '', text)            
            text = re.sub('[Ss][0-9]+[Ee][0-9]+.*?FIN', '', text)
            text = re.sub('[Ss][0-9] [Ee][0-9]+.*?FIN', '', text) 

            # print(' - +.*?FIN:INIT ', text)
            text = re.sub(' - +.*?FIN', '', text) 
            # print(' - +.*?FIN:END ', text)
            # text = transEpis(text)
            # text = text.replace('+', ' ')
            # print('transEpis text: ', text)

            text = text.replace(' .', '.').replace('  ', ' ').replace(' - ', ' ').replace(' - "', '')

            # text = REGEX.sub('', text)  # paused
            # # add
            # text = text.replace("\xe2\x80\x93","").replace('\xc2\x86', '').replace('\xc2\x87', '') # replace special
            # # add end

            # # add
            # remove || content at start
            text = re.sub(r'^\|[\w\-\|]*\|', '', text)
            # print('^\|[\w\-\|]*\| text: ', text)
            # remove () content
            # n = 1  # run at least once
            # while n:
                # text, n = re.subn(r'\([^\(\)]*\)', '', text)
            # print('\([^\(\)]*\) text: ', text)
            # # remove [] content
            # n = 1  # run at least once
            # while n:
                # text, n = re.subn(r'\[[^\[\]]*\]', '', text)
            # print('\[[^\[\]]*\] text: ', text)
            # # # add end

            # text = re.sub('\ \(\d+\/\d+\)$', '', text)  # remove episode-number " (xx/xx)" at the end
            # text = re.sub('\ \(\d+\)$', '', text)  # remove episode-number " (xxx)" at the end
            text = re.sub(r"[-,?!/\.\":]", '', text)  # replace (- or , or ! or / or . or " or :) by space
            # print('[-,?!/\.\":] text: ', text)

            # text = re.sub(r'\s{1,}', ' ', text)  # replace multiple space by one space
            # # add
            # text = re.sub('\ |\?|\.|\,|\!|\/|\;|\:|\@|\&|\'|\-|\"|\%|\(|\)|\[|\]\#|\+', '', text)  # modifcare questo (remove space from regex)
            # text = re.sub('\?|\.|\,|\!|\/|\;|\:|\@|\&|\'|\-|\"|\%|\(|\)|\[|\]\#|\+', '', text)  # modifcare questo (remove space from regex)
            # # text = text.replace(' ^`^s', '').replace(' ^`^y','')
            # text = re.sub('\Teil\d+$', '', text)
            # text = re.sub('\Folge\d+$', '', text)
            # # add end

            cleanEvent = re.sub('\ \(\d+\)$', '', text) #remove episode-number " (xxx)" at the end
            cleanEvent = re.sub('\ \(\d+\/\d+\)$', '', cleanEvent) #remove episode-number " (xx/xx)" at the end
            text = re.sub('\!+$', '', cleanEvent)

            # text = unicodify(text)
            text = text.capitalize()
            print('Final text: ', text)
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


class ZEvent(Renderer, VariableText):

    def __init__(self):
        adsl = intCheck()
        if not adsl:
            return
        Renderer.__init__(self)
        VariableText.__init__(self)
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
        if self.event and self.event != 'None' or self.event is not None:
            self.evnt = self.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '')
            self.evntNm = convtext(self.evnt)
            self.infos_file = r"{}\{}.txt".format(path_folder, self.evntNm)
            # if not os.path.exists(self.infos_file):
                # self.downloadInfos()
            self.dwn_infos = "{}/{}.zstar.txt".format(path_folder, self.evntNm)
            # self.infos_file = "{}/{}.event.txt".format(path_folder, self.evntNm)
            if os.path.exists(self.infos_file) and os.stat(self.infos_file).st_size > 1:
                self.setRating(self.infos_file)
                return
            # if os.path.exists(self.dwn_infos) and os.stat(self.dwn_infos).st_size > 1:
                # self.setRating(self.dwn_infos)
                # return
            # if not os.path.exists(self.infos_file):
                # self.downloadInfos()

    def downloadInfos(self):
        if os.path.exists(self.infos_file) and os.stat(self.infos_file).st_size < 1:
            os.remove(self.infos_file)
            print("Zchannel as been removed %s successfully" % self.evntNm)
        url = 'http://api.themoviedb.org/3/search/tv?api_key={}&query={}'.format(str(tmdb_api), quote(self.evntNm))
        if PY3:
            url = url.encode()
        url2 = urlopen(url).read().decode('utf-8')
        jurl = json.loads(url2)
        if 'results' in jurl:
            if 'id' in jurl['results'][0]:
                ids = jurl['results'][0]['id']
                url_2 = 'http://api.themoviedb.org/3/tv/{}?api_key={}&language={}'.format(str(ids), str(tmdb_api), str(lng))
                if PY3:
                    url_2 = url_2.encode()
                url_3 = urlopen(url_2).read().decode('utf-8')
                data2 = json.loads(url_3)
                with open(self.infos_file, "w") as f:
                    json.dump(data2, f)
                print('ZEvent pas data to setRating ', data2)
                self.setRating(self.infos_file)

        else:
            url = 'http://api.themoviedb.org/3/search/movie?api_key={}&query={}'.format(str(tmdb_api), quote(self.evntNm))
            if PY3:
                url = url.encode()
            url2 = urlopen(url).read().decode('utf-8')
            jurl = json.loads(url2)
            if 'results' in jurl:
                if 'id' in jurl['results'][0]:
                    ids = jurl['results'][0]['id']
                    url_2 = 'http://api.themoviedb.org/3/movie/{}?api_key={}&language={}'.format(str(ids), str(tmdb_api), str(lng))
                    if PY3:
                        url_2 = url_2.encode()
                    url_3 = urlopen(url_2).read().decode('utf-8')
                    data2 = json.loads(url_3)
                    with open(self.infos_file, "w") as f:
                        json.dump(data2, f)
                    print('ZEvent pas data to setRating ', data2)
                    self.setRating(self.infos_file)

    def filterSearch(self):
        try:
            sd = "%s\n%s\n%s" % (self.event.getEventName(), self.event.getShortDescription(), self.event.getExtendedDescription())
            w = [
                    "t/s",
                    "Т/s",
                    "SM",
                    "SM",
                    "d/s",
                    "D/s",
                    "stagione",
                    "Sig.",
                    "episodio",
                    "serie TV",
                    "serie"
                    ]
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

    # def delay2(self):
        # self.timer = eTimer()
        # try:
            # self.timer_conn = self.timer.timeout.connect(self.dwn)
        # except:
            # self.timer.callback.append(self.dwn)
        # self.timer.start(50, True)

    def dwn(self):
        start_new_thread(self.epgs, ())

    def setRating(self, data):
        try:
            self.text = ''
            self.infos_file = data
            if os.path.exists(self.infos_file) and os.stat(self.infos_file).st_size > 1:
                if not PY3:
                    try:
                        myFile = open(self.infos_file, 'r')
                        myObject = myFile.read()
                        u = myObject.decode('utf-8-sig')
                        data = u.encode('utf-8')
                        # data.encoding
                        # data.close()
                        data = json.loads(myObject, 'utf-8')
                    except Exception as e:
                        print('ZEvent object error ', e)
                # else:
                # with open(data) as f:
                    # data = json.load(f)

                # {
                  # "poster_path": "/IfB9hy4JH1eH6HEfIgIGORXi5h.jpg",
                  # "adult": false,
                  # "overview": "Jack Reacher must uncover the truth behind a major government conspiracy in order to clear his name. On the run as a fugitive from the law, Reacher uncovers a potential secret from his past that could change his life forever.",
                  # "release_date": "2016-10-19",
                  # "genre_ids": [
                    # 53,
                    # 28,
                    # 80,
                    # 18,
                    # 9648
                  # ],
                  # "id": 343611,
                  # "original_title": "Jack Reacher: Never Go Back",
                  # "original_language": "en",
                  # "title": "Jack Reacher: Never Go Back",
                  # "backdrop_path": "/4ynQYtSEuU5hyipcGkfD6ncwtwz.jpg",
                  # "popularity": 26.818468,
                  # "vote_count": 201,
                  # "video": false,
                  # "vote_average": 4.19
                # }


                with open(self.infos_file) as f:
                    data = json.load(f)
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
                    print("ZEvent text= ", self.text)
                    # if not PY3:
                        # self.text = self.text.encode('utf-8')
                    self.text = "Anno: %s\nNazione: %s\nGenere: %s\nRegista: %s\nAttori: %s" % (Year, Country, Genre, Director, Actors)
                    self.instance.show()
        except Exception as e:
            print('error Exception data  ', e)
