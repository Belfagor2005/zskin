#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import _, PLUGIN_PATH, PLUGIN_NAME
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from Components.config import config
from Components.config import getConfigListEntry
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Tools.Directories import SCOPE_SKIN
from Tools.Directories import fileExists, resolveFilename
from enigma import eTimer
from shutil import copy2
import os
import sys
from .style_ops import getSkinName, isSkinChanged
from .style import Skin
from .addons.Utils import RequestAgent
PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    unicode = str
    unichr = chr
    long = int

try:
    from enigma import eMediaDatabase  # @UnresolvedImport @UnusedImport
    isDreamOS = True
except:
    isDreamOS = False


global apis, apis2, zaddon
apis = False
apis2 = False
mvi = '/usr/share/'
cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
tmdb_skin = "%senigma2/%s/apikey" % (mvi, cur_skin)
omdb_skin = "%senigma2/%s/omdbkey" % (mvi, cur_skin)
visual_skin = "/etc/enigma2/VisualWeather/apikey.txt"
thetvdb_skin = "%senigma2/%s/thetvdbkey" % (mvi, cur_skin)
# tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
# omdb_api = "cb1d9f55"
# visual_api = "5KAUFAYCDLUYVQPNXPN3K24V5"
# thetvdbkey = 'D19315B88B2DE21F'

global tarfile
tarfile = ''
zaddon = False
zaddons = '/usr/lib/enigma2/python/Plugins/SystemPlugins/zStyles/addons'
if os.path.exists(zaddons):
    zaddon = True


class StylesSetup(Screen, ConfigListScreen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.onChangedEntry = []
        self["setupActions"] = ActionMap(["ColorActions", "OkCancelActions", "MenuActions", "NumberActions", "VirtualKeyboardActions", "DirectionActions"],
                {
                "ok": self.keyOk,
                "cancel": self.keyCancel,
                "left": self.keyLeft,
                "right": self.keyRight,
                "red": self.keyCancel,
                "green": self.keySave,
                "yellow": self.keyOpenSkinselector,
                "showVirtualKeyboard": self.KeyText,
                "blue": self.checkSkin,
                '5': self.answercheck,
                }, -2)
        self["key_red"] = StaticText(_("Close"))
        self["key_green"] = StaticText(_("Save"))
        self["key_yellow"] = StaticText(self.getSkinSelector() is not None and "Skin" or "")
        self["key_blue"] = StaticText(_("Reset skin"))
        self.setup_title = PLUGIN_NAME
        self.list = []
        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)
        self.createSetup()
        self.onLayoutFinish.append(self.layoutFinished)
        self.current_skin = config.skin.primary_skin.value

    def answercheck(self, answer=None):
        if answer is None:
            self.session.openWithCallback(self.answercheck, MessageBox, _("This operation checks if the skin has its components (is not sure)..\nDo you really want to continue?"), MessageBox.TYPE_YESNO)
        else:
            self.check_module = eTimer()
            if isDreamOS:
                self.check_module_conn = self.check_module.timeout.connect(self.checki)
            else:
                self.check_module.callback.append(self.checki)
            self.check_module.start(300, True)

    def checki(self):
        if zaddon is True:
            from .addons import checkskin
            checkskin.check_module_skin()
            self.openVi()

    def openVi(self):
        from .addons.type_utils import zEditor
        user_log = '/tmp/debug_my_skin.log'
        if fileExists(user_log):
            self.session.open(zEditor, user_log)

    def createSetup(self):
        self.editListEntry = None
        self.list = []
        # self.list.append(getConfigListEntry(_("Skin auto update:"), config.zStyles.skin_auto_update))
        self.list.append(getConfigListEntry(_("Skin update:"), config.zStyles.update))
        if config.zStyles.update.value is True:
            self.list.append(getConfigListEntry("Update/Restore FHD zSkin", config.zStyles.fhdupfind))
            self.list.append(getConfigListEntry("Update/Restore WQHD zSkin", config.zStyles.wqhdupfind))
        self.list.append(getConfigListEntry(_("Read style configuration from skin:"), config.zStyles.load_style_from_skin))
        self.list.append(getConfigListEntry(_("TMDB API:"), config.zStyles.data))
        if config.zStyles.data.getValue():
            self.list.append(getConfigListEntry(_("Read Apikey TMDB from file /tmp/tmdbapikey.txt"), config.zStyles.api))
            self.list.append(getConfigListEntry(_("Set Your Apikey TMDB"), config.zStyles.txtapi))
        self.list.append(getConfigListEntry(_("OMDB API:"), config.zStyles.data2))
        if config.zStyles.data2.getValue():
            self.list.append(getConfigListEntry(_("Read Apikey OMDB from file /tmp/omdbapikey.txt"), config.zStyles.api2))
            self.list.append(getConfigListEntry(_("Set Your Apikey OMDB"), config.zStyles.txtapi2))
        # self.list.append(getConfigListEntry(_("VISUALWEATHER API:"), config.zStyles.data3))
        # if config.zStyles.data3.getValue():
            # self.list.append(getConfigListEntry(_("Read Apikey VisualWeather from /etc/enigma2/VisualWeather/apikey.txt"), config.zStyles.api3))
            # self.list.append(getConfigListEntry(_("Set Your Apikey VisualWeather"), config.zStyles.txtapi3))
        # self.list.append(getConfigListEntry(_("THE TVDB API:"), config.zStyles.data4))
        # if config.zStyles.data4.getValue():
            # self.list.append(getConfigListEntry(_("Read Apikey TheTVDBkey from /tmp/thetvdbkey.txt"), config.zStyles.api4))
            # self.list.append(getConfigListEntry(_("Set Your Apikey TheTVDBkey"), config.zStyles.txtapi4))
        self.list.append(getConfigListEntry(_("Preserve preview if not defined:"), config.zStyles.preserve_preview))
        self["config"].list = self.list
        self["config"].l.setList(self.list)

    def layoutFinished(self):
        from .Version import __version__, __revision__
        self.setTitle(_("Setup") + str.format(" - {0} {1}.{2}", PLUGIN_NAME, __version__, __revision__))

    def keyOk(self):
        global tarfile
        ConfigListScreen.keyOK(self)
        sel = self["config"].getCurrent()[1]
        if sel and sel == config.zStyles.api:
            self.keyApi()
        if sel and sel == config.zStyles.txtapi:
            self.KeyText()
        if sel and sel == config.zStyles.api2:
            self.keyApi2()
        if sel and sel == config.zStyles.txtapi2:
            self.KeyText()
        if sel and sel == config.zStyles.fhdupfind:
            tarfile = 'ZSkin-FHD.tar'
            self.fhdupfind()
        if sel and sel == config.zStyles.wqhdupfind:
            tarfile = 'ZSkin-WQHD.tar'
            self.fhdupfind()

    def fhdupfind(self):
        self.Timer = eTimer()
        try:
            self.Timer.callback.append(self.zUpdate)
        except:
            self.Timer_conn = self.Timer.timeout.connect(self.zUpdate)
        self.Timer.start(500, 1)
        self.createSetup()

    def zUpdate(self):
        CHECKSKIN = "%senigma2/%s" % (mvi, cur_skin)
        if os.path.exists(CHECKSKIN):
            self.session.openWithCallback(self.zUpdate2, MessageBox, _("Skin exist!! Do you really want to Upgrade?"), MessageBox.TYPE_YESNO)
        else:
            self.session.openWithCallback(self.zUpdate2, MessageBox, _('Do you really want to install the Skin??\nDo it at your own risk.\nDo you want to continue?'), MessageBox.TYPE_YESNO)
        return

    def zUpdate2(self, answer=None):
        if answer:
            if config.zStyles.update:
                print('tarfile is: ', tarfile)
                self.zSkin()
        return

    def zSkin(self):
        tmpdirfile = '/tmp/%s' % tarfile
        if fileExists(tmpdirfile):
            os.remove(tmpdirfile)
        try:
            self.com = 'https://patbuweb.com/zskin/%s' % tarfile  # cur_skin
            self.dest = self.dowfil()
            Req = RequestAgent()
            self.command = ["tar -xvf /tmp/%s -C /" % tarfile]
            cmd = "wget -U '%s' -c '%s' -O '%s';%s > /dev/null" % (Req, str(self.com), self.dest, self.command[0])
            if "https" in str(self.com):
                cmd = "wget --no-check-certificate -U '%s' -c '%s' -O '%s';%s > /dev/null" % (Req, str(self.com), self.dest, self.command[0])
            print('self cmd: ', cmd)
            self.session.open(Console, title=_('Installation zSkin'), cmdlist=[cmd, 'sleep 5'])  # , finishedCallback=self.upd_zeta)

        except Exception as e:
            print('error download: ', e)
            return
        print('update tarfile')

    def dowfil(self):
        if PY3:
            import urllib.request as urllib2
            import http.cookiejar as cookielib
        else:
            import urllib2
            import cookielib
        Req = RequestAgent()
        headers = {'User-Agent': Req}
        cookie_jar = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
        urllib2.install_opener(opener)
        try:
            req = urllib2.Request(self.com, data=None, headers=headers)
            handler = urllib2.urlopen(req, timeout=15)
            data = handler.read()
            with open(('/tmp/%s' % tarfile), 'wb') as f:
                f.write(data)
            print('MYDEBUG - download ok - URL: %s , filename: %s' % (self.com, tarfile))
        except:
            print('MYDEBUG - download failed - URL: %s , filename: %s' % (self.com, tarfile))
        return tarfile

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.createSetup()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.createSetup()

    def getCurrentEntry(self):
        return self["config"].getCurrent()[0]

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()

    def getSkinSelector(self):
        try:
            from Plugins.SystemPlugins.SkinSelector.plugin import SkinSelector
            return SkinSelector
        except Exception as e:
            print(str(e))

    def checkSkin(self):
        if not config.zStyles.skin.value:
            self.session.open(MessageBox, _("No previous styled skin - restore canceled!"), MessageBox.TYPE_INFO)
        else:
            self.skin_name = getSkinName()
            if isSkinChanged():
                self.skin_name = config.zStyles.skin.value
            text = _("Would you really reset this skin?") + "\n{0}".format(self.skin_name.split('/')[0])
            dlg = self.session.openWithCallback(self.restoreSkin, MessageBox, text, MessageBox.TYPE_YESNO)
            dlg.setTitle(_("Reset skin?"))

    def restoreSkin(self, answer):
        if not answer:
            return
        dst = resolveFilename(SCOPE_SKIN, self.skin_name)
        src = os.path.join(PLUGIN_PATH, self.skin_name)
        if not fileExists(dst):
            self.session.open(MessageBox, _("The skin not exists - restore canceled!"), MessageBox.TYPE_INFO)
            return
        if not Skin.checkStyled(dst):
            self.session.open(MessageBox, _("The skin is not styled - restore canceled!"), MessageBox.TYPE_INFO)
            return

        if fileExists(src):
            print("[zStyles] restore skin")
            print(src)
            print(dst)
            config.zStyles.preset.clear()
            config.zStyles.style.clear()
            config.zStyles.skin.value = ""
            config.zStyles.skin.save()
            copy2(src, dst)
            dlg = self.session.openWithCallback(self.restartGUI, MessageBox, _("GUI needs a restart to apply a new skin\nDo you want to Restart the GUI now?"), MessageBox.TYPE_YESNO)
            dlg.setTitle(_("Restart GUI now?"))

    def restartGUI(self, answer):
        if answer:
            self.session.open(TryQuitMainloop, 3)

    def keyCancel(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close()

    def keySave(self):
        if config.zStyles.data.getValue():
            if apis is True:
                config.zStyles.txtapi.save()
        config.zStyles.save()
        self.close()

    def keyDummy(self):
        print("[zStyles] key dummy")

    def keyOpenSkinselector(self):
        if self.getSkinSelector() is not None:
            self.session.openWithCallback(self.restoreCurrentSkin, self.getSkinSelector())

    def restoreCurrentSkin(self, **kwargs):
        print("[zStyles] restore current skin")
        config.skin.primary_skin.value = self.current_skin
        config.skin.primary_skin.save()

    def KeyText(self):
        from Screens.VirtualKeyBoard import VirtualKeyBoard
        sel = self["config"].getCurrent()
        if sel:
            self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=self["config"].getCurrent()[0], text=self["config"].getCurrent()[1].value)

    def VirtualKeyBoardCallback(self, callback=None):
        if callback is not None and len(callback):
            self["config"].getCurrent()[1].value = callback
            self["config"].invalidate(self["config"].getCurrent())
        return

    def keyApi(self, answer=None):
        api = "/tmp/tmdbapikey.txt"
        if answer is None:
            if fileExists(api) and os.stat(api).st_size > 0:
                self.session.openWithCallback(self.keyApi, MessageBox, _("Import Api Key TMDB from /tmp/tmdbapikey.txt?"))
            else:
                self.mbox = self.session.open(MessageBox, (_("Missing %s !") % api), MessageBox.TYPE_INFO, timeout=4)
        elif answer:
            if fileExists(api) and os.stat(api).st_size > 0:
                with open(api, 'r') as f:
                    fpage = f.readline()
                    with open(tmdb_skin, "w") as t:
                        t.write(str(fpage))
                        t.close()
                    config.zStyles.txtapi.setValue(str(fpage))
                    config.zStyles.txtapi.save()
                    self.createSetup()
                    self.mbox = self.session.open(MessageBox, (_("TMDB ApiKey Imported & Stored!")), MessageBox.TYPE_INFO, timeout=4)
            else:
                self.mbox = self.session.open(MessageBox, (_("Missing %s !") % api), MessageBox.TYPE_INFO, timeout=4)
        return

    def keyApi2(self, answer=None):
        api2 = "/tmp/omdbapikey.txt"
        if answer is None:
            if fileExists(api2) and os.stat(api2).st_size > 0:
                self.session.openWithCallback(self.keyApi2, MessageBox, _("Import Api Key OMDB from /tmp/omdbapikey.txt?"))
            else:
                self.mbox = self.session.open(MessageBox, (_("Missing %s !") % api2), MessageBox.TYPE_INFO, timeout=4)
        elif answer:
            if fileExists(api2) and os.stat(api2).st_size > 0:
                with open(api2, 'r') as f:
                    fpage = f.readline()
                    with open(omdb_skin, "w") as t:
                        t.write(str(fpage))
                        t.close()
                    config.zStyles.txtapi2.setValue(str(fpage))
                    config.zStyles.txtapi2.save()
                    self.createSetup()
                    self.mbox = self.session.open(MessageBox, (_("OMDB ApiKey Imported & Stored!")), MessageBox.TYPE_INFO, timeout=4)
            else:
                self.mbox = self.session.open(MessageBox, (_("Missing %s !") % api2), MessageBox.TYPE_INFO, timeout=4)
        return
