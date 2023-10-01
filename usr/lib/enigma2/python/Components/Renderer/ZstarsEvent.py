#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng
# v1 07.2020, 11.2021
# for channellist
# <widget source="ServiceEvent" render="zStarX" position="750,390" size="200,20" alphatest="blend" transparent="1" zPosition="3" />
# or
# <widget source="ServiceEvent" render="zStarX" pixmap="xtra/star.png" position="750,390" size="200,20" alphatest="blend" transparent="1" zPosition="3" />
# edit lululla 05-2022
# <ePixmap pixmap="MetriXconfluencExp/star.png" position="136,104" size="200,20" alphatest="blend" zPosition="10" transparent="1" />
# <widget source="session.Event_Now" render="zStarX" pixmap="MetriXconfluencExp/star.png" position="560,367" size="200,20" alphatest="blend" transparent="1" zPosition="3" />
# <ePixmap pixmap="MetriXconfluencExp/star.png" position="136,104" size="200,20" alphatest="blend" zPosition="10" transparent="1" />
# <widget source="session.Event_Next" render="zStarX" pixmap="MetriXconfluencExp/star.png" position="560,367" size="200,20" alphatest="blend" transparent="1" zPosition="3" />

from __future__ import absolute_import
from Components.Renderer.Renderer import Renderer
from Components.VariableValue import VariableValue
from enigma import eSlider
import os
import re
import json
try:
    from urllib.parse import quote
except:
    from urllib import quote


def isMountReadonly(mnt):
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


folder_poster = "/tmp/poster"
if os.path.exists("/media/hdd"):
    if not isMountReadonly("/media/hdd"):
        folder_poster = "/media/hdd/poster"
elif os.path.exists("/media/usb"):
    if not isMountReadonly("/media/usb"):
        folder_poster = "/media/usb/poster"
elif os.path.exists("/media/mmc"):
    if not isMountReadonly("/media/mmc"):
        folder_poster = "/media/mmc/poster"
else:
    folder_poster = "/tmp/poster"

if not os.path.exists(folder_poster):
    os.makedirs(folder_poster)
if not os.path.exists(folder_poster):
    folder_poster = "/tmp/poster"

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


class ZstarsEvent(VariableValue, Renderer):
    def __init__(self):
        Renderer.__init__(self)
        VariableValue.__init__(self)
        self.__start = 0
        self.__end = 100

    GUI_WIDGET = eSlider

    def changed(self, what):
        if what[0] == self.CHANGED_CLEAR:
            (self.range, self.value) = ((0, 1), 0)
            return
        if what[0] != self.CHANGED_CLEAR:
            print('zstar event what[0] != self.CHANGED_CLEAR')
            rtng = 0
            range = 0
            value = 0
            try:
                self.event = self.source.event
                if self.event:  # and self.instance:
                    evnt = self.event.getEventName().encode('utf-8')
                    self.evnt = cleantitle(evnt)
                    rating_json = os.path.join(folder_poster, "url_rate")
                    if os.path.exists(rating_json) and os.stat(rating_json).st_size > 0:
                        with open(rating_json) as f:
                            try:
                                rating = json.load(f)['vote_average']
                            except:
                                rating = json.load(f)['imdbRating']
                        if rating:
                            rtng = int(10 * (float(rating)))
                        else:
                            rtng = 0
                    else:
                        rtng = 0
                else:
                    rtng = 0
                print('value d ', rtng)

            except Exception as e:
                print('my e ', str(e))

            range = 100
            value = rtng
            (self.range, self.value) = ((0, range), value)

    def postWidgetCreate(self, instance):
        instance.setRange(self.__start, self.__end)

    def setRange(self, range):
        (self.__start, self.__end) = range
        if self.instance is not None:
            self.instance.setRange(self.__start, self.__end)

    def getRange(self):
        return self.__start, self.__end

    range = property(getRange, setRange)
