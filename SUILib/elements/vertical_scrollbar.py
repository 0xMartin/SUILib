"""
VerticalScrollbar UI element for SUILib
"""

import pygame
from ..utils import *
from ..colors import *
from ..guielement import *


class VerticalScrollbar(GUIElement):
    """
    Represents a vertical scrollbar UI element for SUILib applications.

    The VerticalScrollbar allows users to scroll through a content area by dragging
    the scroller handle. It supports custom styles, event callbacks, and integrates
    with the View layout system.

    Attributes:
        scroller_pos (float): Current vertical position of the scroller handle.
        scroller_size (int): Height of the scroller handle in pixels.
        callback (callable): Function to call when the scroller is moved.
    """

    def __init__(self, view, style: dict, scroller_size: int, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new VerticalScrollbar.

        Args:
            view: The parent View instance where this scrollbar is placed.
            style (dict): Dictionary containing style attributes for the scrollbar.
                See config/styles.json for details.
            scroller_size (int): Height of the scroller handle in pixels.
            width (int, optional): Width of the scrollbar in pixels. Defaults to 0.
            height (int, optional): Height of the scrollbar in pixels. Defaults to 0.
            x (int, optional): X coordinate of the scrollbar. Defaults to 0.
            y (int, optional): Y coordinate of the scrollbar. Defaults to 0.
        """
        super().__init__(view, x, y, width, height, style, pygame.SYSTEM_CURSOR_SIZENS)
        self.callback = None
        self.scroller_pos = 0
        self.scroller_size = scroller_size

    def set_scroller_size(self, size: int):
        """
        Set the size of the scroller handle.

        Args:
            size (int): New height of the scroller handle in pixels.
        """
        self.scroller_size = max(size, super().get_width())

    def set_on_scroll_evt(self, callback):
        """
        Set a callback to be called when the scrollbar is scrolled.

        Args:
            callback (callable): Function to be called with the new position (0.0 - 1.0).
        """
        self.callback = callback

    @overrides(GUIElement)
    def draw(self, view, screen):
        """
        Render the scrollbar background, handle, and outline.

        Args:
            view: The parent View instance.
            screen (pygame.Surface): The surface to render the scrollbar onto.
        """
        # Background
        pygame.draw.rect(screen, super().get_style()["background_color"], super().get_view_rect())
        # Scroller handle
        pygame.draw.rect(
            screen,
            super().get_style()["foreground_color"],
            pygame.Rect(
                super().get_x(),
                super().get_y() + self.scroller_pos,
                super().get_width(),
                self.scroller_size
            ),
            border_radius=6
        )
        # Outline
        pygame.draw.rect(screen, super().get_style()["outline_color"], super().get_view_rect(), 2)

    @overrides(GUIElement)
    def process_event(self, view, event):
        """
        Handle Pygame events for scrollbar interaction (dragging the handle).

        Args:
            view: The parent View instance.
            event (pygame.event.Event): The event to process.
        """
        if self.scroller_size >= super().get_height():
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            if in_rect(event.pos[0], event.pos[1], super().get_view_rect()):
                super().select()
                self.def_scroller_pos = self.scroller_pos
                self.drag_start = event.pos[1]
        elif event.type == pygame.MOUSEBUTTONUP:
            super().un_select()
        elif event.type == pygame.MOUSEMOTION:
            if super().is_selected():
                self.scroller_pos = self.def_scroller_pos + (event.pos[1] - self.drag_start)
                self.scroller_pos = min(
                    max(0, self.scroller_pos), super().get_height() - self.scroller_size)
                if self.callback is not None:
                    self.callback(self.scroller_pos / (super().get_height() - self.scroller_size))

    @overrides(GUIElement)
    def update(self, view):
        """
        Update logic for the vertical scrollbar.

        Args:
            view: The parent View instance.
        """
        pass
