"""
TextInput UI element for SUILib
"""

import pygame
import re
import string
from SUILib.guielement import GUIElement
from SUILib.utils import overrides, generate_signal
from SUILib.colors import color_change
from SUILib.events import SUIEvents

class TextInput(GUIElement):
    """
    Represents a single-line text input UI element for SUILib applications.

    The TextInput allows users to enter or edit a string, supports caret navigation,
    optional input filtering via regex, and triggers a callback when the text is changed/committed.
    """

    def __init__(self, view, style: dict, text: str, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new TextInput element.

        Args:
            view: The parent View instance where this text input is placed.
            style (dict): Dictionary describing the style for this element.
                See config/styles.json for details.
            text (str): Initial text for the input.
            width (int, optional): Width of the input in pixels. Defaults to 0.
            height (int, optional): Height of the input in pixels. Defaults to 0.
            x (int, optional): X coordinate of the input. Defaults to 0.
            y (int, optional): Y coordinate of the input. Defaults to 0.
        """
        super().__init__(view, x, y, width, height, style, pygame.SYSTEM_CURSOR_IBEAM)
        self._filter_pattern = None
        self._text = text
        self._caret_position = len(text)
        self._font = pygame.font.SysFont(
            super().get_style()["font_name"],
            super().get_style()["font_size"],
            bold=super().get_style()["font_bold"]
        )

    def set_text(self, text: str):
        """
        Set the current text value.

        Args:
            text (str): New text string for this input.
        """
        self._text = text
        self._caret_position = len(text)

    def get_text(self):
        """
        Get the current text value.

        Returns:
            str: The text in the input.
        """
        return self._text

    def set_filter_pattern(self, pattern: str):
        """
        Set a regular expression pattern that the text must match when committed.

        Args:
            pattern (str): Regex pattern as a string.
        """
        self._filter_pattern = re.compile(pattern)

    @overrides(GUIElement)
    def draw(self, view, screen):
        # background
        if super().is_focused():
            c = super().get_style()["background_color"]
            pygame.draw.rect(screen, color_change(
                c, 0.4 if c[0] > 128 else 0.7), super().get_view_rect(), border_radius=5)
        else:
            pygame.draw.rect(screen, super().get_style()["background_color"], super().get_view_rect(), border_radius=5)

        # create subsurface for text (clipping)
        surface = screen.subsurface(super().get_view_rect())
        text_offset = 0
        caret_offset = 0
        if len(self._text) != 0:
            text_surface = self._font.render(
                self._text,
                1,
                super().get_style()["foreground_color"]
            )
            # calculate caret offset
            caret_offset = self._font.size(self._text[0: self._caret_position])[0]
            # offset for text
            text_offset = max(caret_offset + 20 - super().get_width(), 0)
            if not super().is_focused():
                text_offset = 0
            # draw text
            surface.blit(
                text_surface, (5 - text_offset, (super().get_height() - text_surface.get_height()) / 2)
            )

        # caret
        if super().is_focused() and generate_signal(400):
            x = 5 - text_offset + caret_offset
            y = surface.get_height() * 0.2
            pygame.draw.line(surface, super().get_style()["foreground_color"], (x, y), (x, surface.get_height() - y), 2)

        # outline
        pygame.draw.rect(screen, super().get_style()["outline_color"], super().get_view_rect(), 2, border_radius=5)

    @overrides(GUIElement)
    def process_event(self, view, event):
        super().process_event(view, event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if super().get_view_rect().collidepoint(event.pos):
                super().focus()
                # Move caret to end on focus
                self._caret_position = len(self._text)
            else:
                self.unselect_text_input()
        elif event.type == pygame.KEYDOWN:
            if super().is_focused():
                if event.key == pygame.K_RETURN:
                    self.unselect_text_input()
                elif event.key == pygame.K_BACKSPACE:
                    i = self._caret_position
                    if i > 0 and len(self._text) > 0:
                        # Remove char before caret
                        self._text = self._text[:i-1] + self._text[i:]
                        self._caret_position = max(0, self._caret_position - 1)
                elif event.key == pygame.K_LEFT:
                    self._caret_position = max(0, self._caret_position - 1)
                elif event.key == pygame.K_RIGHT:
                    self._caret_position = min(len(self._text), self._caret_position + 1)
                else:
                    # Insert new char at caret
                    if hasattr(event, "unicode") and event.unicode in string.printable and event.unicode != '':
                        i = self._caret_position
                        self._text = self._text[:i] + event.unicode + self._text[i:]
                        self._caret_position += 1

    def unselect_text_input(self):
        """
        Handle unselecting the text input, call text changed event, and validate filter if set.
        """
        if super().is_focused():
            # text filter
            if self._filter_pattern is not None:
                if not self._filter_pattern.match(self._text):
                    # clear text if invalid
                    self._text = ""
            super().trigger_event(SUIEvents.EVENT_ON_CHANGE, self._text)
        super().un_focus()