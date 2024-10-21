#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng...07.2021
# russian and py3 support by sunriser...
# 07.2021 start edit lululla
# edit by lululla 07.2022
# recode from lululla 2023
# <widget source="session.Event_Now" render="ZPBorder" position="1620,505" size="300,438" alphatest="blend" trasparent="1" zPosition="8" />
from Components.AVSwitch import AVSwitch
from Components.Renderer.Renderer import Renderer
from Components.config import config
from Tools.Directories import fileExists
from enigma import ePixmap, ePicLoad
import os
import re
import sys
import socket

global cur_skin

PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    unicode = str
    unichr = chr
    long = int
    from urllib.parse import quote_plus, quote
else:
    from urllib import quote_plus, quote


if sys.version_info[0] >= 3:
    from urllib.error import HTTPError, URLError
    from urllib.request import urlopen

else:
    from urllib2 import HTTPError, URLError
    from urllib2 import urlopen


try:
    from urllib import unquote
except ImportError:
    from urllib.parse import unquote


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
            print('original text:', text)
                                         
            text = text.lower()
            print('lowercased text:', text)
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
            text = text.replace("\xe2\x80\x93", "").replace('\xc2\x86', '').replace('\xc2\x87', '')  # replace special
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

            text = text + 'FIN'
            if re.search(r'[Ss][0-9][Ee][0-9]+.*?FIN', text):
                text = re.sub(r'[Ss][0-9][Ee][0-9]+.*?FIN', '', text)
            if re.search(r'[Ss][0-9] [Ee][0-9]+.*?FIN', text):
                text = re.sub(r'[Ss][0-9] [Ee][0-9]+.*?FIN', '', text)
            text = re.sub(r'(odc.\s\d+)+.*?FIN', '', text)
            text = re.sub(r'(odc.\d+)+.*?FIN', '', text)
            text = re.sub(r'(\d+)+.*?FIN', '', text)
            text = text.partition("(")[0] + 'FIN'  # .strip()
            # text = re.sub("\\s\d+", "", text)
            text = text.partition("(")[0]  # .strip()
            text = text.partition(":")[0]  # .strip()
            text = text.partition(" -")[0]  # .strip()
            text = re.sub(' - +.+?FIN', '', text)  # all episodes and series ????
            text = re.sub('FIN', '', text)
            text = re.sub(r'^\|[\w\-\|]*\|', '', text)
            text = re.sub(r"[-,?!/\.\":]", '', text)  # replace (- or , or ! or / or . or " or :) by space

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


class ZPBorder(Renderer):
    def __init__(self):
        adsl = intCheck()
        if not adsl:
            return
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

    def showBorder(self):
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

    def info(self):
        if self.downloading:
            return
        self.evnt = ''
        self.pstrNm = ''
        self.evntNm = ''
        self.downloading = False
        self.event = self.source.event
        if self.event:
            self.evnt = self.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '')
            if self.evnt.endswith(' '):
                self.evnt = self.evnt[:-1]
            self.evntNm = convtext(self.evnt)
            print('zborder clean Zborder: ', self.evntNm)
            self.pstrNm = "{}/{}.jpg".format(path_folder, self.evntNm)
            print('zborder self.pstrNm: ', self.pstrNm)
            if fileExists(self.pstrNm) and self.instance:
                print('zborder fileExists')
                self.showBorder()
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
