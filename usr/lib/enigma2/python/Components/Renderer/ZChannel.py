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
from ServiceReference import ServiceReference
from six import text_type
from enigma import ePixmap, ePicLoad
from enigma import getDesktop
import NavigationInstance
import json
import os
import re
import socket
import sys
from re import search, sub, I, S

global my_cur_skin, cur_skin

PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    from urllib.error import URLError, HTTPError
    from urllib.request import urlopen
    from urllib.parse import quote_plus
else:
    from urllib2 import URLError, HTTPError
    from urllib2 import urlopen
    from urllib import quote_plus


try:
    lng = config.osd.language.value
    lng = lng[:-3]
except:
    lng = 'en'
    pass


# w92
# w154
# w185
# w342
# w500
# w780
# original
formatImg = 'w185'
tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
omdb_api = "679b0028"
# thetvdbkey = 'D19315B88B2DE21F'
thetvdbkey = "a99d487bb3426e5f3a60dea6d3d3c7ef"
my_cur_skin = False
cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
screenwidth = getDesktop(0).size()


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


def quoteEventName(eventName):
    try:
        text = eventName.decode('utf8').replace(u'\x86', u'').replace(u'\x87', u'').encode('utf8')
    except:
        text = eventName
    return quote_plus(text, safe="+")


REGEX = re.compile(
    r'[\(\[].*?[\)\]]|'                    # Parentesi tonde o quadre
    r':?\s?odc\.\d+|'                      # odc. con o senza numero prima
    r'\d+\s?:?\s?odc\.\d+|'                # numero con odc.
    r'[:!]|'                               # due punti o punto esclamativo
    r'\s-\s.*|'                            # trattino con testo successivo
    r',|'                                  # virgola
    r'/.*|'                                # tutto dopo uno slash
    r'\|\s?\d+\+|'                         # | seguito da numero e +
    r'\d+\+|'                              # numero seguito da +
    r'\s\*\d{4}\Z|'                        # * seguito da un anno a 4 cifre
    r'[\(\[\|].*?[\)\]\|]|'                # Parentesi tonde, quadre o pipe
    r'(?:\"[\.|\,]?\s.*|\"|'               # Testo tra virgolette
    r'\.\s.+)|'                            # Punto seguito da testo
    r'Премьера\.\s|'                       # Specifico per il russo
    r'[хмтдХМТД]/[фс]\s|'                  # Pattern per il russo con /ф o /с
    r'\s[сС](?:езон|ерия|-н|-я)\s.*|'      # Stagione o episodio in russo
    r'\s\d{1,3}\s[чсЧС]\.?\s.*|'           # numero di parte/episodio in russo
    r'\.\s\d{1,3}\s[чсЧС]\.?\s.*|'         # numero di parte/episodio in russo con punto
    r'\s[чсЧС]\.?\s\d{1,3}.*|'             # Parte/Episodio in russo
    r'\d{1,3}-(?:я|й)\s?с-н.*',            # Finale con numero e suffisso russo
    re.DOTALL)


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


def remove_accents(string):
    if not isinstance(string, text_type):
        string = text_type(string, 'utf-8')
    string = re.sub(u"[àáâãäå]", 'a', string)
    string = re.sub(u"[èéêë]", 'e', string)
    string = re.sub(u"[ìíîï]", 'i', string)
    string = re.sub(u"[òóôõö]", 'o', string)
    string = re.sub(u"[ùúûü]", 'u', string)
    string = re.sub(u"[ýÿ]", 'y', string)
    return string


def unicodify(s, encoding='utf-8', norm=None):
    if not isinstance(s, text_type):
        s = text_type(s, encoding)
    if norm:
        from unicodedata import normalize
        s = normalize(norm, s)
    return s


def cutName(eventName=""):
    if eventName:
        eventName = eventName.replace('"', '').replace('.', '').replace(' | ', '')  # .replace('Х/Ф', '').replace('М/Ф', '').replace('Х/ф', '')
        eventName = eventName.replace('(18+)', '').replace('18+', '').replace('(16+)', '').replace('16+', '').replace('(12+)', '')
        eventName = eventName.replace('12+', '').replace('(7+)', '').replace('7+', '').replace('(6+)', '').replace('6+', '')
        eventName = eventName.replace('(0+)', '').replace('0+', '').replace('+', '')
        eventName = eventName.replace('المسلسل العربي', '')
        eventName = eventName.replace('مسلسل', '')
        eventName = eventName.replace('برنامج', '')
        eventName = eventName.replace('فيلم وثائقى', '')
        eventName = eventName.replace('حفل', '')
        return eventName
    return ""


def getCleanTitle(eventitle=""):
    # save_name = re.sub('\\(\d+\)$', '', eventitle)
    # save_name = re.sub('\\(\d+\/\d+\)$', '', save_name)  # remove episode-number " (xx/xx)" at the end
    # # save_name = re.sub('\ |\?|\.|\,|\!|\/|\;|\:|\@|\&|\'|\-|\"|\%|\(|\)|\[|\]\#|\+', '', save_name)
    save_name = eventitle.replace(' ^`^s', '').replace(' ^`^y', '')
    return save_name


def convtext(text=''):
    try:
        if text is None:
            print('return None original text:' + str(type(text)))
            return
        if text == '':
            print('text is an empty string')
        if isinstance(text, text_type):
            text = text.encode('utf-8')
        else:
            print('original text:' + text)
            text = text.lower()
            print('lowercased text:' + text)
            text = text.lstrip()
            # # Applica le funzioni di taglio e pulizia del titolo
            # text = cutName(text)
            # text = getCleanTitle(text)
            # Regola il titolo se finisce con "the"
            if text.endswith("the"):
                text = "the " + text[:-4]

            # Modifiche personalizzate
            if 'giochi olimpici parigi' in text:
                text = 'olimpiadi di parigi'
            if 'bruno barbieri' in text:
                text = text.replace('bruno barbieri', 'brunobarbierix')
            if "anni '60" in text:
                text = "anni 60"
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
            if 'alessandro borghese - 4 ristoranti' in text:
                text = 'alessandroborgheseristoranti'
            if 'alessandro borghese: 4 ristoranti' in text:
                text = 'alessandroborgheseristoranti'

            cutlist = ['x264', '720p', '1080p', '1080i', 'pal', 'german', 'english', 'ws', 'dvdrip', 'unrated',
                       'retail', 'web-dl', 'dl', 'ld', 'mic', 'md', 'dvdr', 'bdrip', 'bluray', 'dts', 'uncut', 'anime',
                       'ac3md', 'ac3', 'ac3d', 'ts', 'dvdscr', 'complete', 'internal', 'dtsd', 'xvid', 'divx', 'dubbed',
                       'line.dubbed', 'dd51', 'dvdr9', 'dvdr5', 'h264', 'avc', 'webhdtvrip', 'webhdrip', 'webrip',
                       'webhdtv', 'webhd', 'hdtvrip', 'hdrip', 'hdtv', 'ituneshd', 'repack', 'sync', '1^tv', '1^ tv',
                       '1^ visione rai', '1^ visione', ' - prima tv', ' - primatv', 'prima visione',
                       'film -', 'de filippi', 'first screening',
                       'live:', 'new:', 'film:', 'première diffusion', 'nouveau:', 'en direct:',
                       'premiere:', 'estreno:', 'nueva emisión:', 'en vivo:'
                       ]
            for word in cutlist:
                text = text.replace(word, '')
            text = ' '.join(text.split())
            print(text)

            # Applica le funzioni di taglio e pulizia del titolo
            text = cutName(text)
            text = getCleanTitle(text)

            text = text.partition("-")[0]  # Mantieni solo il testo prima del primo "-"

            # Pulizia finale
            text = text.replace('.', ' ').replace('-', ' ').replace('_', ' ').replace('+', '')

            # Rimozione pattern specifici
            if search(r'[Ss][0-9]+[Ee][0-9]+', text):
                text = sub(r'[Ss][0-9]+[Ee][0-9]+.*[a-zA-Z0-9_]+', '', text, flags=S | I)
            text = sub(r'\(.*\)', '', text).rstrip()
            text = text.partition("(")[0]
            text = sub(r"\\s\d+", "", text)
            text = text.partition(":")[0]
            text = re.sub(r'(odc.\s\d+)+.*?FIN', '', text)
            text = re.sub(r'(odc.\d+)+.*?FIN', '', text)
            text = re.sub(r'(\d+)+.*?FIN', '', text)
            text = re.sub('FIN', '', text)
            # remove episode number in arabic series
            text = re.sub(r'\sح\s*\d+', '', text)
            # remove season number in arabic series
            text = re.sub(r'\sج\s*\d+', '', text)
            # remove season number in arabic series
            text = re.sub(r'\sم\s*\d+', '', text)

            # Rimuovi accenti e normalizza
            text = remove_accents(text)
            print('remove_accents text: ' + text)

            # Forzature finali
            text = text.replace('XXXXXX', '60')
            text = text.replace('brunobarbierix', 'bruno barbieri - 4 hotel')
            text = text.replace('alessandroborgheseristoranti', 'alessandro borghese - 4 ristoranti')
            text = text.replace('il ritorno di colombo', 'colombo')

            # text = sanitize_filename(text)
            # print('sanitize_filename text: ' + text)
            return text.capitalize()
    except Exception as e:
        print('convtext error: ' + str(e))
        pass


def getScale():
    return AVSwitch().getFramebufferScale()


class ZChannel(Renderer):

    def __init__(self):
        adsl = intCheck()
        if not adsl:
            return
        Renderer.__init__(self)
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
            # self.picload = ePicLoad()
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
        if self.event:
            self.evnt = self.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '')
            if self.evnt.endswith(' '):
                self.evnt = self.evnt[:-1]
            self.evntNm = convtext(self.evnt)
            print('zchannel new self event name:', self.evntNm)
            self.dwn_infos = "{}/{}.zstar.txt".format(path_folder, self.evntNm)
            self.dataNm = "{}/{}.txt".format(path_folder, self.evntNm)
            self.pstrNm = "{}/{}.jpg".format(path_folder, self.evntNm)
            poster = ''
            if os.path.exists(self.pstrNm):
                self.showPoster()
            else:
                if os.path.exists(self.dwn_infos) and os.stat(self.dwn_infos).st_size > 1:
                    try:
                        if PY3:
                            with open(self.dwn_infos) as f:
                                data = json.load(f)
                        else:
                            myFile = open(self.dwn_infos, 'r')
                            myObject = myFile.read()
                            u = myObject.decode('utf-8-sig')
                            data = u.encode('utf-8')
                            # data.encoding
                            # data.close()
                            data = json.loads(myObject, 'utf-8')
                        if "poster_path" in data:
                            poster = data['poster_path']
                            if poster and poster != 'null' or poster is not None:
                                self.url_poster = "http://image.tmdb.org/t/p/{}{}".format(formatImg, str(poster))
                                # print('ZChannel dwn_infos poster download')
                                self.savePoster()
                    except Exception as e:
                        print('ZChannel error 1 ', e)
                # forced
                elif os.path.exists(self.dataNm) and os.stat(self.dataNm).st_size > 1:
                    try:
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
                        if "poster_path" in data:
                            poster = data['poster_path']
                            if poster and poster != 'null' or poster is not None:
                                self.url_poster = "http://image.tmdb.org/t/p/{}{}".format(formatImg, str(poster))
                                # print('ZChannel dataNm poster download')
                                self.savePoster()
                    except Exception as e:
                        print('ZChannel error 2 ', e)

                else:
                    servicetype = None
                    try:
                        service = None
                        if isinstance(self.source, ServiceEvent):  # source="ServiceEvent"
                            service = self.source.getCurrentService()
                            servicetype = "ServiceEvent"
                        elif isinstance(self.source, CurrentService):  # source="session.CurrentService"
                            service = self.source.getCurrentServiceRef()
                            servicetype = "CurrentService"
                        elif isinstance(self.source, EventInfo):  # source="session.Event_Now" or source="session.Event_Next"
                            service = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
                            servicetype = "EventInfo"
                        elif isinstance(self.source, Event):  # source="Event"
                            service = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
                            servicetype = "Event"
                        if service:
                            # events = epgcache.lookupEvent(['IBDCTESX', (service.toString(), 0, -1, -1)])
                            if PY3:
                                self.evnt = ServiceReference(service).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '')  # .encode('utf-8')
                            else:
                                self.evnt = ServiceReference(service).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '').encode('utf-8')
                    except Exception as e:
                        print('ZChannel error 3 ', e)
                        if self.instance:
                            self.instance.hide()
                    if not servicetype or servicetype is None:
                        if self.instance:
                            self.instance.hide()
                        return
                    try:
                        if os.path.exists(self.dataNm) and os.stat(self.dataNm).st_size < 1:
                            os.remove(self.dataNm)
                            # print("Zchannel as been removed %s successfully" % self.evntNm)
                        url = 'http://api.themoviedb.org/3/search/tv?api_key={}&query={}'.format(str(tmdb_api), quoteEventName(self.evntNm))
                        if PY3:
                            url = url.encode()
                            url2 = urlopen(url).read()
                        else:
                            url2 = urlopen(url).read().decode('utf-8')
                        jurl = json.loads(url2)
                        if 'results' in jurl:
                            if 'id' in jurl['results'][0]:
                                ids = jurl['results'][0]['id']
                                url_2 = 'http://api.themoviedb.org/3/tv/{}?api_key={}&language={}'.format(str(ids), str(tmdb_api), str(lng))
                                if PY3:
                                    url_2 = url_2.encode()
                                    url_3 = urlopen(url_2).read().read()
                                else:
                                    url_3 = urlopen(url_2).read().decode('utf-8')
                                data2 = json.loads(url_3)
                                with open(self.dataNm, "w") as f:
                                    json.dump(data2, f)
                                poster = data2['poster_path']
                                if poster and poster != 'null' or poster is not None:
                                    self.url_poster = "http://image.tmdb.org/t/p/{}{}".format(formatImg, str(poster))  # w185 risoluzione poster
                                    self.savePoster()
                        else:
                            url = 'http://api.themoviedb.org/3/search/movie?api_key={}&query={}'.format(str(tmdb_api), quoteEventName(self.evntNm))
                            if PY3:
                                url = url.encode()
                                url2 = urlopen(url).read()
                            else:
                                url2 = urlopen(url).read().decode('utf-8')
                            # url2 = urlopen(url).read().decode('utf-8')
                            jurl = json.loads(url2)
                            if 'results' in jurl:
                                if 'id' in jurl['results'][0]:
                                    ids = jurl['results'][0]['id']
                                    url_2 = 'http://api.themoviedb.org/3/movie/{}?api_key={}&language={}'.format(str(ids), str(tmdb_api), str(lng))
                                    if PY3:
                                        url_2 = url_2.encode()
                                    url_3 = urlopen(url_2).read().decode('utf-8')
                                    data2 = json.loads(url_3)
                                    with open(self.dataNm, "w") as f:
                                        json.dump(data2, f)
                                    poster = data2['poster_path']
                                    if poster and poster != 'null' or poster is not None:
                                        self.url_poster = "http://image.tmdb.org/t/p/{}{}".format(formatImg, str(poster))
                                        self.savePoster()
                    except Exception as e:
                        print('ZChannel error 4 ', e)
                        if self.instance:
                            self.instance.hide()

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
        self.picload.setPara([width, height, sc[0], sc[1], 0, 1, 'FF000000'])
        try:
            if self.picload.startDecode(self.pstrNm):
                # if this has failed, then another decode is probably already in progress
                # throw away the old picload and try again immediately
                self.picload = ePicLoad()
                try:
                    self.picload.PictureData.get().append(self.DecodePicture)
                except:
                    self.picload_conn = self.picload.PictureData.connect(self.DecodePicture)
                self.picload.setPara([width, height, sc[0], sc[1], 0, 1, "FF000000"])
                self.picload.startDecode(self.pstrNm)
        except Exception as e:
            print(e)

    def DecodePicture(self, PicInfo=None):
        # print("* DecodePicture *")
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
