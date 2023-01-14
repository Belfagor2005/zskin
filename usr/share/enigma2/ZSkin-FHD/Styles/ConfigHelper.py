#!/usr/bin/python
# -*- coding: utf-8 -*-
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

from Components.config import config, ConfigSubDict, ConfigText

KEYS = ((".", "\s01"), ("=", "\s02"))

def __encodeConfig(value):
    for x in KEYS:
        value = value.replace(x[0], x[1])
    return value

def __decodeConfig(value):
    for x in KEYS:
        value = value.replace(x[1], x[0])
    return value

def encodeConfig(conf, c):
    try:
        for key, item in c.iteritems():
            key = __encodeConfig(key)
            conf[key] = ConfigText()
            conf[key].value = __encodeConfig(item.value)
    except Exception, e:
        print e

def storeConfig():
    p = config.Styles.preset
    s = config.Styles.style
    config.Styles.preset = ConfigSubDict()
    config.Styles.style = ConfigSubDict()
    encodeConfig(config.Styles.preset, p)
    encodeConfig(config.Styles.style, s)
    config.Styles.save()

def loadConfig(conf):
    try:
        for key, value in conf.stored_values.iteritems():
            key = __decodeConfig(key)
            conf[key] = ConfigText()
            conf[key].value = __decodeConfig(value)
    except Exception, e:
        print e
