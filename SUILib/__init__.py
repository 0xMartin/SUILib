"""
Simple library for multiple views game aplication with pygame

File:       __init__.py
Date:       08.02.2022

Github:     https://github.com/0xMartin
Email:      martin.krcma1@gmail.com
 
Copyright (C) 2022 Martin Krcma
 
Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:
 
The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

"""
https://github.com/0xMartin/SimpleApp-Pygame-framework
"""

from .application import Application, View, Layout
from .guielement import GUIElement, Container
from .stylemanager import StyleManager
from .layout import RelativeLayout, AbsoluteLayout
from .colors import colorChange, colorAdd, colorInvert, createColor
from .utils import overrides, inRect, generateSignal, loadImage, drawGraph, loadConfig, getDisplayWidth, getDisplayHeight, runTaskAsync
from .graphics import Vertex, Edge, Wireframe

__all__ = [
    "Application",
    "Layout",
    "View",

    "GUIElement",
    "Container",

    "colorChange",
    "colorAdd",
    "colorInvert",
    "createColor",

    "overrides",
    "inRect",
    "generateSignal",
    "loadImage",
    "drawGraph",
    "loadConfig",
    "getDisplayWidth",
    "getDisplayHeight",
    "runTaskAsync",

    "StyleManager",

    "RelativeLayout",
    "AbsoluteLayout",

    "Vertex",
    "Edge",
    "Wireframe"
]