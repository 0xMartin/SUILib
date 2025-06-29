"""
HorizontalScrollbar UI element for SUILib
"""

import pygame
from ..utils import *
from ..colors import *
from ..guielement import *


class HorizontalScrollbar(GUIElement):
    """
    Represents a horizontal scrollbar UI element for SUILib applications.

    The HorizontalScrollbar allows users to select or scroll through a range horizontally.
    It supports custom styles, drag interaction, and a callback for scroll events.

    Attributes:
        callback (callable): Function to be called when the scrollbar moves.
        scroller_pos (int): Current X position (in pixels) of the scroller.
        scroller_size (int): Width of the draggable scroller in pixels.
    """

    def __init__(self, view, style: dict, scroller_size: int, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new HorizontalScrollbar instance.

        Args:
            view: The parent View instance where this scrollbar is placed.
            style (dict): Dictionary describing the style for this scrollbar.
                See config/styles.json for details.
            scroller_size (int): Width of the draggable scroller in pixels.
            width (int, optional): Width of the scrollbar in pixels. Defaults to 0.
            height (int, optional): Height of the scrollbar in pixels. Defaults to 0.
            x (int, optional): X coordinate of the scrollbar. Defaults to 0.
            y (int, optional): Y coordinate of the scrollbar. Defaults to 0.
        """
        super().__init__(view, x, y, width, height, style, pygame.SYSTEM_CURSOR_SIZEWE)
        self.callback = None
        self.scroller_pos = 0
        self.scroller_size = scroller_size

    def set_scroller_size(self, size: int):
        """
        Set the width of the scroller.

        Args:
            size (int): New width of the scroller in pixels.
        """
        self.scroller_size = max(size, super().get_height())

    def set_on_scroll_evt(self, callback):
        """
        Set the callback function to be called when the scrollbar position changes.

        Args:
            callback (callable): Function to be invoked on scroll.
                The function should accept the normalized scroll position (float from 0.0 to 1.0).
        """
        self.callback = callback

    @overrides(GUIElement)
    def draw(self, view, screen):
        """
        Render the horizontal scrollbar and its scroller.

        Args:
            view: The parent View instance.
            screen (pygame.Surface): The surface to render the scrollbar onto.
        """
        # Draw background
        pygame.draw.rect(screen, super().get_style()["background_color"], super().get_view_rect())
        # Draw scroller
        pygame.draw.rect(
            screen,
            super().get_style()["foreground_color"],
            pygame.Rect(
                super().get_x() + self.scroller_pos,
                super().get_y(),
                self.scroller_size,
                super().get_height()
            ),
            border_radius=6
        )
        # Draw outline
        pygame.draw.rect(screen, super().get_style()["outline_color"], super().get_view_rect(), 2)

    @overrides(GUIElement)
    def process_event(self, view, event):
        """
        Handle Pygame events for scrollbar interaction (drag, release, hover).

        Args:
            view: The parent View instance.
            event (pygame.event.Event): The event to process.
        """
        if self.scroller_size >= super().get_width():
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            if in_rect(event.pos[0], event.pos[1], super().get_view_rect()):
                super().select()
                self.def_scroller_pos = self.scroller_pos
                self.drag_start = event.pos[0]
        elif event.type == pygame.MOUSEBUTTONUP:
            super().un_select()
        elif event.type == pygame.MOUSEMOTION:
            if super().is_selected():
                self.scroller_pos = self.def_scroller_pos + (event.pos[0] - self.drag_start)
                self.scroller_pos = min(
                    max(0, self.scroller_pos), super().get_width() - self.scroller_size)
                if self.callback is not None:
                    self.callback(self.scroller_pos / (super().get_width() - self.scroller_size))

    @overrides(GUIElement)
    def update(self, view):
        """
        Update logic for the scrollbar.

        This method is a placeholder for future extensions; currently, it does not perform any updates.

        Args:
            view: The parent View instance.
        """
        pass