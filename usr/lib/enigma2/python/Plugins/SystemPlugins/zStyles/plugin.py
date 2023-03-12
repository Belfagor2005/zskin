#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Styles for Dreambox-Enigma2
#
#  Coded by cmikula (c)2018
#  Support: www.i-have-a-dreambox.com
#
#  This plugin is licensed under the Creative Commons
#  Attribution-NonCommercial-ShareAlike 3.0 Unported
#  License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-nc-sa/3.0/ or send a letter to Creative
#  Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
#
#  Alternatively, this plugin may be distributed and executed on hardware which
#  is licensed by Dream Property GmbH.
#
#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially
#  distributed other than under the conditions noted above.
#

from . import _, loadPluginSkin, PLUGIN_NAME, getPluginIcon
from Components.config import config, ConfigSubsection
from Components.config import ConfigText, ConfigSubDict, ConfigYesNo
from Plugins.Plugin import PluginDescriptor
from .PicLoader import isDreamOS
from .zConfigHelper import loadConfig

config.zStyles = ConfigSubsection()
config.zStyles.skintest = ConfigText()
config.zStyles.skin = ConfigText()
config.zStyles.preserve_preview = ConfigYesNo()
config.zStyles.skin_auto_update = ConfigYesNo(False)
config.zStyles.data = ConfigYesNo(default=False)
config.zStyles.api = ConfigText(default="PRESS OK")
config.zStyles.txtapi = ConfigText(default="12345678909876543212345678909876", visible_width=50, fixed_size=False)
config.zStyles.data2 = ConfigYesNo(default=False)
config.zStyles.api2 = ConfigText(default="PRESS OK")
config.zStyles.txtapi2 = ConfigText(default="cb1d9f55", visible_width=50, fixed_size=False)
config.zStyles.load_style_from_skin = ConfigYesNo(True)
config.zStyles.style = ConfigSubDict()
config.zStyles.preset = ConfigSubDict()
loadConfig(config.zStyles.style)
loadConfig(config.zStyles.preset)


def autostart(reason, **kwargs):
    if reason == 0:
        print("[zStyles] startup...")
        if config.zStyles.load_style_from_skin.value:
            from .zstyle_ops import loadStyleConfigFromSkin
            loadStyleConfigFromSkin()

    if reason == 1:
        print("[zStyles] shutdown...")
        if config.zStyles.skin_auto_update.value:
            from .style_ops import checkSkin4Update
            checkSkin4Update()


def pluginOpen(session, **kwargs):
    from .zStyles import zStyles
    session.open(zStyles)


def startMenu(menuid):
    ret = [(PLUGIN_NAME, pluginOpen, "zstyles", 15)]
    if isDreamOS and menuid == "osd_video_audio":
        return ret
    if not isDreamOS and menuid == "system":
        return ret
    return []


def Plugins(**kwargs):
    print("[zStyles] creation...")
    loadPluginSkin()
    description = _("Style your skin")
    descriptors = []
    descriptors.append(PluginDescriptor(name=PLUGIN_NAME, description=description, where=PluginDescriptor.WHERE_AUTOSTART, fnc=autostart))
    descriptors.append(PluginDescriptor(name=PLUGIN_NAME, description=description, where=PluginDescriptor.WHERE_MENU, fnc=startMenu))
    descriptors.append(PluginDescriptor(name=PLUGIN_NAME, description=description, where=[PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU], icon=getPluginIcon(), fnc=pluginOpen))
    return descriptors
