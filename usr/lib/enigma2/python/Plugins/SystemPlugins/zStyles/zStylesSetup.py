from . import _, PLUGIN_PATH, PLUGIN_NAME
from Screens.Screen import Screen
from Components.Sources.StaticText import StaticText
from Components.ActionMap import ActionMap
from Components.config import config
from Components.ConfigList import ConfigListScreen
from Tools.Directories import fileExists, resolveFilename
from Tools.Directories import SCOPE_SKIN
from .zstyle import zSkin
from shutil import copy2
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.config import getConfigListEntry
from .zstyle_ops import getSkinName, isSkinChanged
import os

from enigma import eTimer
tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
omdb_api = "cb1d9f55"

cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
try:
    from enigma import eMediaDatabase  # @UnresolvedImport @UnusedImport
    isDreamOS = True
except:
    isDreamOS = False

global apis, apis2, my_cur_skin, zaddon
apis = False
apis2 = False
my_cur_skin = False

try:
    if my_cur_skin is False:
        myz_skin = "/usr/share/enigma2/%s/apikey" % cur_skin
        print('skinz namez', myz_skin)
        omdb_skin = "/usr/share/enigma2/%s/omdbkey" % cur_skin
        print('skinz namez', omdb_skin)
        if os.path.exists(myz_skin):
            with open(myz_skin, "r") as f:
                tmdb_api = f.read()
        if os.path.exists(omdb_skin):
            with open(omdb_skin, "r") as f:
                omdb_api = f.read()
except:
    my_cur_skin = False

zaddon = False
zaddons = '/usr/lib/enigma2/python/Plugins/SystemPlugins/zStyles/addons'
if os.path.exists(zaddons):
    zaddon = True
print('zaddon ', zaddon)


class zStylesSetup(Screen, ConfigListScreen):
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
        self.list.append(getConfigListEntry(_("Skin auto update:"), config.zStyles.skin_auto_update))
        self.list.append(getConfigListEntry(_("Read style configuration from skin:"), config.zStyles.load_style_from_skin))
        self.list.append(getConfigListEntry(_("TMDB API:"), config.zStyles.data))
        if config.zStyles.data.getValue():
            self.list.append(getConfigListEntry(_("Read Api key TMDB from file /tmp/tmdbapikey.txt"), config.zStyles.api))
            self.list.append(getConfigListEntry(_("Set Your Api key TMDB"), config.zStyles.txtapi))
        self.list.append(getConfigListEntry(_("OMDB API:"), config.zStyles.data2))
        if config.zStyles.data2.getValue():
            self.list.append(getConfigListEntry(_("Read Api key OMDB from file /tmp/omdbapikey.txt"), config.zStyles.api2))
            self.list.append(getConfigListEntry(_("Set Your Api key OMDB"), config.zStyles.txtapi2))
        self.list.append(getConfigListEntry(_("Preserve preview if not defined:"), config.zStyles.preserve_preview))
        self["config"].list = self.list
        self["config"].setList(self.list)

    def layoutFinished(self):
        from .Version import __version__, __revision__
        self.setTitle(_("Setup") + str.format(" - {0} {1}.{2}", PLUGIN_NAME, __version__, __revision__))

    def keyOk(self):
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
        if not zSkin.checkStyled(dst):
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

    def keyApi(self):
        api = "/tmp/tmdbapikey.txt"
        if fileExists(api) and os.stat(api).st_size > 0:
            self.session.openWithCallback(self.importApi, MessageBox, _("Import Api Key TMDB from /tmp/tmdbapikey.txt?"), type=MessageBox.TYPE_YESNO, timeout=10, default=False)
        else:
            self.mbox = self.session.open(MessageBox, (_("Missing %s !") % api), MessageBox.TYPE_INFO, timeout=4)

    def keyApi2(self):
        api2 = "/tmp/omdbapikey.txt"
        if fileExists(api2) and os.stat(api2).st_size > 0:
            self.session.openWithCallback(self.importApi2, MessageBox, _("Import Api Key OMDB from /tmp/omdbapikey.txt?"), type=MessageBox.TYPE_YESNO, timeout=10, default=False)
        else:
            self.mbox = self.session.open(MessageBox, (_("Missing %s !") % api2), MessageBox.TYPE_INFO, timeout=4)

    def importApi(self, result):
        if result:
            api = "/tmp/apikey.txt"
            if fileExists(api) and os.stat(api).st_size > 0:
                global apis
                apis = False
                with open(api, 'r') as f:
                    fpage = f.readline()
                    with open(myz_skin, "w") as t:
                        t.write(str(fpage))
                        t.close()
                    apis = True
                    self.mbox = self.session.open(MessageBox, (_("TMDB ApiKey Imported!")), MessageBox.TYPE_INFO, timeout=4)
                    config.zStyles.txtapi.setValue(str(fpage))
                    config.zStyles.txtapi.save()
                    self.createSetup()
                    self.mbox = self.session.open(MessageBox, (_("TMDB ApiKey Stored!")), MessageBox.TYPE_INFO, timeout=4)
            else:
                self.mbox = self.session.open(MessageBox, (_("Missing %s !") % api), MessageBox.TYPE_INFO, timeout=4)
        else:
            return

    def importApi2(self, result):
        if result:
            api2 = "/tmp/omdbkey.txt"
            if fileExists(api2) and os.stat(api2).st_size > 0:
                global api2s
                api2s = False
                with open(api2, 'r') as f:
                    fpage = f.readline()
                    with open(omdb_skin, "w") as t:
                        t.write(str(fpage))
                        t.close()
                    api2s = True
                    self.mbox = self.session.open(MessageBox, (_("OMDB ApiKey Imported!")), MessageBox.TYPE_INFO, timeout=4)
                    config.zStyles.txtapi2.setValue(str(fpage))
                    config.zStyles.txtapi2.save()
                    self.createSetup()
                    self.mbox = self.session.open(MessageBox, (_("OMDB ApiKey Stored!")), MessageBox.TYPE_INFO, timeout=4)
            else:
                self.mbox = self.session.open(MessageBox, (_("Missing %s !") % api2), MessageBox.TYPE_INFO, timeout=4)
        else:
            return
