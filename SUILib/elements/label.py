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

    Attributes:
        text (str): The text content displayed by the label.
        h_centered (bool): Whether the text is horizontally centered.
        v_centered (bool): Whether the text is vertically centered.
        font (pygame.font.Font): Font object used for rendering the label text.
    """

    def __init__(self, view, style: dict, text: str, h_centered: bool = False, v_centered: bool = False, x: int = 0, y: int = 0):
        """
        Initialize a new Label element.

        Args:
            view: The parent View instance where this label is placed.
            style (dict): Dictionary containing style attributes for the label.
                See config/styles.json for details.
            text (str): The text to display on the label.
            h_centered (bool, optional): If True, center text horizontally. Defaults to False.
            v_centered (bool, optional): If True, center text vertically. Defaults to False.
            x (int, optional): X coordinate of the label. Defaults to 0.
            y (int, optional): Y coordinate of the label. Defaults to 0.
        """
        super().__init__(view, x, y, 0, 0, style)
        self.text = text
        self.h_centered = h_centered
        self.v_centered = v_centered
        self.font = pygame.font.SysFont(
            super().get_style()["font_name"],
            super().get_style()["font_size"],
            bold=super().get_style()["font_bold"]
        )

    def set_h_centered(self, centered: bool):
        """
        Set horizontal alignment for the label text.

        Args:
            centered (bool): If True, text will be horizontally centered at the label's X coordinate.
        """
        self.h_centered = centered

    def set_v_centered(self, centered: bool):
        """
        Set vertical alignment for the label text.

        Args:
            centered (bool): If True, text will be vertically centered at the label's Y coordinate.
        """
        self.v_centered = centered

    def set_text(self, text: str):
        """
        Set the text displayed by the label.

        Args:
            text (str): New label text.
        """
        self.text = text

    def get_text(self) -> str:
        """
        Get the current text content of the label.

        Returns:
            str: The label's text.
        """
        return self.text

    @overrides(GUIElement)
    def draw(self, view, screen):
        if len(self.text) != 0:
            text_surface = self.font.render(self.text, True, super().get_style()["foreground_color"])
            x = super().get_x()
            if self.h_centered:
                x -= text_surface.get_width() / 2
            y = super().get_y()
            if self.v_centered:
                y -= text_surface.get_height() / 2
            screen.blit(text_surface, (x, y))
