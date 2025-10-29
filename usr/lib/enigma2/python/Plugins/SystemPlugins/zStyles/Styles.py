#!/usr/bin/python
# -*- coding: utf-8 -*-

#  zStyles for Dreambox-Enigma2
#
# Copyright (C) 2018 cmikula
#
# In case of reuse of this source code please do not remove this copyright.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# For more information on the GNU General Public License see:
# <http://www.gnu.org/licenses/>.
#
# For example, if you distribute copies of such a program, whether gratis or for a fee, you
# must pass on to the recipients the same freedoms that you received. You must make sure
# that they, too, receive or can get the source code. And you must show them these terms so they know their rights.
#
from . import _, PLUGIN_NAME, isDreambox
from Screens.Screen import Screen
from Components.Sources.StaticText import StaticText
from Components.ActionMap import ActionMap
from Components.config import config, ConfigNothing, ConfigSelection, ConfigSubDict, ConfigText
from Components.ConfigList import ConfigListScreen
from Tools.Directories import fileExists
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from .StylesSetup import StylesSetup
from .ConfigHelper import storeConfig
from .style_ops import writeStyle, loadStyle, getStyleFile, getSkinFile, isPrimarySkin
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Components.AVSwitch import AVSwitch
from Components.Pixmap import Pixmap
from .PicLoader import PicLoader
from enigma import gPixmapPtr
import os


if isDreambox:
    from Components.config import getConfigListEntry
else:
    def getConfigListEntry(*args):
        if len(args) == 1:
            return "{0} {1} {2}".format(
                "-" * 5, args[0], "-" * 200), ConfigNothing()
        return args


class ConfigSelectionEx(ConfigSelection):
    def __init__(self, choices, default):
        ConfigSelection.__init__(self, choices, default)


class Styles(Screen, ConfigListScreen):
    def __init__(self, session, style_file=None):
        Screen.__init__(self, session)
        self.preview = Preview(self, "preview")
        self["setupActions"] = ActionMap(
            ["ColorActions", "OkCancelActions", "MenuActions"],
            {
                "ok": self.keySave,
                "cancel": self.close,
                "red": self.close,
                "green": self.keySave,
                "yellow": self.keyDefault,
                "blue": self.keyDummy,
                "menu": self.openMenu,
            },
            -2
        )
        self["key_red"] = StaticText(_("Close"))
        self["key_green"] = StaticText(_("Save"))
        self["key_yellow"] = StaticText(_("Default"))
        self["key_blue"] = StaticText()
        self.setup_title = PLUGIN_NAME
        self.list = []
        ConfigListScreen.__init__(self, self.list, session)
        self["config"].onSelectionChanged.append(self.onSelectionChanged)
        self.current_skin_path = os.path.dirname(getSkinFile())
        self.onFirstExecBegin.append(self.loadStyle)
        self.onLayoutFinish.append(self.layoutFinished)
        self.style_file = style_file

    def layoutFinished(self):
        self.setTitle(self.setup_title)

    def openMenu(self):
        self.session.open(StylesSetup)

    def loadStyle(self):
        self.style = loadStyle(self.style_file)
        self.style.checkDependency = self.checkDependency
        self.preset = self.style.getPreset()
        self.createConfigListEntries()
        if not self.style.hasStyle():
            return

        style_errors = self.style.checkPresets()
        if style_errors:
            file_name = getStyleFile().replace(".xml", "_error.xml")
            with open(file_name, "wb") as f:
                f.write(style_errors)
            self.session.open(
                MessageBox,
                _("Style presets contains errors!") +
                "\n" +
                file_name,
                MessageBox.TYPE_ERROR)

    def keySave(self):
        if not self.style.hasStyle():
            self.close()
            return

        config.zStyles.skin.value = config.skin.primary_skin.value
        config.zStyles.preset = ConfigSubDict()
        config.zStyles.style = ConfigSubDict()

        for item in self["config"].getList():
            if len(item) < 2:
                continue
            key = item[0]
            value = item[1].getValue()
            if not value:
                continue
            # print key
            # print value
            if isinstance(item[1], ConfigSelectionEx):
                config.zStyles.preset[key] = ConfigText()
                config.zStyles.preset[key].value = value
                continue
            if isinstance(item[1], ConfigSelection):
                config.zStyles.style[key] = ConfigText()
                config.zStyles.style[key].value = value

        config.zStyles.save()
        writeStyle(self.style, config.zStyles, getSkinFile())
        storeConfig()

        dlg = self.session.openWithCallback(
            self.restartGUI,
            MessageBox,
            _("GUI needs a restart to apply a new skin\nDo you want to Restart the GUI now?"),
            MessageBox.TYPE_YESNO)
        dlg.setTitle(_("Restart GUI now?"))

    def restartGUI(self, answer):
        if answer:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()

    def keyDummy(self):
        print("[zStyles] key dummy")

    def keyDefault(self):
        print("[zStyles] key default")
        default = self.style.getDefault()
        for item in self.list:
            if len(item) < 2:
                continue
            key = item[0]
            val = item[1].getValue()
            if key and val and key in default:  # .has_key(key):
                item[1].setValue(default[key])
                self["config"].invalidate(item)
        self.onSelectionChanged()

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.updateConfigList()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.updateConfigList()

    def onSelectionChanged(self):
        current = self["config"].getCurrent()
        if current is None or len(current) < 2:
            return
        name = current[0]
        value = current[1].getValue()
        self.updatePreview(name, value)

    def updateConfigList(self):
        if len(self.list) < 2:
            return

        current = self["config"].getCurrent()
        if current is None or len(current) < 2:
            return

        name = current[0]
        value = current[1].getValue()
        # update preview
        self.updatePreview(name, value)

        if isinstance(current[1], ConfigSelectionEx):
            # update selection
            preset = self.preset[name][value]
            for name, value in preset.iteritems():
                for item in self.list:
                    # print item[0]
                    if item[0] == name:
                        item[1].setValue(value)
                        self["config"].invalidate(item)

    def getSelected(self, key, conf_dict):
        if key in conf_dict:  # .has_key(key):
            if isinstance(conf_dict[key], str):
                return conf_dict[key]
            else:
                return conf_dict[key].value

    def getConfigSelection(self, T, key, entries, selected):
        if not isinstance(entries, list):
            entries = list(entries)
        if selected not in entries:
            selected = None
        return T(entries, selected)

    def checkDependency(self, depend):
        if not depend:
            return True
        return os.path.exists(
            os.path.join(
                resolveFilename(SCOPE_PLUGINS),
                depend))

    def createConfigListEntries(self):
        self.list = []
        if isPrimarySkin() or not self.style.hasStyle():
            self.list.append(
                getConfigListEntry(
                    _("Current skin can not styled!"),
                    ConfigNothing()))
            self["config"].setList(self.list)
            return
        depends = self.style.getDepends()
        default = self.style.getDefault()
        if len(self.preset) > 0:
            self.list.append(getConfigListEntry(_("PRESET")))
            # for key1 in sorted(self.preset):
            for key1 in self.style.sort(self.preset):
                if not self.checkDependency(depends.get(key1)):
                    continue
                selected = self.getSelected(key1, config.zStyles.preset)
                if not selected:
                    selected = self.getSelected(key1, default)
                self.list.append(
                    getConfigListEntry(
                        key1, self.getConfigSelection(
                            ConfigSelectionEx, key1, sorted(
                                self.preset[key1]), selected)))
                # self.updatePreview(key1, selected)

        groups = self.style.getGroup()
        for key in self.style.sort(groups):
            # print key
            if not self.checkDependency(depends.get(key)):
                continue
            self.list.append(getConfigListEntry(key.upper()))
            # for key1 in sorted(groups[key]):
            for key1 in self.style.sort(groups[key]):
                # print "  " + key1
                if not self.checkDependency(depends.get(key1)):
                    continue
                selected = self.getSelected(key1, config.zStyles.style)
                if not selected:
                    selected = self.getSelected(key1, default)
                self.list.append(
                    getConfigListEntry(
                        key1, self.getConfigSelection(
                            ConfigSelection, key1, sorted(
                                groups[key][key1]), selected)))

        self["config"].setList(self.list)

    def updatePreview(self, name, value):
        default = None
        if not config.zStyles.preserve_preview.value:
            default = ""
        preview = self.style.getPreview(name, value, default)
        print(str.format("Preview '{0}.{1}' = {2}", name, value, str(preview)))
        if not preview:
            print("Try load preview from preset")
            preview = self.style.getPresetPreview(name, value, default)
        if preview is not None:
            file_name = os.path.join(self.current_skin_path, preview)
            self.preview.loadPreview(file_name)


class Preview():
    def __init__(self, parent, name):
        self.picload = PicLoader()
        self.picload.addCallback(self.showPreviewCallback)
        self.name = name
        self.parent = parent
        self.parent[name] = Pixmap()
        self.parent.onLayoutFinish.append(self.layoutFinish)
        self.parent.onClose.append(self.__onClose)
        self.default_pixmap = None

    def __onClose(self):
        self.picload.destroy()
        self.parent = None

    def layoutFinish(self):
        sc = AVSwitch().getFramebufferScale()
        self.picload.setPara((self.parent[self.name].instance.size().width(
        ), self.parent[self.name].instance.size().height(), sc[0], sc[1], False, 1, "#ff000000"))
        for attribute in self.parent[self.name].skinAttributes:
            if attribute[0] == "pixmap":
                self.default_pixmap = attribute[1]

    def showPreviewCallback(self, picInfo=None):
        if picInfo:
            ptr = self.picload.getData()
            if ptr is not None and self.working:
                self.parent[self.name].instance.setPixmap(ptr)
        self.working = False

    def loadPreview(self, file_name):
        if os.path.isfile(file_name) and fileExists(file_name):
            self.working = True
            self.picload.startDecode(file_name)
        elif self.default_pixmap:
            self.working = True
            self.picload.startDecode(self.default_pixmap)
        else:
            empty = gPixmapPtr()
            self.parent[self.name].instance.setPixmap(empty)
