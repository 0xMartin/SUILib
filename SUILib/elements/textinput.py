"""
TextInput UI element for SUILib
"""

import pygame
import re
import string
from ..utils import *
from ..colors import *
from ..guielement import *


class TextInput(GUIElement):
    """
    Represents a single-line text input UI element for SUILib applications.

    The TextInput allows users to enter or edit a string, supports caret navigation,
    optional input filtering via regex, and triggers a callback when the text is changed/committed.

    Attributes:
        text (str): The current text content.
        caret_position (int): The caret position within the text.
        callback (callable): Function to call when the text is changed/committed.
        filter_pattern (re.Pattern): Optional compiled regex for input validation.
        font (pygame.font.Font): Font object used for rendering the text.
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
        self.callback = None
        self.filter_pattern = None
        self.text = text
        self.caret_position = len(text)
        self.font = pygame.font.SysFont(
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
        self.text = text
        self.caret_position = len(text)

    def get_text(self):
        """
        Get the current text value.

        Returns:
            str: The text in the input.
        """
        return self.text

    def set_text_changed_evt(self, callback):
        """
        Set the callback function to be called when the text is changed/committed.

        Args:
            callback (callable): Function to be invoked with the new text.
        """
        self.callback = callback

    def set_filter_pattern(self, pattern: str):
        """
        Set a regular expression pattern that the text must match when committed.

        Args:
            pattern (str): Regex pattern as a string.
        """
        self.filter_pattern = re.compile(pattern)

    @overrides(GUIElement)
    def draw(self, view, screen):
        """
        Render the text input box, its text, caret, and outline.

        Args:
            view: The parent View instance.
            screen (pygame.Surface): The surface to render the input onto.
        """
        # background
        if super().is_selected():
            c = super().get_style()["background_color"]
            pygame.draw.rect(screen, color_change(
                c, 0.4 if c[0] > 128 else 0.7), super().get_view_rect(), border_radius=5)
        else:
            pygame.draw.rect(screen, super().get_style()["background_color"], super().get_view_rect(), border_radius=5)

        # create subsurface for text (clipping)
        surface = screen.subsurface(super().get_view_rect())
        text_offset = 0
        caret_offset = 0
        if len(self.text) != 0:
            text_surface = self.font.render(
                self.text,
                1,
                super().get_style()["foreground_color"]
            )
            # calculate caret offset
            caret_offset = self.font.size(self.text[0: self.caret_position])[0]
            # offset for text
            text_offset = max(caret_offset + 20 - super().get_width(), 0)
            if not super().is_selected():
                text_offset = 0
            # draw text
            surface.blit(
                text_surface, (5 - text_offset, (super().get_height() - text_surface.get_height()) / 2)
            )

        # caret
        if super().is_selected() and generate_signal(400):
            x = 5 - text_offset + caret_offset
            y = surface.get_height() * 0.2
            pygame.draw.line(surface, super().get_style()["foreground_color"], (x, y), (x, surface.get_height() - y), 2)

        # outline
        pygame.draw.rect(screen, super().get_style()["outline_color"], super().get_view_rect(), 2, border_radius=5)

    @overrides(GUIElement)
    def process_event(self, view, event):
        """
        Handle Pygame events for text input focus, editing, and caret navigation.

        Args:
            view: The parent View instance.
            event (pygame.event.Event): The event to process.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if in_rect(event.pos[0], event.pos[1], super().get_view_rect()):
                super().select()
                # Move caret to end on focus
                self.caret_position = len(self.text)
            else:
                self.unselect_ti()
        elif event.type == pygame.KEYDOWN:
            if super().is_selected():
                if event.key == pygame.K_RETURN:
                    self.unselect_ti()
                elif event.key == pygame.K_BACKSPACE:
                    i = self.caret_position
                    if i > 0 and len(self.text) > 0:
                        # Remove char before caret
                        self.text = self.text[:i-1] + self.text[i:]
                        self.caret_position = max(0, self.caret_position - 1)
                elif event.key == pygame.K_LEFT:
                    self.caret_position = max(0, self.caret_position - 1)
                elif event.key == pygame.K_RIGHT:
                    self.caret_position = min(len(self.text), self.caret_position + 1)
                else:
                    # Insert new char at caret
                    if hasattr(event, "unicode") and event.unicode in string.printable and event.unicode != '':
                        i = self.caret_position
                        self.text = self.text[:i] + event.unicode + self.text[i:]
                        self.caret_position += 1

    @overrides(GUIElement)
    def update(self, view):
        """
        Update logic for the text input.

        Args:
            view: The parent View instance.
        """
        pass

    def unselect_ti(self):
        """
        Handle unselecting the text input, call text changed event, and validate filter if set.
        """
        if super().is_selected():
            # text filter
            if self.filter_pattern is not None:
                if not self.filter_pattern.match(self.text):
                    # clear text if invalid
                    self.text = ""
            if self.callback is not None:
                self.callback(self.text)
        super().un_select()