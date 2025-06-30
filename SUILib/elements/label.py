"""
Label UI element for SUILib
"""

import pygame
from SUILib.guielement import GUIElement
from SUILib.utils import overrides


class Label(GUIElement):
    """
    Represents a static text label UI element for SUILib applications.

    The Label displays a single line of text, optionally aligned horizontally and/or vertically
    relative to its coordinates. It supports custom styles, font settings, and integrates with
    the View layout system. Labels are typically used as captions, titles, or static annotations
    within the interface.
    """

    def __init__(self, view, style: dict, text: str, x: int = 0, y: int = 0):
        """
        Initialize a new Label element.

        Args:
            view: The parent View instance where this label is placed.
            style (dict): Dictionary containing style attributes for the label.
                See config/styles.json for details.
            text (str): The text to display on the label.
            x (int, optional): X coordinate of the label. Defaults to 0.
            y (int, optional): Y coordinate of the label. Defaults to 0.
        """
        super().__init__(view, x, y, 0, 0, style)
        self._text = text
        self._offset_x = 0
        self._offset_y = 0
        self._font = pygame.font.SysFont(
            super().get_style()["font_name"],
            super().get_style()["font_size"],
            bold=super().get_style()["font_bold"]
        )

    def set_text(self, text: str):
        """
        Set the text displayed by the label.

        Args:
            text (str): New label text.
        """
        self._text = text

    def get_text(self) -> str:
        """
        Get the current text content of the label.

        Returns:
            str: The label's text.
        """
        return self._text

    @overrides(GUIElement)
    def draw(self, view, screen):
        if len(self._text) != 0:
            text_surface = self._font.render(self._text, True, super().get_style()["foreground_color"])
            x = super().get_x() + self.get_offset_x()
            y = super().get_y() + self.get_offset_y()
            # need to adjust position based on anchor here because label has no width/height
            anchor_x = super().get_anchor_x()
            anchor_y = super().get_anchor_y()
            x -= self._parse_anchor(anchor_x, text_surface.get_width())
            y -= self._parse_anchor(anchor_y, text_surface.get_height())
            screen.blit(text_surface, (x, y))

    def _parse_anchor(self, anchor, size):
        """
        Convert anchor value (int or percent string) to px offset.
        Examples:
            - 0      -> 0
            - 15     -> 15
            - "50%"  -> 0.5 * size
            - "100%" -> size
        """
        if isinstance(anchor, int):
            return anchor
        elif isinstance(anchor, str) and anchor.endswith('%'):
            try:
                percent = float(anchor[:-1]) / 100.0
                return int(size * percent)
            except ValueError:
                return 0
        else:
            return 0
