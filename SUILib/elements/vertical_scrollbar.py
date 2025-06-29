"""
VerticalScrollbar UI element for SUILib
"""

import pygame
from SUILib.guielement import GUIElement
from SUILib.utils import overrides
from SUILib.events import SUIEvents


class VerticalScrollbar(GUIElement):
    """
    Represents a vertical scrollbar UI element for SUILib applications.

    The VerticalScrollbar allows users to scroll through a content area by dragging
    the scroller handle. It supports custom styles, event callbacks, and integrates
    with the View layout system.

    Attributes:
        scroller_pos (float): Current vertical position of the scroller handle.
        scroller_size (int): Height of the scroller handle in pixels.
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
        self.scroller_pos = 0
        self.scroller_size = scroller_size
        self._start_scroller_pos = 0
        self._drag_start = 0

    def set_scroller_size(self, size: int):
        """
        Set the size of the scroller handle.

        Args:
            size (int): New height of the scroller handle in pixels.
        """
        self.scroller_size = max(size, super().get_width())

    @overrides(GUIElement)
    def draw(self, view, screen):
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
        super().process_event(view, event)
        if self.scroller_size >= super().get_height():
            return
        if not super().is_focused():
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            self._start_scroller_pos = self.scroller_pos
            self._drag_start = event.pos[1]
        elif event.type == pygame.MOUSEBUTTONUP:
            super().un_focus()
            super().trigger_event(SUIEvents.EVENT_ON_BLUR)
        elif event.type == pygame.MOUSEMOTION:
            # calculate relative scroller position
            self.scroller_pos = self._start_scroller_pos + (event.pos[1] - self._drag_start)
            self.scroller_pos = min(max(0, self.scroller_pos), super().get_height() - self.scroller_size)
            relative_pos = self.scroller_pos / (super().get_height() - self.scroller_size)
            super().trigger_event(SUIEvents.EVENT_ON_CHANGE, relative_pos)

