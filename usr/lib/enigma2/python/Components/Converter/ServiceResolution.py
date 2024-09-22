# -*- coding: utf-8 -*-
#
# ServiceResolution  - Converter
#
# Coded by dhwz (c) 2018-2020
# E-Mail: dhwz@gmx.net
#
# This plugin is open source but it is NOT free software.
#
# This plugin may only be distributed to and executed on hardware which
# is licensed by Dream Property GmbH.
# In other words:
# It's NOT allowed to distribute any parts of this plugin or its source code in ANY way
# to hardware which is NOT licensed by Dream Property GmbH.
# It's NOT allowed to execute this plugin and its source code or even parts of it in ANY way
# on hardware which is NOT licensed by Dream Property GmbH.
#
# If you want to use or modify the code or parts of it,
# you have to keep MY license and inform me about the modifications by mail.
#

try:
    f = open("/proc/stb/info/model", "r")
    model = ''.join(f.readlines()).strip()
except:
    model = ''

from Components.Converter.Converter import Converter
from enigma import iServiceInformation, iPlayableService
from Components.Element import cached
from os import path

if model in ["one", "two"]:
    from enigma import CT_MPEG2, CT_H264, CT_MPEG1, CT_MPEG4_PART2, CT_VC1, CT_VC1_SIMPLE_MAIN, CT_H265, CT_DIVX311, CT_DIVX4, CT_SPARK, CT_VP6, CT_VP8, CT_VP9, CT_H263, CT_MJPEG, CT_REAL, CT_AVS, CT_UNKNOWN


class ServiceResolution(Converter, object):
    VIDEO_INFO = 0
    VIDEO_INFOCODEC = 1
    VIDEO_CODEC = 2

    def __init__(self, type):
        Converter.__init__(self, type)
        if model in ["one", "two"]:
            self.type, self.interesting_events = {"VideoInfo": (self.VIDEO_INFO, (iPlayableService.evVideoSizeChanged, iPlayableService.evVideoProgressiveChanged, iPlayableService.evVideoFramerateChanged, iPlayableService.evUpdatedInfo,)),
                                                  "VideoInfoCodec": (self.VIDEO_INFOCODEC, (iPlayableService.evVideoSizeChanged, iPlayableService.evVideoProgressiveChanged, iPlayableService.evVideoFramerateChanged, iPlayableService.evUpdatedInfo, iPlayableService.evVideoTypeReady,)),
                                                  "VideoCodec": (self.VIDEO_CODEC, (iPlayableService.evVideoSizeChanged, iPlayableService.evVideoProgressiveChanged, iPlayableService.evVideoFramerateChanged, iPlayableService.evUpdatedInfo, iPlayableService.evVideoTypeReady,)),
                                                  }[type]
        else:
            self.type, self.interesting_events = {"VideoInfo": (self.VIDEO_INFO, (iPlayableService.evVideoSizeChanged, iPlayableService.evVideoProgressiveChanged, iPlayableService.evVideoFramerateChanged, iPlayableService.evUpdatedInfo,)),
                                                  "VideoInfoCodec": (self.VIDEO_INFOCODEC, (iPlayableService.evVideoSizeChanged, iPlayableService.evVideoProgressiveChanged, iPlayableService.evVideoFramerateChanged, iPlayableService.evUpdatedInfo,)),
                                                  "VideoCodec": (self.VIDEO_CODEC, (iPlayableService.evVideoSizeChanged, iPlayableService.evVideoProgressiveChanged, iPlayableService.evVideoFramerateChanged, iPlayableService.evUpdatedInfo,)),
                                                  }[type]
        self.need_wa = iPlayableService.evVideoSizeChanged in self.interesting_events

    def reuse(self):
        self.need_wa = iPlayableService.evVideoSizeChanged in self.interesting_events

    @cached
    def getBoolean(self):
        service = self.source.service
        info = service and service.info()
        if not info:
            return False

        if self.type == self.VIDEO_INFO:
            frame_rate = info.getInfo(iServiceInformation.sFrameRate)
            if model in ["one", "two"]:
                xres = info.getInfo(iServiceInformation.sVideoWidth)
                yres = info.getInfo(iServiceInformation.sVideoHeight)
                if frame_rate > 0 and xres > 0 and yres > 0:
                    return True
                else:
                    return False
            else:
                if frame_rate > 0:
                    return True
                else:
                    return False

        return False

    boolean = property(getBoolean)

    @cached
    def getText(self):
        service = self.source.service
        info = service and service.info()
        if not info:
            return ""

        if self.type in [self.VIDEO_INFO, self.VIDEO_INFOCODEC]:
            xres = None
            if path.exists("/proc/stb/vmpeg/0/xres"):
                f = open("/proc/stb/vmpeg/0/xres", "r")
                try:
                    xres = int(f.read(), 16)
                except:
                    pass
                f.close()
            if not xres:
                xres = info.getInfo(iServiceInformation.sVideoWidth)

            yres = None
            if path.exists("/proc/stb/vmpeg/0/yres"):
                f = open("/proc/stb/vmpeg/0/yres", "r")
                try:
                    yres = int(f.read(), 16)
                except:
                    pass
                f.close()
            if not yres:
                yres = info.getInfo(iServiceInformation.sVideoHeight)

            progressive = info.getInfo(iServiceInformation.sProgressive)
            frame_rate = info.getInfo(iServiceInformation.sFrameRate)
            if not progressive:
                frame_rate *= 2
            frame_rate = (frame_rate + 500) / 1000
            if frame_rate > 0 and xres > 0 and yres > 0:
                xres = str(xres)
                yres = str(yres)
                x = "x"
                frame_rate = str(frame_rate)
                p = 'p' if progressive else 'i'
            else:
                xres = ""
                yres = ""
                x = ""
                frame_rate = ""
                p = ""
            if self.type == self.VIDEO_INFO:
                return "%s%s%s%s%s" % (xres, x, yres, p, frame_rate)
        if self.type in [self.VIDEO_INFOCODEC, self.VIDEO_CODEC]:
            codec = None
            if model in ["one", "two"]:
                codec = info.getInfo(iServiceInformation.sVideoType)
                codec = {CT_MPEG2: "MPEG2", CT_H264: "H.264/AVC", CT_MPEG1: "MPEG1", CT_MPEG4_PART2: "MPEG4",
                         CT_VC1: "VC1", CT_VC1_SIMPLE_MAIN: "WMV3", CT_H265: "H.265/HEVC", CT_DIVX311: "DIVX3",
                         CT_DIVX4: "DIVX4", CT_SPARK:  "SPARK", CT_VP6: "VP6", CT_VP8:  "VP8",
                         CT_VP9: "VP9", CT_H263: "H.263", CT_MJPEG: "MJPEG", CT_REAL: "RV",
                         CT_AVS: "AVS", CT_UNKNOWN: "UNKNOWN"}[codec]
            else:
                if path.exists("/proc/stb/vmpeg/0/codec"):
                    f = open("/proc/stb/vmpeg/0/codec", "r")
                    try:
                        codec = f.read().strip()
                        codec = codec.replace('H.264 (MPEG4 AVC)', 'H.264/AVC').replace('H.265 (HEVC)', 'H.265/HEVC')
                    except:
                        pass
                    f.close()
            if self.type == self.VIDEO_INFOCODEC:
                if xres in ["", "0"]:
                    return ""
                elif codec:
                    return "%s%s%s%s%s [%s]" % (xres, x, yres, p, frame_rate, codec)
                else:
                    return "%s%s%s%s%s" % (xres, x, yres, p, frame_rate)
            if self.type == self.VIDEO_CODEC:
                if codec:
                    return codec
                else:
                    return ""
        return ""

    text = property(getText)

    @cached
    def getValue(self):
        service = self.source.service
        info = service and service.info()
        if not info:
            return -1

        if self.type == self.VIDEO_INFO:
            return -1 if info.getInfo(iServiceInformation.sVideoHeight) < 0 or info.getInfo(iServiceInformation.sFrameRate) < 0 or info.getInfo(iServiceInformation.sProgressive) < 0 else -2
        return -1

    value = property(getValue)

    def changed(self, what):
        if what[0] != self.CHANGED_SPECIFIC or what[1] in self.interesting_events:
            Converter.changed(self, what)
        elif self.need_wa:
            if self.getValue() != -1:
                Converter.changed(self, (self.CHANGED_SPECIFIC, iPlayableService.evVideoSizeChanged))
                self.need_wa = False
