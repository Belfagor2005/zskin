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
import sys
global cur_skin

PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    unicode = str
    unichr = chr
    long = int

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
            text = text.replace("\xe2\x80\x93","").replace('\xc2\x86', '').replace('\xc2\x87', '') # replace special
            print('\xe2\x80\x93 text: ', text)
            text = text.lower()
            text = text.replace('studio aperto mag', 'Studio Aperto').replace('primatv', '').replace('1^tv', '')
            text = text.replace(' prima pagina', '').replace(' -20.30', '').replace(': parte 2', '').replace(': parte 1', '')
            if text.endswith("the"):
                text.rsplit(" ", 1)[0]
                text = text.rsplit(" ", 1)[0]
                text = "the " + str(text)
                print('the from last to start text: ', text)
            text = text + 'FIN'
            text = re.sub(' - [Ss][0-9]+[Ee][0-9]+.*?FIN', '', text)
            text = re.sub('[Ss][0-9]+[Ee][0-9]+.*?FIN', '', text)
            text = re.sub('FIN', '', text)
            # text = transEpis(text)
            # text = text.replace('+', ' ')
            print('transEpis text: ', text)

            text = text.replace(' .', '.').replace('  ', ' ').replace(' - ', ' ').replace(' - "', '')

            # text = REGEX.sub('', text)  # paused
            # # add
            # text = text.replace("\xe2\x80\x93","").replace('\xc2\x86', '').replace('\xc2\x87', '') # replace special
            # # add end

            # # add
            # remove || content at start
            text = re.sub(r'^\|[\w\-\|]*\|', '', text)
            print('^\|[\w\-\|]*\| text: ', text)
            # remove () content
            n = 1  # run at least once
            while n:
                text, n = re.subn(r'\([^\(\)]*\)', '', text)
            print('\([^\(\)]*\) text: ', text)
            # remove [] content
            n = 1  # run at least once
            while n:
                text, n = re.subn(r'\[[^\[\]]*\]', '', text)
            print('\[[^\[\]]*\] text: ', text)
            # # add end

            text = re.sub('\ \(\d+\/\d+\)$', '', text)  # remove episode-number " (xx/xx)" at the end
            text = re.sub('\ \(\d+\)$', '', text)  # remove episode-number " (xxx)" at the end
            text = re.sub(r"[-,?!/\.\":]", '', text)  # replace (- or , or ! or / or . or " or :) by space
            print('[-,?!/\.\":] text: ', text)

            # text = re.sub(r'\s{1,}', ' ', text)  # replace multiple space by one space
            # # add
            # text = re.sub('\ |\?|\.|\,|\!|\/|\;|\:|\@|\&|\'|\-|\"|\%|\(|\)|\[|\]\#|\+', '', text)  # modifcare questo (remove space from regex)
            # text = re.sub('\?|\.|\,|\!|\/|\;|\:|\@|\&|\'|\-|\"|\%|\(|\)|\[|\]\#|\+', '', text)  # modifcare questo (remove space from regex)
            print('\?|\.|\,|\!|\/|\;|\:|\@|\&|\'|\-|\"|\%|\(|\)|\[|\]\#|\+', text)
            # # text = text.replace(' ^`^s', '').replace(' ^`^y','')
            # text = re.sub('\Teil\d+$', '', text)
            # text = re.sub('\Folge\d+$', '', text)
            # # add end

            text = unicodify(text)
            text = text.capitalize()
            print('Final text: ', text)
        else:
            text = text
        return text
    except Exception as e:
        print('convtext error: ', e)
        pass


class ZPBorder(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        # self.timer40 = eTimer()
        self.downloading = False

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if what[0] == self.CHANGED_CLEAR:
            if self.instance:
                self.instance.hide()
        if what[0] != self.CHANGED_CLEAR:
            print('zborder what[0] != self.CHANGED_CLEAR: ')
            # self.delay()
            self.info()

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
                # self.timer40.stop()
            else:
                if self.instance:
                    self.instance.hide()
                # self.timer40.stop()
        else:
            if self.instance:
                self.instance.hide()
            # self.timer40.stop()
            return
