"""
ComboBox UI element for SUILib
"""

import pygame
from SUILib.guielement import GUIElement, Container
from SUILib.events import SUIEvents
from SUILib.utils import overrides, parser_udim
from SUILib.elements.button import Button
from SUILib.elements.listpanel import ListPanel


class ComboBox(GUIElement, Container):
    """
    Represents a dropdown ComboBox UI element for SUILib applications.

    ComboBox allows users to select a value from a list of options via a dropdown menu.
    It combines a display area showing the current selection and a button that toggles
    the visibility of a popup panel containing all available options. ComboBox supports
    customizable styles, value change callbacks, and integrates with the View layout system.
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
        self._button = None
        self._listpanel = None
        super().__init__(view, x, y, width, height, style)
        self._values = values
        self._selected_item = values[0]
        # Popup panel for options
        self._listpanel = ListPanel(
            view, super().get_style()["listpanel"], values)
        self._listpanel.set_visibility(False)
        self._listpanel.add_event_callback(
            SUIEvents.EVENT_ON_CHANGE,
            lambda p: self.set_selected_item(p)
        )
        # Dropdown toggle button
        self._button = Button(view, super().get_style()["button"], "↓")
        self._button.add_event_callback(
            SUIEvents.EVENT_ON_CLICK,
            lambda x: self.set_popup_panel_visibility(not self._listpanel.is_visible())
        )
        # Font for rendering selected value
        self._font = pygame.font.SysFont(
            super().get_style()["font_name"],
            super().get_style()["font_size"],
            bold=super().get_style()["font_bold"]
        )
        super().update_view_rect()

    @overrides(GUIElement)
    def update_view_rect(self):
        super().update_view_rect()
        if self._button is not None:
            self._button.width =  super().get_height()
            self._button.height = super().get_height()
            self._button.x = super().get_x() + super().get_width() - self._button.width
            self._button.y = super().get_y()
            self._button.update_view_rect()
        if self._listpanel is not None:
            self._listpanel.width = super().get_width()
            self._listpanel.x = super().get_x()
            self._listpanel.y = super().get_y() + super().get_height()
            self._listpanel.update_view_rect()

    def set_popup_panel_visibility(self, visibility):
        """
        Set the visibility of the popup panel containing selectable options.

        Args:
            visibility (bool): True to show the panel, False to hide it.
        """
        self._listpanel.set_visibility(visibility)
        if self._listpanel.is_visible():
            # self.get_view().set_filter_process_only(self)
            self._button.set_text("↓")
        else:
            self._button.set_text("↑")
            # self.get_view().clear_filter()

    def set_values(self, values: list):
        """
        Set the list of possible values for the ComboBox.

        Args:
            values (list): The new list of selectable options.
        """
        self._values = values

    def get_values(self) -> list:
        """
        Get the list of possible values for the ComboBox.

        Returns:
            list: The current list of selectable options.
        """
        return self._values

    def get_selected_item(self) -> str:
        """
        Get the currently selected item.

        Returns:
            str: The currently selected option.
        """
        return self._selected_item

    def set_selected_item(self, item_name: str):
        """
        Set the currently selected item and hide the popup panel.

        Args:
            item_name (str): The value to select.
        """
        self._selected_item = item_name
        self.set_popup_panel_visibility(False)
        super().trigger_event(SUIEvents.EVENT_ON_CHANGE, item_name)

    @overrides(GUIElement)
    def draw(self, view, screen):
        corner_radius = parser_udim(super().get_style()["corner_radius"], super().get_view_rect())

        # Draw ComboBox background
        pygame.draw.rect(
            screen, 
            super().get_style()["background_color"], 
            super().get_view_rect(), 
            border_bottom_left_radius=corner_radius,
            border_top_left_radius=corner_radius
        )

        # Draw selected value text
        if len(self._values[0]) != 0:
            screen.set_clip(super().get_view_rect())
            text = self._font.render(
                str(self._selected_item),
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
        pygame.draw.rect(
            screen, 
            super().get_style()["outline_color"], 
            super().get_view_rect(), 
            2, 
            border_bottom_left_radius=corner_radius,
            border_top_left_radius=corner_radius
        )
        # Draw dropdown button
        self._button.draw(view, screen)
        # Draw popup panel if visible (on top)
        if self._listpanel.is_visible():
            self._listpanel.draw(view, screen)

    @overrides(GUIElement)
    def process_event(self, view, event):
        super().process_event(view, event)
        
        if self._listpanel.is_visible():
            # Process event in listpanel
            self._listpanel.process_event(view, event)
        
        if not super().is_focused() and event.type == pygame.MOUSEBUTTONDOWN:
            self.set_popup_panel_visibility(False)

        self._button.process_event(view, event)

    @overrides(Container)
    def get_childs(self):
        return [self._button, self._listpanel]