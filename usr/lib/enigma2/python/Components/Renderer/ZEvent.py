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
import re
import socket
import sys
global my_cur_skin, path_folder


PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    unicode = str
    unichr = chr
    long = int
    from urllib.request import urlopen
    from urllib.parse import quote_plus, quote
    from _thread import start_new_thread

else:
    from urllib2 import URLError, HTTPError
    from urllib2 import urlopen
    from urllib import quote_plus, quote
    from thread import start_new_thread


try:
    from urllib import unquote
except ImportError:
    from urllib.parse import unquote


try:
    lng = config.osd.language.value
    lng = lng[:-3]
except:
    lng = 'en'
    pass


tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
omdb_api = "cb1d9f55"
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


def isMountedInRW(path):
    testfile = path + '/tmp-rw-test'
    os.system('touch ' + testfile)
    if os.path.exists(testfile):
        os.system('rm -f ' + testfile)
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
        myz_skin = "/usr/share/enigma2/%s/apikey" % cur_skin
        omdb_skin = "/usr/share/enigma2/%s/omdbkey" % cur_skin
        thetvdb_skin = "/usr/share/enigma2/%s/thetvdbkey" % (cur_skin)
        if os.path.exists(myz_skin):
            with open(myz_skin, "r") as f:
                tmdb_api = f.read()
            my_cur_skin = True
        if os.path.exists(omdb_skin):
            with open(omdb_skin, "r") as f:
                omdb_api = f.read()
            my_cur_skin = True
        if os.path.exists(thetvdb_skin):
            with open(thetvdb_skin, "r") as f:
                thetvdbkey = f.read()
            my_cur_skin = True
except:
    my_cur_skin = False


def OnclearMem():
    try:
        os.system('sync')
        os.system('echo 1 > /proc/sys/vm/drop_caches')
        os.system('echo 2 > /proc/sys/vm/drop_caches')
        os.system('echo 3 > /proc/sys/vm/drop_caches')
    except:
        pass


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


def remove_accents(string):
    if type(string) is not unicode:
        string = unicode(string, encoding='utf-8')
    string = re.sub(u"[àáâãäå]", 'a', string)
    string = re.sub(u"[èéêë]", 'e', string)
    string = re.sub(u"[ìíîï]", 'i', string)
    string = re.sub(u"[òóôõö]", 'o', string)
    string = re.sub(u"[ùúûü]", 'u', string)
    string = re.sub(u"[ýÿ]", 'y', string)
    return string


def unicodify(s, encoding='utf-8', norm=None):
    if not isinstance(s, unicode):
        s = unicode(s, encoding)
    if norm:
        from unicodedata import normalize
        s = normalize(norm, s)
    return s


def cutName(eventName=""):
    if eventName:
        eventName = eventName.replace('"', '').replace('Х/Ф', '').replace('М/Ф', '').replace('Х/ф', '').replace('.', '').replace(' | ', '')
        eventName = eventName.replace('(18+)', '').replace('18+', '').replace('(16+)', '').replace('16+', '').replace('(12+)', '')
        eventName = eventName.replace('12+', '').replace('(7+)', '').replace('7+', '').replace('(6+)', '').replace('6+', '')
        eventName = eventName.replace('(0+)', '').replace('0+', '').replace('+', '')
        return eventName
    return ""


def getCleanTitle(eventitle=""):
    # save_name = re.sub('\\(\d+\)$', '', eventitle)
    # save_name = re.sub('\\(\d+\/\d+\)$', '', save_name)  # remove episode-number " (xx/xx)" at the end
    # # save_name = re.sub('\ |\?|\.|\,|\!|\/|\;|\:|\@|\&|\'|\-|\"|\%|\(|\)|\[|\]\#|\+', '', save_name)
    save_name = eventitle.replace(' ^`^s', '').replace(' ^`^y', '')
    return save_name


def quoteEventName(eventName):
    try:
        text = eventName.decode('utf8').replace(u'\x86', u'').replace(u'\x87', u'').encode('utf8')
    except:
        text = eventName
    return quote_plus(text, safe="+")


def convtext(text=''):
    try:
        if text != '' or text is not None or text != 'None':
            print('original text: ', text)
            text = text.lower()
            text = remove_accents(text)
            # text = cutName(text)
            # text = getCleanTitle(text)
            if text.endswith("the"):
                text = "the " + text[:-4]
            text = text.replace("\xe2\x80\x93", "").replace('\xc2\x86', '').replace('\xc2\x87', '')  # replace special
            text = text.replace('1^ visione rai', '').replace('1^ visione', '').replace('primatv', '').replace('1^tv', '')
            text = text.replace('prima visione', '').replace('1^ tv', '').replace('((', '(').replace('))', ')')
            text = text.replace('live:', '').replace(' - prima tv', '')
            if 'tg regione' in text:
                text = 'tg3'
            if 'studio aperto' in text:
                text = 'studio aperto'
            if 'josephine ange gardien' in text:
                text = 'josephine ange gardien'
            if 'elementary' in text:
                text = 'elementary'
            if 'squadra speciale cobra 11' in text:
                text = 'squadra speciale cobra 11'
            if 'criminal minds' in text:
                text = 'criminal minds'
            if 'i delitti del barlume' in text:
                text = 'i delitti del barlume'
            if 'senza traccia' in text:
                text = 'senza traccia'
            if 'hudson e rex' in text:
                text = 'hudson e rex'
            if 'ben-hur' in text:
                text = 'ben-hur'
            if 'la7' in text:
                text = 'la7'
            if 'skytg24' in text:
                text = 'skytg24'
            text = text + 'FIN'
            if re.search(r'[Ss][0-9][Ee][0-9]+.*?FIN', text):
                text = re.sub(r'[Ss][0-9][Ee][0-9]+.*?FIN', '', text)
            if re.search(r'[Ss][0-9] [Ee][0-9]+.*?FIN', text):
                text = re.sub(r'[Ss][0-9] [Ee][0-9]+.*?FIN', '', text)
            text = re.sub(r'(odc.\s\d+)+.*?FIN', '', text)
            text = re.sub(r'(odc.\d+)+.*?FIN', '', text)
            text = re.sub(r'(\d+)+.*?FIN', '', text)
            text = text.partition("(")[0] + 'FIN'
            text = re.sub("\\s\d+", "", text)
            text = text.partition("(")[0]
            text = text.partition(":")[0]
            text = text.partition(" -")[0]
            text = re.sub(' - +.+?FIN', '', text)  # all episodes and series ????
            text = re.sub('FIN', '', text)
            text = re.sub(r'^\|[\w\-\|]*\|', '', text)
            text = re.sub(r"[-,?!/\.\":]", '', text)  # replace (- or , or ! or / or . or " or :) by space
            '''
            # remove xx: at start
            text = re.sub(r'^\w{2}:', '', text)
            # remove xx|xx at start
            text = re.sub(r'^\w{2}\|\w{2}\s', '', text)
            # remove xx - at start
            text = re.sub(r'^.{2}\+? ?- ?', '', text)
            # remove all leading content between and including ||
            text = re.sub(r'^\|\|.*?\|\|', '', text)
            text = re.sub(r'^\|.*?\|', '', text)
            # remove everything left between pipes.
            text = re.sub(r'\|.*?\|', '', text)
            # remove all content between and including () multiple times
            text = re.sub(r'\(\(.*?\)\)|\(.*?\)', '', text)
            # remove all content between and including [] multiple times
            text = re.sub(r'\[\[.*?\]\]|\[.*?\]', '', text)
            # List of bad strings to remove
            bad_strings = [

                "ae|", "al|", "ar|", "at|", "ba|", "be|", "bg|", "br|", "cg|", "ch|", "cz|", "da|", "de|", "dk|",
                "ee|", "en|", "es|", "eu|", "ex-yu|", "fi|", "fr|", "gr|", "hr|", "hu|", "in|", "ir|", "it|", "lt|",
                "mk|", "mx|", "nl|", "no|", "pl|", "pt|", "ro|", "rs|", "ru|", "se|", "si|", "sk|", "sp|", "tr|",
                "uk|", "us|", "yu|",
                "1080p", "1080p-dual-lat-cine-calidad.com", "1080p-dual-lat-cine-calidad.com-1",
                "1080p-dual-lat-cinecalidad.mx", "1080p-lat-cine-calidad.com", "1080p-lat-cine-calidad.com-1",
                "1080p-lat-cinecalidad.mx", "1080p.dual.lat.cine-calidad.com", "3d", "'", "#", "(", ")", "-", "[]", "/",
                "4k", "720p", "aac", "blueray", "ex-yu:", "fhd", "hd", "hdrip", "hindi", "imdb", "multi:", "multi-audio",
                "multi-sub", "multi-subs", "multisub", "ozlem", "sd", "top250", "u-", "uhd", "vod", "x264"
            ]
            # Remove numbers from 1900 to 2030
            bad_strings.extend(map(str, range(1900, 2030)))
            # Construct a regex pattern to match any of the bad strings
            bad_strings_pattern = re.compile('|'.join(map(re.escape, bad_strings)))
            # Remove bad strings using regex pattern
            text = bad_strings_pattern.sub('', text)
            # List of bad suffixes to remove
            bad_suffix = [
                " al", " ar", " ba", " da", " de", " en", " es", " eu", " ex-yu", " fi", " fr", " gr", " hr", " mk",
                " nl", " no", " pl", " pt", " ro", " rs", " ru", " si", " swe", " sw", " tr", " uk", " yu"
            ]
            # Construct a regex pattern to match any of the bad suffixes at the end of the string
            bad_suffix_pattern = re.compile(r'(' + '|'.join(map(re.escape, bad_suffix)) + r')$')
            # Remove bad suffixes using regex pattern
            text = bad_suffix_pattern.sub('', text)
            # Replace ".", "_", "'" with " "
            text = re.sub(r'[._\']', ' ', text)
            # Replace "-" with space and strip trailing spaces
            text = text.strip(' -')
            '''
            text = text.strip(' -')
            text = quote(text, safe="")
            print('zevent Final text: ', text)
        else:
            text = text
        return unquote(text).capitalize()
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
            if self.evnt.endswith(' '):
                self.evnt = self.evnt[:-1]
            self.evntNm = convtext(self.evnt)
            self.infos_file = r"{}\{}.txt".format(path_folder, self.evntNm)
            self.dwn_infos = "{}/{}.zstar.txt".format(path_folder, self.evntNm)
            if os.path.exists(self.infos_file) and os.stat(self.infos_file).st_size > 1:
                self.setRating(self.infos_file)
                # return
            else:
                self.downloadInfos()

    def downloadInfos(self):
        if os.path.exists(self.infos_file) and os.stat(self.infos_file).st_size < 1:
            os.remove(self.infos_file)
            print("Zchannel as been removed %s successfully" % self.evntNm)

        url = 'http://api.themoviedb.org/3/search/tv?api_key={}&query={}'.format(str(tmdb_api), quote(self.evntNm))
        if PY3:
            url = url.encode()
            url2 = urlopen(url).read()
        else:
            url2 = urlopen(url).read().decode('utf-8')

        jurl = json.loads(url2)
        if 'results' in jurl:
            print('zchannel part one')
            if 'id' in jurl['results'][0]:
                ids = jurl['results'][0]['id']
                try:
                    url = 'http://api.themoviedb.org/3/tv/{}?api_key={}&language={}'.format(str(ids), str(tmdb_api), str(lng))
                    if PY3:
                        url = url.encode()
                        url = urlopen(url).read()
                    else:
                        url = urlopen(url).read().decode('utf-8')
                except:
                    print('zchannel part two')
                    url = 'http://api.themoviedb.org/3/search/movie?api_key={}&query={}'.format(str(tmdb_api), quote(self.evntNm))
                    if PY3:
                        url = url.encode()
                        url = urlopen(url).read()
                    else:
                        url = urlopen(url).read().decode('utf-8')
                data2 = json.loads(url)
                with open(self.infos_file, "w") as f:
                    json.dump(data2, f)
                # print('ZEvent pas data to setRating ', data2)
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
                "serie"]
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
