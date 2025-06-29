"""
Base classes for GUI elements in SUILib

This module defines the core abstract base classes for GUI elements and containers
used in the SUILib framework. It provides the foundational interface and functionality
for all graphical elements (buttons, panels, sliders, etc.) in a multi-view
pygame-based application.

Author: Martin Krcma <martin.krcma1@gmail.com>
Github: https://github.com/0xMartin
Date: 08.02.2022

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

import pygame
from typing import final
import abc
import inspect

class GUIElement(metaclass=abc.ABCMeta):
    """
    Abstract base class for all GUI elements in SUILib.

    Provides position, size, style, visibility, selection state, and required
    abstract interface for rendering, event processing, and updates.

    Attributes:
        view: Reference to parent View.
        x (int): X position.
        y (int): Y position.
        width (int): Width of the element.
        height (int): Height of the element.
        style (dict): Style dictionary.
        selected_cursor: Pygame cursor type shown when this element is selected.
        visible (bool): Visibility of the element.
        selected (bool): Selection state.
        rect (pygame.Rect): Rectangle representing the element's position and size.
    """

    def __init__(
        self,
        view,
        x: int,
        y: int,
        width: int,
        height: int,
        style: dict,
        selected_cursor=pygame.SYSTEM_CURSOR_HAND
    ):
        """
        Initialize a new GUIElement.

        Args:
            view: Parent View where the element is placed.
            x (int): X position.
            y (int): Y position.
            width (int): Width in pixels.
            height (int): Height in pixels.
            style (dict): Style dictionary. If None, will be resolved by class name.
            selected_cursor: Pygame cursor type to show when element is selected.
        """
        self.view = view
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.selected_cursor = selected_cursor
        self.visible = True

        sm = view.get_app().get_style_manager()
        if style is None:
            self.style = sm.get_style_with_name(self.__class__.__name__)
            if not self.style:
                # Fallback to check all base 
                for base in inspect.getmro(self.__class__)[1:]:
                    if base is object:
                        continue
                    style = sm.get_style_with_name(base.__name__)
                    if style:
                        self.style = style
                        break
        else:
            self.style = style

        self.selected = False
        self.update_view_rect()

    def set_visibility(self, visible: bool):
        """
        Set visibility of this element.

        Args:
            visible (bool): True to make element visible, False to hide.
        """
        self.visible = visible

    def is_visible(self) -> bool:
        """
        Check visibility of this element.

        Returns:
            bool: True if visible, False otherwise.
        """
        return self.visible

    def set_select_cursor(self, cursor):
        """
        Set the cursor type to use when this element is selected.

        Args:
            cursor: Pygame cursor type constant.
        """
        self.selected_cursor = cursor

    @final
    def get_select_cursor(self):
        """
        Get the cursor type to use when this element is selected.

        Returns:
            int: Pygame cursor type constant.
        """
        return self.selected_cursor

    @final
    def get_view(self):
        """
        Get reference to the parent View.

        Returns:
            View: The parent view object.
        """
        return self.view

    @final
    def get_x(self) -> int:
        """Get X position of this element."""
        return self.x

    @final
    def get_y(self) -> int:
        """Get Y position of this element."""
        return self.y

    @final
    def get_width(self) -> int:
        """Get width of this element."""
        return self.width

    @final
    def get_height(self) -> int:
        """Get height of this element."""
        return self.height

    @final
    def get_style(self) -> dict:
        """Get style dictionary of this element."""
        return self.style

    def set_x(self, x: int):
        """
        Set the X position of this element.

        Args:
            x (int): New X position.
        """
        self.x = x
        self.update_view_rect()

    def set_y(self, y: int):
        """
        Set the Y position of this element.

        Args:
            y (int): New Y position.
        """
        self.y = y
        self.update_view_rect()

    def set_width(self, width: int):
        """
        Set the width of this element.

        Args:
            width (int): New width in pixels.
        """
        if width >= 0:
            self.width = width
            self.update_view_rect()

    def set_height(self, height: int):
        """
        Set the height of this element.

        Args:
            height (int): New height in pixels.
        """
        if height >= 0:
            self.height = height
            self.update_view_rect()

    def set_style(self, style: dict):
        """
        Set the style dictionary for this element.

        Args:
            style (dict): New style.
        """
        self.style = style

    def update_view_rect(self):
        """
        Update the pygame.Rect representing this element's area.
        """
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    @final
    def get_view_rect(self) -> pygame.Rect:
        """
        Get the pygame.Rect representing the element's area.

        Returns:
            pygame.Rect: The rectangle for drawing and hit-testing.
        """
        return self.rect

    @final
    def select(self):
        """Mark this element as selected."""
        self.selected = True

    @final
    def un_select(self):
        """Mark this element as unselected."""
        self.selected = False

    @final
    def is_selected(self) -> bool:
        """
        Check if this element is currently selected.

        Returns:
            bool: True if selected, False otherwise.
        """
        return self.selected

    @abc.abstractmethod
    def draw(self, view, screen: pygame.Surface):
        """
        Draw the element on the pygame surface.

        Args:
            view: The parent View calling the draw method.
            screen (pygame.Surface): The surface to draw on.
        """
        pass

    @abc.abstractmethod
    def process_event(self, view, event):
        """
        Process a pygame event sent from the parent view.

        Args:
            view: The parent View sending the event.
            event: The pygame event object.
        """
        pass

    @abc.abstractmethod
    def update(self, view):
        """
        Update the element's state.

        Args:
            view: The parent View updating this element.
        """
        pass


class Container(metaclass=abc.ABCMeta):
    """
    Abstract base class for a container of GUI elements.

    Any class inheriting from Container must implement get_childs().

    Methods:
        get_childs(): Returns a list of child GUI elements.
    """

    @abc.abstractmethod
    def get_childs(self) -> list:
        """
        Get child GUI elements of the container.

        Returns:
            list: List of contained child elements.
        """
        pass