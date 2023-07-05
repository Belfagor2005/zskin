#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng...07.2021
# russian and py3 support by sunriser...
# 07.2021 start edit lululla
# <widget source="session.Event_Now" render="ZPBorder" position="1620,505" size="300,438" alphatest="blend" trasparent="1" zPosition="8" />
from Components.Renderer.Renderer import Renderer
from Components.AVSwitch import AVSwitch
from Components.config import config
from Tools.Directories import fileExists
from enigma import ePixmap, ePicLoad, eTimer
import os
import re

global cur_skin

path_folder = "/tmp/poster/"
if os.path.isdir("/media/hdd"):
    path_folder = "/media/hdd/poster/"
elif os.path.isdir("/media/usb"):
    path_folder = "/media/usb/poster/"
else:
    path_folder = "/tmp/poster/"
if not os.path.isdir(path_folder):
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


class ZPBorder(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        self.timer40 = eTimer()

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if self.timer40:
            self.timer40.stop()
        if what[0] == self.CHANGED_CLEAR:
            self.instance.hide()
        if what[0] != self.CHANGED_CLEAR:
            self.delay()

    def delay(self):
        self.downloading = False
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
            else:
                self.instance.hide()
        else:
            self.instance.hide()

    def info(self):
        if self.downloading:
            return
        self.evnt = ''
        self.pstrNm = ''
        self.evntNm = ''
        self.downloading = False
        self.event = self.source.event
        if self.event:
            # self.evnt = self.event.getEventName()
            # self.evntNm = REGEX.sub('', self.evnt).strip()
            
            self.evnt = self.event.getEventName()
            self.evntNm = REGEX.sub('', self.evnt).strip()
            self.evntNm = self.evntNm.replace('\xc2\x86', '').replace('\xc2\x87', '')
            
            print('clean event Zborder: ', self.evntNm)
            self.pstrNm = "/tmp/ZPoster/{}.jpg".format(self.evntNm)
            if fileExists(self.pstrNm) and self.instance:
                print('fileExists')
                self.showPoster()
                self.timer40.stop()
            else:
                self.instance.hide()
                self.timer40.stop()
        else:
            self.instance.hide()
            self.timer40.stop()
            return
