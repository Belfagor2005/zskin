from Components.config import config, ConfigText, ConfigSubDict
# from __init__ import PLUGIN_PATH

from . import _, PLUGIN_PATH
from Tools.Directories import fileExists, resolveFilename, SCOPE_SKIN, SCOPE_CONFIG
from .style import Skin, Style, StyleUser
from shutil import copy2
import os

STYLES_FILENAME = "styles.xml"
STYLES_USER_FILENAME = "styles_user.xml"

def checkSkin4Update():
    mtime1 = getStyleUserFileMTime()
    mtime2 = getStyleUserFileMTimeFromSkin()
    if not isSkinChanged() and (not isSkinStyled() or mtime1 != mtime2):
        print("[Styles] perform update...")
        style = loadStyle()
        writeStyle(style, config.Styles, getSkinFile())

def loadStyleConfigFromSkin():
    if isSkinChanged() and isSkinStyled():
        print("[Styles] skin changed, load style configuration...")
        config.Styles.skin.value = config.skin.primary_skin.value
        conf = getSkinConfig(getSkinFile())
        for key1 in sorted(conf):
            for key2 in sorted(conf[key1]):
                print((key1, key2, conf[key1][key2]))
        config.Styles.style = ConfigSubDict()
        for key, value in conf["preset"].iteritems():
            config.Styles.preset[key] = ConfigText()
            config.Styles.preset[key].value = value
        for key, value in conf["style"].iteritems():
            config.Styles.style[key] = ConfigText()
            config.Styles.style[key].value = value
        config.Styles.save()

def isSkinStyled():
    return Skin.checkStyled(getSkinFile())

def isSkinChanged():
    return config.Styles.skin.value != config.skin.primary_skin.value

def isPrimarySkin():
    return getSkinName() == config.skin.primary_skin.default

def getSkinName():
    return config.Styles.skintest.value and config.Styles.skintest.value or config.skin.primary_skin.value 

def getSkinFile():
    return resolveFilename(SCOPE_SKIN, getSkinName())

def getStyleFile():
    return getSkinFile().replace("skin.xml", STYLES_FILENAME)

def getStyleUserFile():
    return resolveFilename(SCOPE_CONFIG, STYLES_USER_FILENAME)

def getStyleUserFileMTime():
    filename = getStyleUserFile()
    result = ""
    if os.path.exists(filename):
        stat = os.stat(filename)
        result = str(stat.st_mtime)
    return result

def getStyleUserFileMTimeFromSkin():
    return Skin.readUserMTime(getSkinFile())

def getSkinConfig(file_name):
    if not Skin.checkStyled(file_name):
        return dict()
    skin = Skin()
    skin.read(file_name)
    return skin.getConfig()

def backupSkin(force=False):
    skin_name = getSkinName()
    src = resolveFilename(SCOPE_SKIN, skin_name)
    dst = os.path.join(PLUGIN_PATH, skin_name)
    #print "[Styles] backup skin"
    #print src
    #print dst
    dst_path = os.path.dirname(dst)
    if not os.path.exists(dst_path):
        os.makedirs(dst_path)
    
    # force skin backup if it is not styled - new skin file
    if not force:
        force = not Skin.checkStyled(src)
        if force:
            print("[Styles] force backup (skin not styled)")
    
    if not fileExists(dst) or force:
        print("[Styles] write backup")
        copy2(src, dst)

    return dst

def loadStyle(file_name=None):
    to_load = file_name or getStyleFile()
    style = Style()
    style.read(to_load)
    user = StyleUser()
    if user.read(getStyleUserFile()) and user.isUsable4Skin(getSkinName()):
        user.loadToStyle(style, getSkinName())
    #if style.hasStyle():
    #    style.printInfo()
    return style

def writeStyle(style, config_Styles, file_name):
    if not style.hasStyle():
        return
    print("#" * 80)

    nodes, style_info = style.getSkinComponents(config_Styles)
    for x in style_info:
        print(x)

    print("-" * 80)

    backup = backupSkin()

    skin = Skin()
    skin.read(backup)
    skin.user_mtime = getStyleUserFileMTime()
    
    comparing = False
    if comparing:
        skin.write(file_name.replace(".xml", "_src.xml"))

    skin.style_info = style_info
    skin.applyNodes(nodes)
    skin.write(file_name)

    if comparing:
        skin.write(file_name.replace(".xml", "_dst.xml"))
    print("#" * 80)


