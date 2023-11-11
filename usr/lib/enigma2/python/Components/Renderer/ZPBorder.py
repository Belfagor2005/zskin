#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng...07.2021
# russian and py3 support by sunriser...
# 07.2021 start edit lululla
# edit by lululla 07.2022
# recode from lululla 2023
# <widget source="session.Event_Now" render="ZPBorder" position="1620,505" size="300,438" alphatest="blend" trasparent="1" zPosition="8" />
from Components.Renderer.Renderer import Renderer
from Components.AVSwitch import AVSwitch
from Components.config import config
from Tools.Directories import fileExists
from enigma import ePixmap, ePicLoad, eTimer
import os
import re

global cur_skin


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


cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
nocover = '/usr/share/enigma2/%s/menu/panels/nocover.png' % cur_skin
border = '/usr/share/enigma2/%s/menu/panels/border.png' % cur_skin

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


def convtext(text=''):
    try:
        if text != '' or text is not None or text != 'None':
            text = REGEX.sub('', text)
            text = re.sub(r"[-,?!/\.\":]", '', text)  # replace (- or , or ! or / or . or " or :) by space
            text = re.sub(r'\s{1,}', ' ', text)  # replace multiple space by one space
            text = re.sub('\ \(\d+\)$', '', text)  # remove episode-number " (xxx)" at the end
            text = re.sub('\ \(\d+\/\d+\)$', '', text)  # remove episode-number " (xx/xx)" at the end
            text = text.replace('PrimaTv', '').replace(' mag', '')
            text = text.replace(' prima pagina', '')
            # text = text.replace(' 6', '').replace(' 7', '').replace(' 8', '').replace(' 9', '').replace(' 10', '')
            # text = text.replace(' 11', '').replace(' 12', '').replace(' 13', '').replace(' 14', '').replace(' 15', '')
            # text = text.replace(' 16', '').replace(' 17', '').replace(' 18', '').replace(' 19', '').replace(' 20', '')
            text = unicodify(text)
            text = text.lower()
        else:
            text = text
        return text
    except Exception as e:
        print('convtext error: ', e)
        pass


class ZPBorder(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        self.timer40 = eTimer()
        self.downloading = False

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if what[0] == self.CHANGED_CLEAR:
            if self.instance:
                self.instance.hide()
        if what[0] != self.CHANGED_CLEAR:
            print('zborder what[0] != self.CHANGED_CLEAR: ')
            self.delay()

    def delay(self):
        try:
            self.timer40.callback.append(self.info)
        except:
            self.timer40_conn = self.timer40.timeout.connect(self.info)
        self.timer40.start(250, False)

    def showPoster(self):
        border = '/usr/share/enigma2/%s/menu/panels/border.png' % cur_skin
        self.border = border
        size = self.instance.size()
        self.picload = ePicLoad()
        sc = AVSwitch().getFramebufferScale()
        if self.picload:
            self.picload.setPara([size.width(), size.height(), sc[0], sc[1], False, 1, '#00000000'])
            if os.path.exists('/var/lib/dpkg/status'):
                self.picload.startDecode(self.border, False)
            else:
                self.picload.startDecode(self.border, 0, 0, False)
            ptr = self.picload.getData()
            if ptr is not None:
                self.instance.setPixmap(ptr)
                self.instance.show()
            # else:
                # if self.instance:
                    # self.instance.hide()
        # else:
            # if self.instance:
                # self.instance.hide()

    def info(self):
        if self.downloading:
            return
        self.evnt = ''
        self.pstrNm = ''
        self.evntNm = ''
        self.downloading = False
        self.event = self.source.event
        if self.event:
            self.evnt = self.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '').encode('utf-8')
            self.evntNm = convtext(self.evnt)
            print('zborder clean Zborder: ', self.evntNm)
            self.pstrNm = "{}/{}.jpg".format(path_folder, self.evntNm)
            print('zborder self.pstrNm: ', self.pstrNm)
            if fileExists(self.pstrNm) and self.instance:
                print('zborder fileExists')
                self.showPoster()
                self.timer40.stop()
            else:
                if self.instance:
                    self.instance.hide()
                self.timer40.stop()
        else:
            if self.instance:
                self.instance.hide()
            self.timer40.stop()
            return
