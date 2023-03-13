#!/usr/bin/python
# -*- coding: utf-8 -*-

#    Copyright (C) 2011 cmikula
#
#    In case of reuse of this source code please do not remove this copyright.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    For more information on the GNU General Public License see:
#    <http://www.gnu.org/licenses/>.
#
#    For example, if you distribute copies of such a program, whether gratis or for a fee, you
#    must pass on to the recipients the same freedoms that you received. You must make sure
#    that they, too, receive or can get the source code. And you must show them these terms so they know their rights.

from Components.AVSwitch import AVSwitch
from enigma import ePicLoad

try:
    from enigma import eMediaDatabase  # @UnresolvedImport @UnusedImport
    isDreamOS = True
except:
    isDreamOS = False


class PicLoader:
    def __init__(self):
        self.picload = ePicLoad()
        self.picload_conn = None

    def setSize(self, width, height, sc=None):
        if sc is None:
            sc = AVSwitch().getFramebufferScale()
        self.picload.setPara((width, height, sc[0], sc[1], False, 1, "#ff000000"))

    def load(self, filename):
        if isDreamOS:
            self.picload.startDecode(filename, False)
        else:
            self.picload.startDecode(filename, 0, 0, False)
        data = self.picload.getData()
        return data

    def destroy(self):
        self.picload = None
        self.picload_conn = None

    def addCallback(self, callback):
        if isDreamOS:
            self.picload_conn = self.picload.PictureData.connect(callback)
        else:
            self.picload.PictureData.get().append(callback)

    def getData(self):
        return self.picload.getData()

    def setPara(self, *args):
        self.picload.setPara(*args)

    def startDecode(self, f):
        self.picload.startDecode(f)
