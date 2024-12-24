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
from Components.config import config, ConfigSubsection, ConfigSelection
from Components.config import NoSave, ConfigText, ConfigSubDict, ConfigYesNo, ConfigOnOff
from Plugins.Plugin import PluginDescriptor
from Tools.Directories import fileExists
from . import _, loadPluginSkin, PLUGIN_NAME, getPluginIcon, isDreambox
from .ConfigHelper import loadConfig
global my_cur_skin
my_cur_skin = False
mvi = '/usr/share/'
cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
tmdb_skin = "%senigma2/%s/apikey" % (mvi, cur_skin)
tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
omdb_skin = "%senigma2/%s/omdbkey" % (mvi, cur_skin)
omdb_api = "cb1d9f55"
visual_skin = "/etc/enigma2/VisualWeather/apikey.txt"
visual_api = "5KAUFAYCDLUYVQPNXPN3K24V5"
thetvdb_skin = "%senigma2/%s/thetvdbkey" % (mvi, cur_skin)
thetvdbkey = 'D19315B88B2DE21F'

try:
    if my_cur_skin is False:
        if fileExists(tmdb_skin):
            with open(tmdb_skin, "r") as f:
                tmdb_api = f.read()
        if fileExists(omdb_skin):
            with open(omdb_skin, "r") as f:
                omdb_api = f.read()
        if fileExists(visual_skin):
            with open(visual_skin, "r") as f:
                visual_api = f.read()
        if fileExists(thetvdb_skin):
            with open(thetvdb_skin, "r") as f:
                thetvdbkey = f.read()
        my_cur_skin = True
except:
    my_cur_skin = False
    pass

config.zStyles = ConfigSubsection()
config.zStyles.skintest = ConfigText()
config.zStyles.skin = ConfigText()
config.zStyles.preserve_preview = ConfigYesNo()
config.zStyles.skin_auto_update = ConfigYesNo(False)
config.zStyles.update = ConfigOnOff(default=False)
config.zStyles.fhdupfind = NoSave(ConfigSelection(['PRESS OK']))
config.zStyles.wqhdupfind = NoSave(ConfigSelection(['PRESS OK']))
config.zStyles.conponent = NoSave(ConfigSelection(['PRESS OK']))
config.zStyles.data = NoSave(ConfigYesNo(default=False))
config.zStyles.api = NoSave(ConfigSelection(["PRESS OK"]))
config.zStyles.txtapi = ConfigText(default=tmdb_api, visible_width=50, fixed_size=False)
config.zStyles.data2 = NoSave(ConfigYesNo(default=False))
config.zStyles.api2 = NoSave(ConfigSelection(["PRESS OK"]))
config.zStyles.txtapi2 = ConfigText(default=omdb_api, visible_width=50, fixed_size=False)
config.zStyles.data3 = NoSave(ConfigYesNo(default=False))
config.zStyles.api3 = NoSave(ConfigSelection(["PRESS OK"]))
config.zStyles.txtapi3 = ConfigText(default=visual_api, visible_width=50, fixed_size=False)
config.zStyles.data4 = NoSave(ConfigYesNo(default=False))
config.zStyles.api4 = NoSave(ConfigSelection(["PRESS OK"]))
config.zStyles.txtapi4 = ConfigText(default=thetvdbkey, visible_width=50, fixed_size=False)
config.zStyles.png = NoSave(ConfigYesNo(default=False))  # NoSave(ConfigSelection(['-> Ok']))
config.zStyles.load_style_from_skin = ConfigYesNo(True)
config.zStyles.style = ConfigSubDict()
config.zStyles.preset = ConfigSubDict()
loadConfig(config.zStyles.style)
loadConfig(config.zStyles.preset)


def autostart(reason, **kwargs):
    if reason == 0:
        print("[zStyles] startup...")
        if config.zStyles.load_style_from_skin.value:
            from .style_ops import loadStyleConfigFromSkin
            loadStyleConfigFromSkin()

    if reason == 1:
        print("[zStyles] shutdown...")
        if config.zStyles.skin_auto_update.value:
            from .style_ops import checkSkin4Update
            checkSkin4Update()


def pluginOpen(session, **kwargs):
    from .Styles import Styles
    session.open(Styles)


def startMenu(menuid):
    ret = [(PLUGIN_NAME, pluginOpen, "zStyles", 15)]
    if isDreambox and menuid == "osd_video_audio":
        return ret
    if not isDreambox and menuid == "system":
        return ret
    return []


def Plugins(**kwargs):
    print("[zStyles] creation...")
    loadPluginSkin()
    description = _("Style your zSkin")
    descriptors = []
    descriptors.append(PluginDescriptor(name=PLUGIN_NAME, description=description, where=PluginDescriptor.WHERE_AUTOSTART, fnc=autostart))
    descriptors.append(PluginDescriptor(name=PLUGIN_NAME, description=description, where=PluginDescriptor.WHERE_MENU, fnc=startMenu))
    # descriptors.append(PluginDescriptor(name=PLUGIN_NAME, description=description, where=[PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU], icon=plugin_icon, fnc=pluginOpen))
    descriptors.append(PluginDescriptor(name=PLUGIN_NAME, description=description, where=[PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU], icon=getPluginIcon(), fnc=pluginOpen))
    return descriptors
