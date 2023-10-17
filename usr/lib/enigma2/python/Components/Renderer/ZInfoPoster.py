#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng...07.2021
# russian and py3 support by sunriser..
# 07.2021 start edit lululla
# <widget source="session.Event_Now" render="ZPBorder" position="1585,240" size="330,487" zPosition="5" />
# <widget source="session.Event_Now" render="ZInfoPoster" position="1585,310" size="320,467" zPosition="6" />
# or
# <widget source="session.Event_Now" render="ZInfoPoster" position="1620,505" size="300,438" alphatest="blend" zPosition="9" />
# <widget source="session.Event_Next" render="ZInfoPoster" position="1620,505" size="300,438" alphatest="blend" zPosition="9" />
from Components.Renderer.Renderer import Renderer

from Components.AVSwitch import AVSwitch
from Tools.Directories import fileExists
from enigma import ePixmap, eTimer, ePicLoad
import os
import re


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


path_folder = "/tmp/poster/"
if os.path.exists("/media/hdd"):
    if not isMountReadonly("/media/hdd"):
        path_folder = "/media/hdd/poster/"
elif os.path.exists("/media/usb"):
    if not isMountReadonly("/media/usb"):
        path_folder = "/media/usb/poster/"
elif os.path.exists("/media/mmc"):
    if not isMountReadonly("/media/mmc"):
        path_folder = "/media/mmc/poster/"

if not os.path.exists(path_folder):
    os.makedirs(path_folder)


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
            text = unicodify(text)
            text = text.lower()
            print('ZstarsEvent text <<<- ', text)
        else:
            text = str(text)
            print('ZstarsEvent text <<<->>> ', text)
        return text
    except Exception as e:
        print('cleantitle error: ', e)
        pass


class ZInfoPoster(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        self.timer50 = eTimer()

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if what[0] == self.CHANGED_CLEAR:
            self.instance.hide()
        else:
            self.delay()

    def delay(self):
        try:
            self.timer50.callback.append(self.info)
        except:
            self.timer50_conn = self.timer50.timeout.connect(self.info)
        self.timer50.start(150, False)

    def showPoster(self):
        size = self.instance.size()
        self.picload = ePicLoad()
        sc = AVSwitch().getFramebufferScale()
        if self.picload:
            self.picload.setPara([size.width(), size.height(), sc[0], sc[1], False, 1, '#00000000'])
            if os.path.exists('/var/lib/dpkg/status'):
                self.picload.startDecode(self.pstrNm, False)
            else:
                self.picload.startDecode(self.pstrNm, 0, 0, False)
        ptr = self.picload.getData()
        if ptr is not None:
            self.instance.setPixmap(ptr)
            self.instance.show()
        del self.picload

    def info(self):
        self.evnt = ''
        self.pstrNm = ''
        self.evntNm = ''
        self.event = self.source.event
        if self.event:   # and self.instance:
            self.evnt = self.event.getEventName().encode('utf-8')
            self.evntNm = cleantitle(self.evnt)
            print('clean event Zchannel: ', self.evntNm)
            self.pstrNm = "{}/{}.jpg".format(path_folder, self.evntNm)
            print('self.pstrNm: ', self.pstrNm)
            # self.evnt = self.event.getEventName()
            # self.evntNm = REGEX.sub('', self.evnt).strip()
            # self.evntNm = self.evntNm.replace('\xc2\x86', '').replace('\xc2\x87', '')
            # print('clean event zinfo poster: ', self.evntNm)
            # self.pstrNm = "{}{}.jpg".format(path_folder, self.evntNm)
            if fileExists(self.pstrNm):
                self.timer50.stop()
                self.showPoster()
