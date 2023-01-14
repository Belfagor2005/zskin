from __init__ import _, PLUGIN_PATH, PLUGIN_NAME
from Screens.Screen import Screen
from Components.Sources.StaticText import StaticText
from Components.ActionMap import ActionMap
from Components.config import config
from Components.ConfigList import ConfigListScreen
from Tools.Directories import fileExists, resolveFilename, SCOPE_SKIN
from style import Skin
from shutil import copy2
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.config import getConfigListEntry
from style_ops import getSkinName, isSkinChanged
import os

class StylesSetup(Screen, ConfigListScreen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self["setupActions"] = ActionMap(["ColorActions", "OkCancelActions", "MenuActions"],
        {
            "ok": self.keySave,
            "cancel": self.keyCancel,
            "red": self.keyCancel,
            "green": self.keySave,
            "yellow": self.keyOpenSkinselector,
            "blue": self.checkSkin,
        }, -2)
        self["key_red"] = StaticText(_("Close"))
        self["key_green"] = StaticText(_("Save"))
        self["key_yellow"] = StaticText(self.getSkinSelector() is not None and "Skin" or "")
        self["key_blue"] = StaticText(_("Reset skin"))
        self.setup_title = PLUGIN_NAME
        self.list = []
        self.list.append(getConfigListEntry(_("Skin auto update:"), config.Styles.skin_auto_update))
        self.list.append(getConfigListEntry(_("Read style configuration from skin:"), config.Styles.load_style_from_skin))
        self.list.append(getConfigListEntry(_("Preserve preview if not defined:"), config.Styles.preserve_preview))
        ConfigListScreen.__init__(self, self.list, session)
        self.onLayoutFinish.append(self.layoutFinished)
        self.current_skin = config.skin.primary_skin.value

    def layoutFinished(self):
        from Version import __version__, __revision__
        self.setTitle(_("Setup") + str.format(" - {0} {1}.{2}", PLUGIN_NAME, __version__, __revision__))

    def getSkinSelector(self):
        try:
            from Plugins.SystemPlugins.SkinSelector.plugin import SkinSelector
            return SkinSelector 
        except Exception, e:
            print e
    
    def checkSkin(self):
        if not config.Styles.skin.value:
            self.session.open(MessageBox, _("No previous styled skin - restore canceled!"), MessageBox.TYPE_INFO)
        else:
            self.skin_name = getSkinName()
            if isSkinChanged():
                self.skin_name = config.Styles.skin.value
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
            print "[Styles] restore skin"
            print src
            print dst
            config.Styles.preset.clear()
            config.Styles.style.clear()
            config.Styles.skin.value = ""
            config.Styles.skin.save()
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
        config.Styles.save()
        self.close()

    def keyDummy(self):
        print "[Styles] key dummy"

    def keyOpenSkinselector(self):
        if self.getSkinSelector() is not None:
            self.session.openWithCallback(self.restoreCurrentSkin, self.getSkinSelector())
        
    def restoreCurrentSkin(self, **kwargs):
        print "[Styles] restore current skin"
        config.skin.primary_skin.value = self.current_skin
        config.skin.primary_skin.save()
        

