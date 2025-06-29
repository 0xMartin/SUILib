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
            x = super().get_x()
            y = super().get_y()
            # need to adjust position based on anchor here because label has no width/height
            anchor_x = super().get_anchor_x()
            anchor_y = super().get_anchor_y()
            if isinstance(anchor_x, str):
                x -= text_surface.get_width() // 2
            elif isinstance(anchor_x, int):
                x -= int(anchor_x * super().get_width())
            if isinstance(anchor_y, str):
                y -= text_surface.get_height() // 2
            elif isinstance(anchor_y, int):
                y -= int(anchor_y * super().get_height())
            screen.blit(text_surface, (x, y))
