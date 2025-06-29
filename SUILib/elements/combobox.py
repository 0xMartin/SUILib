"""
ComboBox UI element for SUILib

File:       combobox.py
Date:       15.02.2022

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

from SUILib.elements.button import Button
from SUILib.elements.listpanel import ListPanel
import pygame
from ..utils import *
from ..colors import *
from ..guielement import *


class ComboBox(GUIElement, Container):
    """
    Represents a dropdown ComboBox UI element for SUILib applications.

    ComboBox allows users to select a value from a list of options via a dropdown menu.
    It combines a display area showing the current selection and a button that toggles
    the visibility of a popup panel containing all available options. ComboBox supports
    customizable styles, value change callbacks, and integrates with the View layout system.

    Attributes:
        values (list): List of selectable string options.
        selected_item (str): Currently selected value.
        button (Button): The dropdown toggle button.
        listpanel (ListPanel): The popup panel displaying selectable options.
        callback (callable): Function to be called when the selected value changes.
        font (pygame.font.Font): Font used for rendering the selected value.
    """

    def __init__(self, view, style: dict, values: list, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new ComboBox instance.

        Args:
            view: The parent View instance where this ComboBox is placed.
            style (dict): Dictionary containing style attributes for the ComboBox.
                See config/styles.json for details.
            values (list): List of string values to choose from.
            width (int, optional): Width of the ComboBox in pixels. Defaults to 0.
            height (int, optional): Height of the ComboBox in pixels. Defaults to 0.
            x (int, optional): X coordinate of the ComboBox. Defaults to 0.
            y (int, optional): Y coordinate of the ComboBox. Defaults to 0.
        """
        self.button = None
        self.listpanel = None
        super().__init__(view, x, y, width, height, style)
        self.values = values
        self.callback = None
        self.hover = False
        self.selected_item = values[0]
        # Popup panel for options
        self.listpanel = ListPanel(
            view, super().get_style()["listpanel"], values)
        self.listpanel.set_visibility(False)
        self.listpanel.set_item_click_evet(lambda p: self.set_selected_item(p))
        # Dropdown toggle button
        self.button = Button(view, super().get_style()["button"], "↓")
        self.button.add_click_evt(
            lambda x: self.set_popup_panel_visibility(not self.listpanel.is_visible()))
        # Font for rendering selected value
        self.font = pygame.font.SysFont(
            super().get_style()["font_name"],
            super().get_style()["font_size"],
            bold=super().get_style()["font_bold"]
        )
        super().update_view_rect()

    @overrides(GUIElement)
    def update_view_rect(self):
        """
        Update the ComboBox's view rectangle and synchronize the position and size
        of the button and popup panel with the ComboBox dimensions.
        """
        super().update_view_rect()
        if self.button is not None:
            self.button.set_width(super().get_height())
            self.button.set_height(super().get_height())
            self.button.set_x(super().get_x() + super().get_width() - self.button.get_width())
            self.button.set_y(super().get_y())
        if self.listpanel is not None:
            self.listpanel.set_width(super().get_width())
            self.listpanel.set_x(super().get_x())
            self.listpanel.set_y(super().get_y() + super().get_height())

    def set_popup_panel_visibility(self, visibility):
        """
        Set the visibility of the popup panel containing selectable options.

        Args:
            visibility (bool): True to show the panel, False to hide it.
        """
        self.listpanel.set_visibility(visibility)
        if self.listpanel.is_visible():
            self.get_view().setFilter_processOnly(self)
            self.button.set_text("↑")
        else:
            self.button.set_text("↓")
            self.get_view().clear_filter()

    def set_values(self, values: list):
        """
        Set the list of possible values for the ComboBox.

        Args:
            values (list): The new list of selectable options.
        """
        self.values = values

    def get_values(self) -> list:
        """
        Get the list of possible values for the ComboBox.

        Returns:
            list: The current list of selectable options.
        """
        return self.values

    def get_selected_item(self) -> str:
        """
        Get the currently selected item.

        Returns:
            str: The currently selected option.
        """
        return self.selected_item

    def set_selected_item(self, item_name: str):
        """
        Set the currently selected item and hide the popup panel.

        Args:
            item_name (str): The value to select.
        """
        self.selected_item = item_name
        self.set_popup_panel_visibility(False)
        if self.callback is not None:
            self.callback(self.selected_item)

    def set_value_changed_evt(self, callback):
        """
        Set the callback function to be called when the selected value changes.

        Args:
            callback (callable): Function to be invoked on value change.
                The function should accept a single argument: the selected item (str).
        """
        self.callback = callback

    @overrides(GUIElement)
    def draw(self, view, screen):
        """
        Render the ComboBox, including the display area, button, and popup panel if visible.

        Args:
            view: The parent View instance.
            screen (pygame.Surface): The surface to render the ComboBox onto.
        """
        # Draw ComboBox background
        if self.is_selected():
            c = super().get_style()["background_color"]
            pygame.draw.rect(screen, color_change(
                c, -0.2 if c[0] > 128 else 0.6), super().get_view_rect(), border_radius=10)
        else:
            pygame.draw.rect(screen, super().get_style()["background_color"], super().get_view_rect(), border_radius=10)
        # Draw selected value text
        if len(self.values[0]) != 0:
            screen.set_clip(super().get_view_rect())
            text = self.font.render(
                self.selected_item,
                1,
                super().get_style()["foreground_color"]
            )
            screen.blit(
                text,
                (
                    super().get_x() + (super().get_width() - text.get_width())/2,
                    super().get_y() + (super().get_height() - text.get_height())/2
                )
            )
            screen.set_clip(None)
        # Draw ComboBox outline
        pygame.draw.rect(screen, super().get_style()["outline_color"], super().get_view_rect(), 2, border_radius=10)
        # Draw dropdown button
        self.button.draw(view, screen)
        # Draw popup panel if visible (on top)
        if self.listpanel.is_visible():
            self.get_view().get_app().draw_later(1000, self.listpanel.draw)

    @overrides(GUIElement)
    def process_event(self, view, event):
        """
        Handle Pygame events for ComboBox interaction.

        Args:
            view: The parent View instance.
            event (pygame.event.Event): The Pygame event to process.
        """
        self.button.process_event(view, event)
        if self.listpanel.is_visible():
            self.listpanel.process_event(view, event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not in_rect(
                event.pos[0],
                event.pos[1],
                pygame.Rect(
                    super().get_x(),
                    super().get_y(),
                    super().get_width(),
                    super().get_height() + self.listpanel.get_height() + 5
                )
            ):
                self.set_popup_panel_visibility(False)

    @overrides(GUIElement)
    def update(self, view):
        """
        Update logic for the ComboBox.

        This method is a placeholder for future extensions; currently, it does not perform any updates.

        Args:
            view: The parent View instance.
        """
        pass

    @overrides(Container)
    def get_childs(self):
        """
        Return the child elements of the ComboBox.

        Returns:
            list: List containing the dropdown button as a child element.
        """
        return [self.button]