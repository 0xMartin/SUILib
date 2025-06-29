"""
ToggleButton UI element for SUILib

File:       togglebutton.py
Date:       12.02.2022

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

import pygame
from ..utils import *
from ..colors import *
from ..guielement import *
from SUILib.elements.label import Label


class ToggleButton(GUIElement):
    """
    Represents a toggle (switch) button UI element for SUILib applications.

    The ToggleButton acts as an ON/OFF switch with an optional label. It supports
    custom styles, click callbacks, and integrates with the View layout system.

    Attributes:
        label (Label): The label displayed next to the toggle button.
        status (bool): The ON/OFF state of the toggle.
        callback (callable): Function to call when the value (status) changes.
    """

    def __init__(self, view, style: dict, text: str, status: bool = False, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new ToggleButton instance.

        Args:
            view: The parent View instance where this toggle button is placed.
            style (dict): Dictionary containing style attributes for the toggle.
                See config/styles.json for details.
            text (str): The text of the label next to the toggle.
            status (bool, optional): Initial ON/OFF state. Defaults to False (OFF).
            width (int, optional): Width of the toggle in pixels. Defaults to 0.
            height (int, optional): Height of the toggle in pixels. Defaults to 0.
            x (int, optional): X coordinate of the toggle. Defaults to 0.
            y (int, optional): Y coordinate of the toggle. Defaults to 0.
        """
        super().__init__(view, x, y, width, height, style)
        self.label = Label(view, super().get_style()["label"], text, False, True)
        self.callback = None
        self.hover = False
        self.status = status

    def set_text(self, text: str):
        """
        Set the text of the toggle's label.

        Args:
            text (str): New text for the label.
        """
        if self.label is not None:
            self.label.set_text(text)

    def get_status(self) -> bool:
        """
        Get the ON/OFF status of the toggle button.

        Returns:
            bool: True if ON, False if OFF.
        """
        return self.status

    def get_label(self) -> Label:
        """
        Get the Label object associated with this toggle.

        Returns:
            Label: The label instance.
        """
        return self.label

    def set_value_changed_evt(self, callback):
        """
        Set the callback function to be called when the toggle value changes.

        Args:
            callback (callable): Function to be invoked with new status (True/False).
        """
        self.callback = callback

    @overrides(GUIElement)
    def draw(self, view, screen):
        """
        Render the toggle button (switch) and its label.

        Args:
            view: The parent View instance.
            screen (pygame.Surface): The surface to render the toggle onto.
        """
        # Background and outline
        if self.status:
            bg_color = color_change(super().get_style()["foreground_color"], 0.8)
        else:
            bg_color = super().get_style()["background_color"]
        pygame.draw.rect(
            screen,
            bg_color,
            super().get_view_rect(),
            border_radius=int(super().get_height() / 2)
        )
        pygame.draw.rect(
            screen,
            super().get_style()["outline_color"],
            super().get_view_rect(),
            2,
            border_radius=int(super().get_height() / 2)
        )
        # Toggle switch handle
        if self.status:
            pos = super().get_width() - super().get_height() / 2
            pygame.draw.circle(
                screen,
                super().get_style()["foreground_color"],
                (super().get_x() + pos, super().get_y() + super().get_height() / 2),
                super().get_height() / 2
            )
        else:
            pygame.draw.circle(
                screen,
                super().get_style()["foreground_color"],
                (super().get_x() + super().get_height() / 2, super().get_y() + super().get_height() / 2),
                super().get_height() / 2
            )
        # Label
        if self.label is not None:
            self.label.set_x(super().get_x() + super().get_width() + 5)
            self.label.set_y(super().get_y() + super().get_height() / 2)
            self.label.draw(view, screen)

    @overrides(GUIElement)
    def process_event(self, view, event):
        """
        Handle Pygame events for toggle button interaction (click, hover).

        Args:
            view: The parent View instance.
            event (pygame.event.Event): The event to process.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if in_rect(event.pos[0], event.pos[1], super().get_view_rect()):
                self.status = not self.status
                if self.callback is not None:
                    self.callback(self.status)
        elif event.type == pygame.MOUSEMOTION:
            if in_rect(event.pos[0], event.pos[1], super().get_view_rect()):
                self.select()
            else:
                self.un_select()

    @overrides(GUIElement)
    def update(self, view):
        """
        Update logic for the toggle button.

        Args:
            view: The parent View instance.
        """
        pass