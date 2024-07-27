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
from enigma import ePixmap, ePicLoad
from enigma import getDesktop
import NavigationInstance
import json
import os
import re
import shutil
import socket
import sys
# import unicodedata
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
            text = cutName(text)
            text = getCleanTitle(text)
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
            text = text.strip(' -')
            text = quote(text, safe="")
            print('ZstarsEvent Final text: ', text)
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


try:
    folder_size = sum([sum(map(lambda fname: os.path.getsize(os.path.join(path_folder, fname)), files)) for folder_p, folders, files in os.walk(path_folder)])
    ozposter = "%0.f" % (folder_size / (1024 * 1024.0))
    if ozposter >= "5":
        shutil.rmtree(path_folder)
except:
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
                            # print('zchannel part one')
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
                            # print('zchannel part two')
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
        sc = getScale()  # AVSwitch().getFramebufferScale()
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
        with open(self.pstrNm, 'wb') as f:
            f.write(urlopen(self.url_poster).read())
            f.flush()
            f.close()
            file_size = os.path.getsize(self.pstrNm)
            if file_size == 0:
                os.remove(self.pstrNm)
            else:
                print('poster downlaoded:', self.pstrNm)

        # if os.path.exists(self.pstrNm):
            # print('ZChannel save poster show ')
            self.showPoster()
        return
