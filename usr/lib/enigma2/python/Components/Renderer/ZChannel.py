#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng...07.2021
# russian and py3 support by sunriser...
# 07.2021 start edit lululla
# edit by lululla 07.2022
# recode from lululla 2023

from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, ePicLoad
from Components.AVSwitch import AVSwitch
from Components.config import config
import re
import json
import os
import socket
import shutil
import sys
from enigma import gPixmapPtr
from Components.Sources.CurrentService import CurrentService
from Components.Sources.Event import Event
from Components.Sources.EventInfo import EventInfo
from Components.Sources.ServiceEvent import ServiceEvent
from ServiceReference import ServiceReference
from enigma import getDesktop
import unicodedata
import NavigationInstance
global cur_skin, my_cur_skin

PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    unicode = str
    unichr = chr
    long = int
    from urllib.error import URLError, HTTPError
    from urllib.request import urlopen
    from urllib.parse import quote
else:
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
tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
omdb_api = "cb1d9f55"
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
    lng = config.osd.language.value
    lng = lng[:-3]
except:
    lng = 'en'
    pass
# print('language: ', lng)


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


# def getCleanContentTitle(event_title=""):
        # cleanEvent = event_title.replace("\xe2\x80\x93","-") # replace special '-'
        # cleanEvent = cleanEvent.replace("’","'")
        # cleanEvent = cleanEvent.replace('"',"")
        # cleanEvent = re.sub('\' ', ' ', cleanEvent)
        # cleanEvent = re.sub('\: ', ' - ', cleanEvent)
        # cleanEvent = re.sub('\ \(Director\'s\ Cut\)$', '', cleanEvent)
        # cleanEvent = re.sub('\ \Director\'s\ Cut\$', '', cleanEvent)
        # cleanEvent = re.sub('\ \(Uncut\)$', '', cleanEvent)
        # cleanEvent = re.sub('\ \[Uncut\]$', '', cleanEvent)
        # cleanEvent = re.sub('\ \Extended Director\'s Cut\$', '', cleanEvent)
        # cleanEvent = re.sub('\ \(Extended Version\)$', '', cleanEvent)
        # cleanEvent = re.sub('\ \(XXL-Version\)$', '', cleanEvent)
        # cleanEvent = re.sub('\ \(\d+\)$', '', cleanEvent) #remove episode-number " (xxx)" at the end
        # cleanEvent = re.sub('\ \(\d+\/\d+\)$', '', cleanEvent) #remove episode-number " (xx/xx)" at the end
        # cleanEvent = re.sub('\!+$', '', cleanEvent)
        # return str(cleanEvent.strip())


# def transEpis(text):
    # text = text.lower() + '+FIN'
    # text = text.replace('  ', '+').replace(' ', '+').replace('&', '+').replace(':', '+').replace('_', '+').replace('u.s.', 'us').replace('l.a.', 'la').replace('.', '+').replace('"', '+').replace('(', '+').replace(')', '+').replace('[', '+').replace(']', '+').replace('!', '+').replace('++++', '+').replace('+++', '+').replace('++', '+')
    # text = text.replace('+720p+', '++').replace('+1080i+', '+').replace('+1080p+', '++').replace('+dtshd+', '++').replace('+dtsrd+', '++').replace('+dtsd+', '++').replace('+dts+', '++').replace('+dd5+', '++').replace('+5+1+', '++').replace('+3d+', '++').replace('+ac3d+', '++').replace('+ac3+', '++').replace('+avchd+', '++').replace('+avc+', '++').replace('+dubbed+', '++').replace('+subbed+', '++').replace('+stereo+', '++')
    # text = text.replace('+x264+', '++').replace('+mpeg2+', '++').replace('+avi+', '++').replace('+xvid+', '++').replace('+blu+', '++').replace('+ray+', '++').replace('+bluray+', '++').replace('+3dbd+', '++').replace('+bd+', '++').replace('+bdrip+', '++').replace('+dvdrip+', '++').replace('+rip+', '++').replace('+hdtv+', '++').replace('+hddvd+', '++')
    # text = text.replace('+german+', '++').replace('+ger+', '++').replace('+english+', '++').replace('+eng+', '++').replace('+spanish+', '++').replace('+spa+', '++').replace('+italian+', '++').replace('+ita+', '++').replace('+russian+', '++').replace('+rus+', '++').replace('+dl+', '++').replace('+dc+', '++').replace('+sbs+', '++').replace('+se+', '++').replace('+ws+', '++').replace('+cee+', '++')
    # text = text.replace('+remux+', '++').replace('+directors+', '++').replace('+cut+', '++').replace('+uncut+', '++').replace('+extended+', '++').replace('+repack+', '++').replace('+unrated+', '++').replace('+rated+', '++').replace('+retail+', '++').replace('+remastered+', '++').replace('+edition+', '++').replace('+version+', '++')
    # text = text.replace('\xc3\x9f', '%C3%9F').replace('\xc3\xa4', '%C3%A4').replace('\xc3\xb6', '%C3%B6').replace('\xc3\xbc', '%C3%BC')
    # text = re.sub('\\+tt[0-9]+\\+', '++', text)
    # text = re.sub('\\+\\+\\+\\+.*?FIN', '', text)
    # text = re.sub('\\+FIN', '', text)
    # return text


def convtext(text=''):
    try:
        if text != '' or text is not None or text != 'None':
            print('original text: ', text)
            text = text.replace("\xe2\x80\x93", "").replace('\xc2\x86', '').replace('\xc2\x87', '')  # replace special
            text = text.lower()
            text = text.replace('1^ visione rai', '').replace('1^ visione', '').replace('primatv', '').replace('1^tv', '').replace('1^ tv', '')
            text = text.replace('prima visione', '')
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
            if text.endswith("the"):
                text.rsplit(" ", 1)[0]
                text = text.rsplit(" ", 1)[0]
                text = "the " + str(text)
                print('the from last to start text: ', text)
            text = text + 'FIN'
            # text = re.sub("[^\w\s]", "", text)  # remove .
            text = re.sub(' [\:][a-z0-9]+.*?FIN', '', text)
            text = re.sub(' [\:][ ][a-z0-9]+.*?FIN', '', text)
            text = re.sub(' [\(][ ][a-z0-9]+.*?FIN', '', text)
            text = re.sub(' [\-][ ][a-z0-9]+.*?FIN', '', text)
            print('[(00)] ', text)

            if re.search('[Ss][0-9]+[Ee][0-9]+.*?FIN', text):
                text = re.sub('[Ss][0-9]+[Ee][0-9]+.*[a-zA-Z0-9_]+.*?FIN', '', text, flags=re.S|re.I)
            if re.search('[Ss][0-9] [Ee][0-9]+.*?FIN', text):
                text = re.sub('[Ss][0-9] [Ee][0-9]+.*[a-zA-Z0-9_]+.*?FIN', '', text, flags=re.S|re.I)
            # if re.search(' - [Ss][0-9] [Ee][0-9]+.*?FIN', text):
                # text = re.sub(' - [Ss][0-9] [Ee][0-9]+.*?FIN', '', text, flags=re.S|re.I)
            # if re.search(' - [Ss][0-9]+[Ee][0-9]+.*?FIN', text):
                # text = re.sub(' - [Ss][0-9]+[Ee][0-9]+.*?FIN', '', text, flags=re.S|re.I)
            # # text = re.sub("([\(\[]).*?([\)\]])|(: odc.\d+)|(\d+: odc.\d+)|(\d+ odc.\d+)|(:)|( -(.*?).*)|(,)|!|\+.*?FIN", "", text)
            text = text.partition("(")[0]  # .strip()
            text = text.partition(":")[0]  # .strip()
            text = text.partition("-")[0]  # .strip()
            print('[(01)] ', text)
            text = re.sub(' - +.+?FIN', '', text)  # all episodes and series ????
            text = re.sub('FIN', '', text)
            print('[(02)] ', text)
            text = REGEX.sub('', text)  # paused
            print('[(03)] ', text)
            text = re.sub(r'^\|[\w\-\|]*\|', '', text)
            text = re.sub(r"[-,?!/\.\":]", '', text)  # replace (- or , or ! or / or . or " or :) by space
            # text = unicodify(text)
            text = remove_accents(text)
            text = text.strip()
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
        # if not self.instance:
            # print('not istance')
            # return
        if what[0] == self.CHANGED_CLEAR:
            print('zchannel A what[0] == self.CHANGED_CLEAR')
            # return
        if what[0] != self.CHANGED_CLEAR:
            print('zchannel B what[0] != self.CHANGED_CLEAR')
            if self.instance:
                self.instance.hide()
            self.picload = ePicLoad()
            try:
                self.picload.PictureData.get().append(self.DecodePicture)
            except:
                self.picload_conn = self.picload.PictureData.connect(self.DecodePicture)
            self.delay()
        # return

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
        if self.event:  # and self.instance:
            print('ZChannel self event true')
            # self.evnt = self.event.getEventName()  # .replace('\xc2\x86', '').replace('\xc2\x87', '').encode('utf-8')
            # self.evntNm = convtext(self.evnt.encode('utf-8'))

            self.evnt = self.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '')
            self.evntNm = convtext(self.evnt)
            print('zchannel new self event name :', self.evntNm)

            self.dwn_infos = "{}/{}.zstar.txt".format(path_folder, self.evntNm)
            self.dataNm = "{}/{}.txt".format(path_folder, self.evntNm)
            self.pstrNm = "{}/{}.jpg".format(path_folder, self.evntNm)
            if os.path.exists(self.pstrNm):
                self.showPoster()
            else:
                if os.path.exists(self.dwn_infos) and os.stat(self.dwn_infos).st_size > 1:
                    try:
                        if not PY3:
                            myFile = open(self.dwn_infos, 'r')
                            myObject = myFile.read()
                            u = myObject.decode('utf-8-sig')
                            data = u.encode('utf-8')
                            # data.encoding
                            # data.close()
                            data = json.loads(myObject, 'utf-8')
                        else:
                            with open(self.dwn_infos) as f:
                                data = json.load(f)
                        poster = ''
                        if "poster_path" in data:
                            poster = data['poster_path']
                            if poster and poster != 'null' or poster is not None:
                                self.url_poster = "http://image.tmdb.org/t/p/{}{}".format(formatImg, str(poster))
                                print('ZChannel dwn_infos poster download')
                                self.savePoster()
                    except Exception as e:
                        print('ZChannel error 1 ', e)
                # forced
                elif os.path.exists(self.dataNm) and os.stat(self.dataNm).st_size > 1:
                    try:
                        if not PY3:
                            myFile = open(self.dataNm, 'r')
                            myObject = myFile.read()
                            u = myObject.decode('utf-8-sig')
                            data = u.encode('utf-8')
                            # data.encoding
                            # data.close()
                            data = json.loads(myObject, 'utf-8')
                        else:
                            with open(self.dataNm) as f:
                                data = json.load(f)
                        poster = ''
                        if "poster_path" in data:
                            poster = data['poster_path']
                            if poster and poster != 'null' or poster is not None:
                                self.url_poster = "http://image.tmdb.org/t/p/{}{}".format(formatImg, str(poster))
                                print('ZChannel dataNm poster download')
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
                    if not servicetype:
                        if self.instance:
                            self.instance.hide()
                        return
                    try:
                        try:
                            if os.path.exists(self.dataNm) and os.stat(self.dataNm).st_size < 1:
                                os.remove(self.dataNm)
                                print("Zchannel as been removed %s successfully" % self.evntNm)
                            url = 'http://api.themoviedb.org/3/search/tv?api_key={}&query={}'.format(str(tmdb_api), quote(self.evntNm))
                            if PY3:
                                url = url.encode()
                            if not PY3:
                                url2 = urlopen(url).read().decode('utf-8')
                            else:
                                url2 = urlopen(url).read()
                            jurl = json.loads(url2)
                            if 'results' in jurl:
                                if 'id' in jurl['results'][0]:
                                    ids = jurl['results'][0]['id']
                                    url_2 = 'http://api.themoviedb.org/3/tv/{}?api_key={}&language={}'.format(str(ids), str(tmdb_api), str(lng))
                                    if PY3:
                                        url_2 = url_2.encode()

                                    if not PY3:
                                        url_3 = urlopen(url_2).read().decode('utf-8')
                                    else:
                                        url_3 = urlopen(url_2).read().read()
                                    # url_3 = urlopen(url_2).read().decode('utf-8')
                                    data2 = json.loads(url_3)
                                    with open(self.dataNm, "w") as f:
                                        json.dump(data2, f)
                                    poster = data2['poster_path']
                                    if poster and poster != 'null' or poster is not None:
                                        self.url_poster = "http://image.tmdb.org/t/p/{}{}".format(formatImg, str(poster))  # w185 risoluzione poster
                                        self.savePoster()
                            else:
                                url = 'http://api.themoviedb.org/3/search/movie?api_key={}&query={}'.format(str(tmdb_api), quote(self.evntNm))
                                if PY3:
                                    url = url.encode()

                                if not PY3:
                                    url2 = urlopen(url).read().decode('utf-8')
                                else:
                                    url2 = urlopen(url).read()

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
                    except Exception as e:
                        print('ZChannel error except zchannel ', e)
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
                # self.picload.setPara([size.width(), size.height(), sc[0], sc[1], 0, 1, "FF000000"])
                print('ZChannel picload.startDecode poster')
                self.picload.startDecode(self.pstrNm)
        except Exception as e:
            print(e)

    def DecodePicture(self, PicInfo=None):
        # print("* DecodePicture *")
        ptr = self.picload.getData()
        if ptr is not None:
            print('ZChannel ptr is true')
            self.instance.setPixmap(ptr)
            self.instance.show()

    def savePoster(self):
        if os.path.exists(self.pstrNm):
            print('ZChannel save poster show ')
            self.showPoster()
            return

        data = urlopen(self.url_poster)
        with open(self.pstrNm, "wb") as local_file:
            local_file.write(data.read())
            if os.path.exists(self.pstrNm):
                print('ZChannel save poster show ')
                self.showPoster()
        # return