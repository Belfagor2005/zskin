#######################################################################
#
#
#    Volume Text Renderer for Dreambox/Enigma-2
#    Coded by Vali (c)2010 powered by cmikula
#    Support: www.dreambox-tools.info
#
#
#  This plugin is licensed under the Creative Commons
#  Attribution-NonCommercial-ShareAlike 3.0 Unported License.
#  To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/
#  or send a letter to Creative Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
#
#  Alternatively, this plugin may be distributed and executed on hardware which
#  is licensed by Dream Multimedia GmbH.
#
#
#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially
#  distributed other than under the conditions noted above.
#
#
#######################################################################

from Components.VariableText import VariableText
from enigma import eLabel, eDVBVolumecontrol, eTimer, ePoint
from Components.Renderer.Renderer import Renderer


class zextvolumeText(Renderer, VariableText):
    def __init__(self):
        Renderer.__init__(self)
        VariableText.__init__(self)
        self.posX = 0
        self.posY = 0
        self.scaleX = 0
        self.scaleY = 0
        self.__timer = eTimer()
        self.__timer_conn = None
        try:
            self.__timer_conn = self.__timer.timeout.connect(self.pollme)
        except:
            self.__timer.callback.append(self.pollme)

    GUI_WIDGET = eLabel

    def destroy(self):  # Override method in Renderer.Element
        self.__timer.stop()
        self.__timer_conn = None
        Renderer.destroy(self)

    def changed(self, what):
        if not self.suspended:
            self.text = str(eDVBVolumecontrol.getInstance().getVolume())
            volume = eDVBVolumecontrol.getInstance().getVolume()
            pos = ePoint(self.posX, self.posY)
            if self.scaleX:
                pos.setX(self.posX + int(volume * self.scaleX))
            if self.scaleY:
                pos.setY(self.posY - int(volume * self.scaleY))
            self.instance.move(pos)

    def pollme(self):
        self.changed(None)

    def onShow(self):
        self.suspended = False
        self.__timer.start(20)

    def onHide(self):
        self.suspended = True
        self.__timer.stop()

    def applySkin(self, desktop, parent):
        def parseXY(value):
            x, y = value.split(',')
            return int(x), int(y)

        if self.skinAttributes is not None:
            attribs = []
            for (attrib, value) in self.skinAttributes:
                if attrib == "slider":
                    x, y = parseXY(value)
                    if x:
                        self.scaleX = x / 100.0
                    if y:
                        self.scaleY = y / 100.0
                else:
                    attribs.append((attrib, value))

            self.skinAttributes = attribs

        Renderer.applySkin(self, desktop, parent)
        self.posX, self.posY = self.getPosition()
