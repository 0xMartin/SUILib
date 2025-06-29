"""
HorizontalScrollbar UI element for SUILib
"""

import pygame
from SUILib.guielement import GUIElement
from SUILib.utils import overrides
from SUILib.events import SUIEvents

class HorizontalScrollbar(GUIElement):
    """
    Represents a horizontal scrollbar UI element for SUILib applications.

    The HorizontalScrollbar allows users to select or scroll through a range horizontally.
    It supports custom styles, drag interaction, and a callback for scroll events.
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
        self._scroller_pos = 0
        self._scroller_size = scroller_size
        self._start_scroller_pos = 0
        self._drag_start = 0

    def set_scroller_size(self, size: int):
        """
        Set the width of the scroller.

        Args:
            size (int): New width of the scroller in pixels.
        """
        self._scroller_size = max(size, super().get_height())

    @overrides(GUIElement)
    def draw(self, view, screen):
        # Draw background
        pygame.draw.rect(screen, super().get_style()["background_color"], super().get_view_rect())
        # Draw scroller
        pygame.draw.rect(
            screen,
            super().get_style()["foreground_color"],
            pygame.Rect(
                super().get_x() + self._scroller_pos,
                super().get_y(),
                self._scroller_size,
                super().get_height()
            ),
            border_radius=6
        )
        # Draw outline
        pygame.draw.rect(screen, super().get_style()["outline_color"], super().get_view_rect(), 2)

    @overrides(GUIElement)
    def process_event(self, view, event):
        super().process_event(view, event)
        if self._scroller_size >= super().get_width():
            return
        if not super().is_focused():
            return
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._start_scroller_pos = self._scroller_pos
            self._drag_start = event.pos[0]
        elif event.type == pygame.MOUSEBUTTONUP:
            super().un_focus()
            super().trigger_event(SUIEvents.EVENT_ON_BLUR)
        elif event.type == pygame.MOUSEMOTION:
            # Calculate relative position
            self._scroller_pos = self._start_scroller_pos + (event.pos[0] - self._drag_start)
            self._scroller_pos = min(max(0, self._scroller_pos), super().get_width() - self._scroller_size)
            self.relative_pos = self._scroller_pos / (super().get_width() - self._scroller_size)
            super().trigger_event(SUIEvents.EVENT_ON_CHANGE, self.relative_pos)