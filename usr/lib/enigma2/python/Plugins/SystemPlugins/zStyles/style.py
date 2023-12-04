#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from xml.etree import ElementTree
from datetime import datetime
from .Version import __version__, __revision__  # @UnresolvedImport


class TreeBase():
    def __init__(self, file_name=None):
        self.read(file_name)

    def read(self, file_name):
        self.tree = None
        self.root = None
        self.file_name = file_name
        if file_name is None:
            return
        if not os.path.exists(file_name):
            print(str.format("file not exists: {0}", file_name))
            self.file_name = None
            return False
        print(str.format("read: {0}", file_name))
        self.tree = ElementTree.parse(file_name)
        self.root = self.tree.getroot()
        return True

    def indent(self, elem, level=0, more_sibs=False):
        t = "        "
        i = "\n"
        if level:
            i += (level - 1) * t
        num_kids = len(elem)
        if num_kids:
            if not elem.text or not elem.text.strip():
                elem.text = i + t
                if level:
                    elem.text += t
            count = 0
            for kid in elem:
                self.indent(kid, level + 1, count < num_kids - 1)
                count += 1
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
                if more_sibs:
                    elem.tail += t
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
                if more_sibs:
                    elem.tail += t

    def write(self, file_name):
        print(str.format("write: {0}", file_name))
        self.indent(self.root)
        self.tree.write(file_name, encoding="utf-8")


class Skin(TreeBase):
    def __init__(self, file_name=None):
        self.read(file_name)

    @staticmethod
    def checkStyled(file_name):
        line_count = 0
        with open(file_name, "r") as f:
            for line in f:
                if "<style " in line:
                    return True
                line_count += 1
                if line_count > 10:
                    break
        return False

    @staticmethod
    def readUserMTime(file_name):
        line_count = 0
        with open(file_name, "r") as f:
            for line in f:
                items = line.split("user_mtime")
                if len(items) > 1:
                    values = items[1].split('"')
                    if len(values) > 1:
                        return values[1]
                    return ""
                line_count += 1
                if line_count > 10:
                    break
        return ""

    def isStyled(self):
        return self.style_node is not None

    def read(self, file_name):
        self.replaces = []
        self.style_info = []
        self.style_node = None
        self.style_name = ""
        self.user_mtime = ""
        result = TreeBase.read(self, file_name)
        if result:
            test = self.root.findall("style")
            if len(test) == 1:
                self.style_node = test[0]
                self.style_name = self.style_node.attrib.get("name", "")
        return result

    def write(self, file_name):
        if self.root is not None:
            self.applyAttributes(self.replaces)
            self.updateStyleInfo()
            TreeBase.write(self, file_name + "~")
            print(str.format("rename: {0}", file_name))
            os.rename(file_name + "~", file_name)

    def updateStyleInfo(self):
        if self.style_node is None:
            self.style_node = ElementTree.Element("style")
            self.root.insert(0, ElementTree.Comment("Auto generated from zStyles {0}.{1} (c)cmikula".format(__version__, __revision__)))
            self.root.insert(1, ElementTree.Comment("Do NOT deliver this informations with any skin update!"))
            self.root.insert(2, self.style_node)

        self.style_node.clear()
        self.style_node.attrib["name"] = self.style_name and self.style_name or ""
        self.style_node.attrib["revision"] = __revision__
        self.style_node.attrib["time_stamp"] = str(datetime.now())
        self.style_node.attrib["user_mtime"] = str(self.user_mtime)
        for tag, key, value in self.style_info:
            elem = ElementTree.Element(tag)
            elem.attrib["name"] = key
            elem.attrib["value"] = value
            self.style_node.append(elem)

    def applyNodes(self, nodes):
        for node in nodes:
            self.applyNode(node)

    def __replaceNode(self, root, node, _tag, _name, _id):
        for index, child in enumerate(root):
            if child.tag == _tag:
                if child.attrib.get("name", "") == _name and child.attrib.get("id", "") == _id:
                    print(str.format("replace tag='{0}' name='{1}' id='{2}' @ index='{3}'", _tag, _name, _id, index))
                    root[index] = node
                    return True

    def applyNode(self, nodes):
        if nodes is None:
            return
        for node in nodes:
            _tag = node.tag
            _name = node.attrib.get("name", "")
            _id = node.attrib.get("id", "")
            if _tag == "attributes":
                self.replaces.extend(node)
                continue

            if _tag == "layout":
                for child in self.root.findall("layouts"):
                    self.__replaceNode(child, node, _tag, _name, _id)
                continue

            found = self.__replaceNode(self.root, node, _tag, _name, _id)

            if not found and _tag == "screen":
                print(str.format("add tag='{0}' name='{1}' id='{2}'", _tag, _name, _id))
                self.root.append(node)
                found = True
            if not found:
                print(str.format("not found tag='{0}' name='{1}' id='{2}'", _tag, _name, _id))

    def applyAttributes(self, nodes):
        if len(nodes) == 0:
            return
        to_replace = []
        for node in nodes:
            name = node.attrib.get("name", "")
            value = node.attrib.get("value", "")
            expect = node.attrib.get("expect", None)
            to_replace.append((name, value, expect, node.tag))
        print("replace", str(to_replace))
        self.__replaceAttributes(self.root, to_replace)

    def __replaceAttributes(self, node, replace):
        for key in node.attrib.iterkeys():
            for name, value, expect, node_tag in replace:
                if expect is not None and expect != node.attrib[key]:
                    continue
                if node_tag == "set" and key == name:
                    node.attrib[key] = value
                    continue
                if node.attrib[key].startswith(name):
                    node.attrib[key] = node.attrib[key].replace(name, value)
                    continue

        for x in node:
            self.__replaceAttributes(x, replace)

    def getConfig(self):
        d = dict()
        d["preset"] = dict()
        d["style"] = dict()
        if self.style_node is None:
            return d
        for node in self.style_node:
            name = node.attrib.get("name", "")
            value = node.attrib.get("value", "")
            if name and value:
                d[node.tag][name] = value
        return d


class Style(TreeBase):
    def __init__(self, file_name=None):
        TreeBase.__init__(self, file_name)
        self.checkDependency = None

    def hasStyle(self):
        return self.root is not None

    def printInfo(self):
        groups = self.getGroup()
        for key1 in sorted(groups):
            print(key1)
            for key2 in sorted(groups[key1]):
                print("  " + key2)
                for key3 in sorted(groups[key1][key2]):
                    print("    " + key3)

    def getStyleNodes(self):
        if not self.hasStyle():
            return []
        l = []
        for node in self.root:
            if node.tag in ("presets", "sorted", "depends"):
                continue
            for style in node.findall("style"):
                item = StyleItem(style, node)
                # print item.getParentName()
                # print item.getName()
                # print item.getValue()
                l.append(item)
        return l

    def getStyleNode(self, key, value):
        styles = self.getStyleNodes()
        for style in styles:
            n = style.getName()
            v = style.getValue()
            if n == key and v == value:
                return style

    def getSkinNode(self, key, value):
        style = self.getStyleNode(key, value)
        if style:
            return style.getSkinNode()
        else:
            print(str.format("not skin name='{0}' value='{1}'", key, value))

    def getGroup(self):
        d = dict()
        styles = self.getStyleNodes()
        for style in styles:
            if self.checkDependency is not None and not self.checkDependency(style.getDepend()):
                continue
            p = style.getParentName()
            n = style.getName()
            v = style.getValue()
            if p not in d:  # .has_key(p):
                d[p] = dict()
            if n not in d[p]:  # .has_key(n):
                d[p][n] = dict()
            d[p][n][v] = style.getSkinNode()
        return d

    def getDefault(self):
        if not self.hasStyle():
            return dict()
        d = dict()
        for node in self.root.findall("presets"):
            for default in node.findall("default"):
                for node in default:
                    name = node.attrib.get("name", "")
                    value = node.attrib.get("value", "")
                    if name and value:
                        d[name] = value
        return d

    def getPreset(self):
        if not self.hasStyle():
            return dict()
        d = dict()
        for node in self.root.findall("presets"):
            for styles in node.findall("style"):
                p = styles.attrib.get("name", "")
                n = styles.attrib.get("value", "")
                if p not in d:  # .has_key(p):
                    d[p] = dict()
                if n not in d[p]:  # .has_key(n):
                    d[p][n] = dict()
                for s in styles:
                    v = s.attrib.get("name", "")
                    value = s.attrib.get("value", "")
                    d[p][n][v] = value
        return d

    def getPresetPreview(self, name, value, default=None):
        if not self.hasStyle() or not name:
            return default
        for node in self.root.findall("presets"):
            for styles in node.findall("style"):
                for s in styles:
                    n = s.attrib.get("name", "")
                    v = s.attrib.get("value", "")
                    if n == name and v == value:
                        if ("preview") in styles.attrib:  # .has_key("preview"):
                            return styles.attrib.get("preview", "")
                        return default
        return default

    def getPreview(self, name, value, default=None):
        if not self.hasStyle() or not name:
            return default
        for node in self.root:
            for styles in node.findall("style"):
                n = styles.attrib.get("name", "")
                v = styles.attrib.get("value", "")
                if n == name and v == value:
                    if ("preview") in styles.attrib:  # .has_key("preview"):
                        return styles.attrib.get("preview", "")
                    return default
        return default

    def getDepends(self):
        d = dict()
        if not self.hasStyle():
            return d
        for node in self.root:
            for styles in node.findall("depend"):
                n = styles.attrib.get("name", "")
                v = styles.attrib.get("value", "")
                if n and v:
                    d[n] = v
        return d

    def getSorted(self):
        d = dict()
        if not self.hasStyle():
            return d
        for nodes in self.root.findall("sorted"):
            for node in nodes:
                i = node.attrib.get("id", "")
                n = node.attrib.get("name", "")
                if n and i:
                    d[n] = int(i)
        return d

    def sort(self, styles):
        s = self.getSorted()
        k = styles.keys()
        lx = sorted(k, key=lambda x: s.get(x, x))
        return lx

    def checkPresets(self):
        errors = []
        count = 0
        preset = self.getPreset()
        node = ElementTree.Element("presets")
        for key1 in preset:
        # for key1 in sorted(preset):
            # print key1
            # for key2 in sorted(preset[key1]):
            for key2 in preset[key1]:
                root = ElementTree.Element("style")
                root.attrib["name"] = key1
                root.attrib["value"] = key2
                element = None
                for key3 in preset[key1][key2]:
                # for key3 in sorted(preset[key1][key2]):
                    # print "  " + str(key2) + " = " + preset[key1][key2][key3]
                    test = self.getSkinNode(key3, preset[key1][key2][key3])
                    if test is None:
                        count += 1
                        text = str.format('name="{0}" value="{1}"', key3, preset[key1][key2][key3])
                        if text not in errors:
                            errors.append(text)
                        print(text)
                        element = ElementTree.Element("style")
                        element.attrib["name"] = key3
                        element.attrib["value"] = preset[key1][key2][key3]
                        root.append(element)
                if element is not None:
                    node.append(root)

        if count > 0:
            info = ElementTree.Element("info")
            node.insert(0, info)
            info.attrib["description"] = "{0} error(s) in presets found!".format(count)
            info.attrib["time_stamp"] = str(datetime.now())
            for text in errors:
                info.append(ElementTree.Comment(text))
            print("[Styles] check preset {0} errors found".format(count))
            self.indent(node)
            return ElementTree.tostring(node)
        return ""

    def getSkinComponents(self, config_Styles):
        defaults = self.getDefault()
        style_info = []
        nodes = []
        for key in config_Styles.preset:
        # for key in sorted(config_Styles.preset):
            value = config_Styles.preset[key].getValue()
            style_info.append(("preset", key, value))
        for key in config_Styles.style:
        # for key in sorted(config_Styles.style):
            value = config_Styles.style[key].getValue()
            node = self.getSkinNode(key, value)
            if node is None and key in defaults:  # .has_key(key):
                print("no zstyle key='{0}' value='{1}'".format(key, value))
                value = defaults[key]
                node = self.getSkinNode(key, value)
                if node is None:
                    print("not found key='{0}' value='{1}'".format(key, value))
                    continue
                print("use default key='{0}' value='{1}'".format(key, value))
            nodes.append(node)
            style_info.append(("style", key, value))
        return (nodes, style_info)


class StyleItem():
    def __init__(self, node, parent):
        self.node = node
        self.parent = parent

    def getParentName(self):
        if self.parent is not None:
            name = self.parent.attrib.get('name', '')
            if not name:
                return self.parent.tag
            return name
        return len(self.node) > 0 and self.node[0].tag or ""

    def getName(self):
        g = self.node.attrib.get('name', '')
        if not g:
            return self.parent.tag
        return g

    def getValue(self):
        return self.node.attrib.get('value', '')

    def getPreview(self):
        return self.node.attrib.get('preview', '')

    def getDepend(self):
        return self.node.attrib.get('depend', '')

    def getSkinNode(self):
        return self.node


class StyleUser():
    def __init__(self):
        self.user_root = None

    def read(self, file_name):
        if file_name is None:
            return
        if not os.path.exists(file_name):
            print(str.format("file not exists: {0}", file_name))
            return False
        print(str.format("read: {0}", file_name))
        tree = ElementTree.parse(file_name)
        self.user_root = tree.getroot()
        return True

    def loadToStyle(self, style, skin_name):
        if style.root is None:
            style.root = ElementTree.fromstring("<styles></styles>")
        unused = self.__getUnusable(skin_name)
        for node in self.user_root:
            n = node.get("name")
            if node.tag == "usable" or n in unused:
                print("cancel", str(node.tag), str(n))
                continue
            print("add", str(node.tag))
            self.__addNode(style, node)

    def __addNode(self, style, node):
        for elem in style.root:
            if elem.tag == node.tag:
                for item in node:
                    elem.append(item)
                return
        style.root.append(node)

    def __getUnusable(self, skin_name):
        l1 = []
        l2 = []
        for nodes in self.user_root.findall("usable"):
            for node in nodes:
                n = node.get("name")
                if n:
                    v = node.get("value")
                    if v in skin_name:
                        l1.append(n)
                    else:
                        l2.append(n)
        s1 = set(l1)
        s2 = set(l2)
        return s2 - s1

    def isUsable4Skin(self, skin_name):
        print("check usability", str(skin_name))
        if self.user_root is None:
            return False
        for nodes in self.user_root.findall("usable"):
            for node in nodes:
                n = node.get("name")
                v = node.get("value")
                if not n and v in skin_name:
                    return True
        return False
