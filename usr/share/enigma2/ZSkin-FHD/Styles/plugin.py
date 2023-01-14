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
from __init__ import _, loadPluginSkin, PLUGIN_NAME, getPluginIcon
from Components.config import config, ConfigSubsection, ConfigText, ConfigSubDict, ConfigYesNo
from Plugins.Plugin import PluginDescriptor
from PicLoader import isDreamOS
from ConfigHelper import loadConfig


config.Styles = ConfigSubsection()
config.Styles.skintest = ConfigText()
config.Styles.skin = ConfigText()
config.Styles.preserve_preview = ConfigYesNo()
config.Styles.skin_auto_update = ConfigYesNo(True)
config.Styles.load_style_from_skin = ConfigYesNo(True)

config.Styles.style = ConfigSubDict()
config.Styles.preset = ConfigSubDict()
loadConfig(config.Styles.style)
loadConfig(config.Styles.preset)


def autostart(reason, **kwargs):
    if reason == 0:
        print "[Styles] startup..."
        if config.Styles.load_style_from_skin.value:
            from style_ops import loadStyleConfigFromSkin
            loadStyleConfigFromSkin()
     
    if reason == 1:
        print "[Styles] shutdown..."
        if config.Styles.skin_auto_update.value:
            from style_ops import checkSkin4Update
            checkSkin4Update()

def pluginOpen(session, **kwargs):
    from Styles import Styles
    session.open(Styles)

def startMenu(menuid):
    ret = [(PLUGIN_NAME, pluginOpen, "styles", 15)]
    if isDreamOS and menuid == "osd_video_audio":
        return ret
    if not isDreamOS and menuid == "system":
        return ret
    return [ ]

def Plugins(**kwargs):
    print "[Styles] creation..."
    loadPluginSkin()
    description = _("Style your skin")
    descriptors = []
    descriptors.append(PluginDescriptor(name=PLUGIN_NAME, description=description, where=PluginDescriptor.WHERE_AUTOSTART, fnc=autostart))
    descriptors.append(PluginDescriptor(name=PLUGIN_NAME, description=description, where=PluginDescriptor.WHERE_MENU, fnc=startMenu))
    descriptors.append(PluginDescriptor(name=PLUGIN_NAME, description=description, where=[PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU], icon=getPluginIcon(), fnc=pluginOpen))
    return descriptors

