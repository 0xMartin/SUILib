"""
Button UI element for SUILib
"""

import pygame
from SUILib.guielement import GUIElement
from SUILib.utils import overrides, parser_udim
from SUILib.colors import color_change

class Button(GUIElement):
    """
    Represents a clickable button UI element for SUILib applications.

    The Button displays customizable text, supports style configuration,
    and triggers a callback function when clicked. It handles rendering
    with hover and selection effects, and automatically adjusts its size
    to fit the text content.
    """

    def __init__(self, view, style: dict, text: str, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new Button instance.

        Args:
            view: The parent View instance where this button is placed.
            style (dict): Dictionary containing style attributes for the button.
                See config/styles.json for details.
            text (str): The text to display on the button.
            width (int, optional): Width of the button in pixels. Defaults to 0 (auto).
            height (int, optional): Height of the button in pixels. Defaults to 0 (auto).
            x (int, optional): X coordinate of the button. Defaults to 0.
            y (int, optional): Y coordinate of the button. Defaults to 0.
        """
        super().__init__(view, x, y, width, height, style)
        self._text = text
        self._font = pygame.font.SysFont(
            super().get_style()["font_name"],
            super().get_style()["font_size"],
            bold=super().get_style()["font_bold"]
        )

    def set_text(self, text: str):
        """
        Set the button's display text.

        Args:
            text (str): New text to display on the button.
        """
        self._text = text

    def get_text(self) -> str:
        """
        Get the current text displayed on the button.

        Returns:
            str: The button's display text.
        """
        return self._text

    @overrides(GUIElement)
    def draw(self, view, screen):
        corner_radius = parser_udim(super().get_style()["corner_radius"], super().get_view_rect())

        # Draw button background with selection effect
        if super().is_hovered():
            c = super().get_style()["background_color"]
            pygame.draw.rect(
                screen,
                color_change(c, -0.2 if c[0] > 128 else 0.6),
                super().get_view_rect(),
                border_radius=corner_radius
            )
        else:
            pygame.draw.rect(
                screen,
                super().get_style()["background_color"],
                super().get_view_rect(),
                border_radius=corner_radius
            )
        # Draw button text
        if len(self._text) != 0:
            text_surface = self._font.render(
                self._text, True, super().get_style()["foreground_color"]
            )
            # Auto-resize button to fit text if needed
            if text_surface.get_height() + 4 > super().get_height():
                super().set_height(text_surface.get_height() + 4)
            if text_surface.get_width() + 4 > super().get_width():
                super().set_width(text_surface.get_width() + 4)
            screen.blit(
                text_surface,
                (
                    super().get_x() + (super().get_width() - text_surface.get_width()) / 2,
                    super().get_y() + (super().get_height() - text_surface.get_height()) / 2
                )
            )
        # Draw button outline
        pygame.draw.rect(
            screen,
            super().get_style()["outline_color"],
            super().get_view_rect(),
            2,
            border_radius=corner_radius
        )