"""
ListPanel UI element for SUILib
"""

from SUILib.elements.vertical_scrollbar import VerticalScrollbar
import pygame
from ..utils import *
from ..colors import *
from ..guielement import *
from ..application import *


class ListPanel(GUIElement, Container):
    """
    Represents a scrollable list panel UI element for SUILib applications.

    The ListPanel displays a vertical list of string items, supporting scrolling via an integrated
    vertical scrollbar. It provides click callbacks for item selection, dynamic list refresh,
    and can be used as a dropdown menu, selection panel, or general-purpose list container.

    Attributes:
        data (list): List of string items to display.
        v_scroll (VerticalScrollbar): Scrollbar for vertical navigation.
        body_offset_y (float): Current vertical offset for list rendering.
        font (pygame.font.Font): Font object used for rendering list items.
        callback (callable): Function to be called when an item is clicked.
        layoutmanager: Reserved for future custom layout integration.
    """

    def __init__(self, view, style: dict, data: list, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new ListPanel instance.

        Args:
            view: The parent View instance where this panel is placed.
            style (dict): Dictionary describing the style for this panel.
                See config/styles.json for details.
            data (list): List of string items to display in the panel.
            width (int, optional): Width of the panel in pixels. Defaults to 0.
            height (int, optional): Height of the panel in pixels. Defaults to 0.
            x (int, optional): X coordinate of the panel. Defaults to 0.
            y (int, optional): Y coordinate of the panel. Defaults to 0.
        """
        self.data = data
        self.v_scroll = None
        self.body_offset_y = 0
        super().__init__(view, x, y, width, height, style)
        self.v_scroll = VerticalScrollbar(
            view, super().get_style()["scrollbar"], super().get_style()["scrollbar_width"])
        self.v_scroll.set_on_scroll_evt(self.scroll_vertical)
        self.layoutmanager = None
        self.callback = None
        self.refresh_list()

    @overrides(GUIElement)
    def update_view_rect(self):
        """
        Update the ListPanel's view rectangle and refresh layout and scrollbar.
        """
        super().update_view_rect()
        self.refresh_list()

    def set_item_click_evet(self, callback):
        """
        Set the callback function to be called when a list item is clicked.

        Args:
            callback (callable): Function to be called with the clicked item's value.
        """
        self.callback = callback

    def scroll_vertical(self, position: float):
        """
        Event handler for vertical scrollbar movement.

        Args:
            position (float): Vertical scroll position in the range [0.0, 1.0].
        """
        total_body_data_height = 10 + (self.font.get_height() + 10) * len(self.data)
        h = super().get_height()
        self.body_offset_y = -max(0, (total_body_data_height - h)) * position

    def refresh_list(self, new_data: list = None):
        """
        Refresh or update the contents of the list panel.

        Args:
            new_data (list, optional): New list of string items to display.
                If None, refreshes with current data.
        """
        if new_data is not None:
            self.data = new_data

        self.font = pygame.font.SysFont(
            super().get_style()["font_name"],
            super().get_style()["font_size"],
            bold=super().get_style()["font_bold"]
        )
        self.height = 10 + (self.font.get_height() + 10) * min(5, len(self.data))

        if self.v_scroll is not None:
            sw = super().get_style()["scrollbar_width"]
            self.v_scroll.set_x(super().get_x() + super().get_width() - sw)
            self.v_scroll.set_y(super().get_y())
            self.v_scroll.set_width(sw)
            self.v_scroll.set_height(super().get_height())

            height = 10 + (self.font.get_height() + 10) * len(self.data)
            self.v_scroll.set_scroller_size(
                (1.0 - max(0, height - super().get_height()) / height) * self.v_scroll.get_height()
            )

    @overrides(GUIElement)
    def draw(self, view, screen):
        """
        Render the list panel, including background, visible items, scrollbar, and outline.

        Args:
            view: The parent View instance.
            screen (pygame.Surface): The surface to render the panel onto.
        """
        # Draw background
        pygame.draw.rect(screen, super().get_style()["background_color"], super().get_view_rect(), border_radius=5)

        # Draw list items
        if len(self.data) != 0:
            screen.set_clip(super().get_view_rect())
            offset = super().get_y() + 10 + self.body_offset_y
            for line in self.data:
                text = self.font.render(
                    line, 1, super().get_style()["foreground_color"])
                screen.blit(text, (super().get_x() + 10, offset))
                offset += text.get_height() + 10
            screen.set_clip(None)

        # Draw vertical scrollbar
        self.v_scroll.draw(view, screen)

        # Draw outline
        pygame.draw.rect(screen, super().get_style()["outline_color"], super().get_view_rect(), 2, border_radius=5)

    @overrides(GUIElement)
    def process_event(self, view, event):
        """
        Handle Pygame events for list item selection and scrollbar interaction.

        Args:
            view: The parent View instance.
            event (pygame.event.Event): The event to process.
        """
        self.v_scroll.process_event(view, event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            offset = super().get_y() + 10 + self.body_offset_y
            for line in self.data:
                if in_rect(
                        event.pos[0],
                        event.pos[1],
                        pygame.Rect(
                            super().get_x(),
                            offset,
                            super().get_width() - self.v_scroll.get_width() - 5,
                            self.font.get_height()
                        )):
                    if self.callback is not None:
                        self.callback(line)
                offset += self.font.get_height() + 10

    @overrides(GUIElement)
    def update(self, view):
        """
        Update logic for the list panel.

        This method is a placeholder for future extensions; currently, it does not perform any updates.

        Args:
            view: The parent View instance.
        """
        pass

    @overrides(Container)
    def get_childs(self):
        """
        Return the child elements of the ListPanel.

        Returns:
            list: List containing the vertical scrollbar as a child element.
        """
        return [self.v_scroll]