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

from __future__ import absolute_import
from Components.Renderer.Renderer import Renderer
from Components.VariableValue import VariableValue
from Components.config import config
from enigma import eSlider
import json
import os
import re
import socket
import sys

global my_cur_skin, cur_skin

PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    unicode = str
    unichr = chr
    long = int
    from urllib.error import URLError, HTTPError
    from urllib.request import urlopen
    from urllib.parse import quote_plus, quote
else:
    from urllib2 import URLError, HTTPError
    from urllib2 import urlopen
    from urllib import quote_plus, quote


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


formatImg = 'w185'
tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
omdb_api = "cb1d9f55"
# thetvdbkey = 'D19315B88B2DE21F'
thetvdbkey = "a99d487bb3426e5f3a60dea6d3d3c7ef"
fanart_api = "6d231536dea4318a88cb2520ce89473b"
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
        if text is None:
            print('return None original text:', type(text))
            return  # Esci dalla funzione se text è None
        if text == '':
            print('text is an empty string')
        else:
            # print('original text:', text)
            # Converti tutto in minuscolo
            text = text.lower()
            # print('lowercased text:', text)
            # Rimuovi accenti
            text = remove_accents(text)
            # print('remove_accents text:', text)
            # Applica le funzioni di taglio e pulizia del titolo
            text = cutName(text)
            text = getCleanTitle(text)

            # Regola il titolo se finisce con "the"
            if text.endswith("the"):
                text = "the " + text[:-4]

            # Sostituisci caratteri speciali con stringhe vuote
            text = text.replace("\xe2\x80\x93", "").replace('\xc2\x86', '').replace('\xc2\x87', '')
            text = text.replace('1^ visione rai', '').replace('1^ visione', '').replace('primatv', '').replace('1^tv', '')
            text = text.replace('prima visione', '').replace('1^ tv', '').replace('((', '(').replace('))', ')')
            text = text.replace('live:', '').replace(' - prima tv', '')

            # Gestione casi specifici
            replacements = {
                'giochi olimpici': 'olimpiadi',
                'bruno barbieri': 'brunobarbierix',
                "anni '60": 'anni 60',
                'tg regione': 'tg3',
                'studio aperto': 'studio aperto',
                'josephine ange gardien': 'josephine ange gardien',
                'elementary': 'elementary',
                'squadra speciale cobra 11': 'squadra speciale cobra 11',
                'criminal minds': 'criminal minds',
                'i delitti del barlume': 'i delitti del barlume',
                'senza traccia': 'senza traccia',
                'hudson e rex': 'hudson e rex',
                'ben-hur': 'ben-hur',
                'la7': 'la7',
                'skytg24': 'skytg24'
            }
            for key, value in replacements.items():
                if key in text:
                    text = text.replace(key, value)
            # Rimozione pattern specifici
            text = re.sub(r'^\w{2}:', '', text)  # Rimuove "xx:" all'inizio
            text = re.sub(r'^\w{2}\|\w{2}\s', '', text)  # Rimuove "xx|xx" all'inizio
            text = re.sub(r'^.{2}\+? ?- ?', '', text)  # Rimuove "xx -" all'inizio
            text = re.sub(r'^\|\|.*?\|\|', '', text)  # Rimuove contenuti tra "||"
            text = re.sub(r'^\|.*?\|', '', text)  # Rimuove contenuti tra "|"
            text = re.sub(r'\|.*?\|', '', text)  # Rimuove qualsiasi altro contenuto tra "|"
            text = re.sub(r'\(\(.*?\)\)|\(.*?\)', '', text)  # Rimuove contenuti tra "()"
            text = re.sub(r'\[\[.*?\]\]|\[.*?\]', '', text)  # Rimuove contenuti tra "[]"
            text = re.sub(r' +ح| +ج| +م', '', text)  # Rimuove numeri di episodi/serie in arabo
            # Rimozione di stringhe non valide
            bad_strings = [
                "ae|", "al|", "ar|", "at|", "ba|", "be|", "bg|", "br|", "cg|", "ch|", "cz|", "da|", "de|", "dk|",
                "ee|", "en|", "es|", "eu|", "ex-yu|", "fi|", "fr|", "gr|", "hr|", "hu|", "in|", "ir|", "it|", "lt|",
                "mk|", "mx|", "nl|", "no|", "pl|", "pt|", "ro|", "rs|", "ru|", "se|", "si|", "sk|", "sp|", "tr|",
                "uk|", "us|", "yu|",
                "1080p", "4k", "720p", "hdrip", "hindi", "imdb", "vod", "x264"
            ]
            bad_strings.extend(map(str, range(1900, 2030)))  # Anni da 1900 a 2030
            bad_strings_pattern = re.compile('|'.join(map(re.escape, bad_strings)))
            text = bad_strings_pattern.sub('', text)
            # Rimozione suffissi non validi
            bad_suffix = [
                " al", " ar", " ba", " da", " de", " en", " es", " eu", " ex-yu", " fi", " fr", " gr", " hr", " mk",
                " nl", " no", " pl", " pt", " ro", " rs", " ru", " si", " swe", " sw", " tr", " uk", " yu"
            ]
            bad_suffix_pattern = re.compile(r'(' + '|'.join(map(re.escape, bad_suffix)) + r')$')
            text = bad_suffix_pattern.sub('', text)
            # Rimuovi "." "_" "'" e sostituiscili con spazi
            text = re.sub(r'[._\']', ' ', text)
            # Rimuove tutto dopo i ":" (incluso ":")
            text = re.sub(r':.*$', '', text)
            # Pulizia finale
            text = text.partition("(")[0]  # Rimuove contenuti dopo "("
            text = text.partition(" -")[0]  # Rimuove contenuti dopo "-"
            text = text.strip(' -')
            # Modifiche forzate
            text = text.replace('XXXXXX', '60')
            text = text.replace('brunobarbierix', 'bruno barbieri - 4 hotel')
            text = quote(text, safe="")
            print('text safe:', text)
        return unquote(text).capitalize()
    except Exception as e:
        print('convtext error:', e)
        return None


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
        adsl = intCheck()
        if not adsl:
            return
        Renderer.__init__(self)
        VariableValue.__init__(self)
        self.__start = 0
        self.__end = 100
        self.text = ''
        # self.timer30 = eTimer()

    GUI_WIDGET = eSlider

    def changed(self, what):
        if what[0] == self.CHANGED_CLEAR:
            print('zstar event A what[0] == self.CHANGED_CLEAR')
            (self.range, self.value) = ((0, 1), 0)
            return
        if what[0] != self.CHANGED_CLEAR:
            print('zstar event B what[0] != self.CHANGED_CLEAR')
            if self.instance:
                self.instance.hide()
            self.infos()

    def infos(self):
        try:
            ids = None
            data = ''
            self.event = self.source.event
            if self.event:
                self.evnt = self.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '')
                if self.evnt.endswith(' '):
                    self.evnt = self.evnt[:-1]
                self.evntNm = convtext(self.evnt)
                self.dwn_infos = "{}/{}.zstar.txt".format(path_folder, self.evntNm)
                self.dataNm = "{}/{}.txt".format(path_folder, self.evntNm)
                if os.path.exists(self.dataNm) and os.stat(self.dataNm).st_size > 1:
                    self.setRating(self.dataNm)
                    return
                if os.path.exists(self.dwn_infos) and os.stat(self.dwn_infos).st_size > 1:
                    self.setRating(self.dwn_infos)
                    return
                # print('clean zstar: ', self.evntNm)
                # if not os.path.exists(self.dwn_infos):
                else:
                    try:
                        url = 'http://api.themoviedb.org/3/search/multi?api_key={}&query={}'.format(str(tmdb_api), quoteEventName(self.evntNm))
                        if PY3:
                            url = url.encode()
                        url = checkRedirect(url)
                        if url is not None:
                            ids = url['results'][0]['id']
                            # print('zstar url2 ids:', ids)
                            if ids and ids is not None or ids != '':
                                try:
                                    data = 'https://api.themoviedb.org/3/movie/{}?api_key={}&append_to_response=credits&language={}'.format(str(ids), str(tmdb_api), str(lng))  # &language=" + str(language)

                                    if PY3:
                                        data = data.encode()

                                    if data is not None:
                                        data = json.load(urlopen(data))
                                        open(self.dwn_infos, "w").write(json.dumps(data))
                                    else:
                                        data = 'https://api.themoviedb.org/3/tv/{}?api_key={}&append_to_response=credits&language={}'.format(str(ids), str(tmdb_api), str(lng))  # &language=" + str(language)
                                        if data:
                                            data = json.load(urlopen(data))
                                            open(self.dwn_infos, "w").write(json.dumps(data))
                                            self.setRating(self.dwn_infos)
                                except Exception as e:
                                    print('zstar pass Exception: ', e)
                            else:
                                return
                        else:
                            return
                    except Exception as e:
                        print('Exception no ids in zstar ', e)
                    return
        except Exception as e:
            print('zstar pass ImdbRating: ', e)

    def setRating(self, data):
        try:
            rtng = 0
            range = 0
            value = 0
            ImdbRating = "0"
            self.dwn_infos = data
            if PY3:
                with open(self.dwn_infos) as f:
                    data = json.load(f)
            else:
                # if not PY3:
                myFile = open(self.dwn_infos, 'r')
                myObject = myFile.read()
                u = myObject.decode('utf-8-sig')
                data = u.encode('utf-8')
                # data.encoding
                # data.close()
                data = json.loads(myObject, 'utf-8')

            ImdbRating = ''
            if "vote_average" in data:
                ImdbRating = data['vote_average']
            elif "imdbRating" in data:
                ImdbRating = data['imdbRating']
            else:
                ImdbRating = '0'
            print('zstar ImdbRating: ', ImdbRating)
            if ImdbRating and ImdbRating != '0':
                rtng = int(10 * (float(ImdbRating)))
            else:
                rtng = 0
            range = 100
            value = rtng
            (self.range, self.value) = ((0, range), value)
            self.instance.show()
        except Exception as e:
            print('zstar ImdbRating Exception: ', e)

    def postWidgetCreate(self, instance):
        instance.setRange(self.__start, self.__end)

    def setRange(self, range):
        (self.__start, self.__end) = range
        if self.instance is not None:
            self.instance.setRange(self.__start, self.__end)

    def getRange(self):
        return self.__start, self.__end

    range = property(getRange, setRange)
