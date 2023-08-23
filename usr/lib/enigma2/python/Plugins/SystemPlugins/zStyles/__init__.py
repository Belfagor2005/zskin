from Components.Language import language
from Tools.Directories import resolveFilename, fileExists
from Tools.Directories import SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ
import gettext
from enigma import getDesktop
from skin import loadSkin

PLUGIN_NAME = "zStyles"
PLUGIN_PATH = resolveFilename(SCOPE_PLUGINS) + "SystemPlugins/" + PLUGIN_NAME + "/"


def getPluginIcon():
    plugin_icon = "skin/images/zstyles.svg"
    try:
        import os
        from Tools.LoadPixmap import LoadPixmap
        LoadPixmap(os.path.join(PLUGIN_PATH, plugin_icon))
        print("[zStyle] svg support")
    except:
        print("[zStyle] no svg support")
        plugin_icon = "skin/images/zstyles.png"
    return plugin_icon


def loadPluginSkin():
    width = getDesktop(0).size().width()
    filename = PLUGIN_PATH + "skin/{0}.xml".format(width)
    print("[zStyle] load skin", filename)
    if fileExists(filename):
        loadSkin(filename)
    else:
        loadSkin(PLUGIN_PATH + "skin/1280.xml")


def localeInit():
    lang = language.getLanguage()
    environ["LANGUAGE"] = lang[:2]
    gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
    gettext.textdomain("enigma2")
    gettext.bindtextdomain(PLUGIN_NAME, PLUGIN_PATH + "locale/")


def _(txt):
    t = gettext.dgettext(PLUGIN_NAME, txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


localeInit()
language.addCallback(localeInit)
