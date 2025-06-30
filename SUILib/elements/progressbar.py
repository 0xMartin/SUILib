"""
ProgressBar UI element for SUILib
"""

import pygame
from SUILib.guielement import GUIElement
from SUILib.utils import overrides, parser_udim
from SUILib.elements import Label

class ProgressBar(GUIElement):
    """
    Represents a horizontal progress bar UI element for SUILib applications.
    """

    def __init__(self, view, style: dict, value: float, min: float, max: float, 
                 width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new ProgressBar element.
        
        Args:
            view: The parent View instance where this progress bar is placed.
            style (dict): Dictionary containing style attributes for the progress bar.
            value (float): Initial value of the progress bar.
            min (float): Minimum value of the progress bar.
            max (float): Maximum value of the progress bar.
            width (int, optional): Width of the progress bar in pixels. Defaults to 0.
            height (int, optional): Height of the progress bar in pixels. Defaults to 0.
            x (int, optional): X coordinate of the progress bar. Defaults to 0.
            y (int, optional): Y coordinate of the progress bar. Defaults to 0.
        """
        self._label = None
        super().__init__(view, x, y, width, height, style, pygame.SYSTEM_CURSOR_ARROW)
        # Label bude vystředěný uvnitř progressbaru
        self._label = Label(view, self.get_style().get("label", {}), " ")
        self._label.set_anchor_x("50%")
        self._label.set_anchor_y("50%")
        self._format = "@ (#%)"  # defaultní formát
        self._min = min
        self._max = max
        self.set_value(value)

    def set_min(self, val: float):
        """
        Set the minimum value of the progress bar.
        
        Args:
            val (float): New minimum value.
        """
        self._min = val

    def set_max(self, val: float):
        """
        Set the maximum value of the progress bar.

        Args:
            val (float): New maximum value.
        """
        self._max = val

    def set_value(self, value: float):
        """
        Set the current value of the progress bar, clamping it between min and max.

        Args:
            value (float): New value to set.
        """
        self._value = max(self._min, min(self._max, value))
        self.refresh_label()

    def get_min(self) -> float:
        """
        Get the minimum value of the progress bar.

        Returns:
            float: The minimum value of the progress bar.
        """
        return self._min
    
    def get_max(self) -> float:
        """
        Get the maximum value of the progress bar.

        Returns:
            float: The maximum value of the progress bar.
        """
        return self._max
    
    def get_value(self) -> float:
        """
        Get the current value of the progress bar.

        Returns:
            float: The current value of the progress bar.
        """
        return self._value

    def get_percent(self) -> float:
        """
        Get the current percentage of the progress bar.

        Returns:
            float: The current percentage (0-100) of the progress bar.
        """
        return (self._value - self._min) / (self._max - self._min) * 100.0 if self._max > self._min else 0

    def set_label_format(self, format: str):
        """
        Set the format string for the slider's label.

        Args:
            format (str): Format string; use '#' for percentage and '@' for numerical value.
        """
        self._format = format
        self.refresh_label()

    def refresh_label(self):
        if self._label and self._format:
            txt = self._format
            txt = txt.replace("#", '%.2f' % self.get_percent())
            txt = txt.replace("@", '%.2f' % self.get_value())
            self._label.set_text(txt)

    @overrides(GUIElement)
    def update_view_rect(self):
        super().update_view_rect()
        # Label vždy doprostřed progressbaru
        if self._label:
            # Použij skutečnou pozici a rozměr progressbaru včetně anchorů a offsetu
            rect = self.get_view_rect()
            self._label.set_position(
                rect.x + rect.width // 2,
                rect.y + rect.height // 2
            )

    @overrides(GUIElement)
    def set_width(self, width):
        super().set_width(width)
        self.refresh_label()

    @overrides(GUIElement)
    def set_height(self, height):
        super().set_height(height)
        self.refresh_label()

    @overrides(GUIElement)
    def draw(self, view, screen):
        corner_radius = parser_udim(super().get_style()["corner_radius"], super().get_view_rect())
        rect = self.get_view_rect()
        
        # Pozadí
        pygame.draw.rect(screen, self.get_style()["background_color"], rect, border_radius=corner_radius)
        
        # Vyplněná část progressbaru
        percent = self.get_percent() / 100.0
        filled_width = int(rect.width * percent)
        fill_rect = pygame.Rect(rect.x, rect.y, filled_width, rect.height)
        pygame.draw.rect(
            screen,
            self.get_style()["foreground_color"],
            fill_rect,
            border_radius=corner_radius
        )
        # Outline
        pygame.draw.rect(screen, self.get_style()["outline_color"], rect, 2, border_radius=corner_radius)
        # Label doprostřed
        self._label.draw(view, screen)

    @overrides(GUIElement)
    def process_event(self, view, event):
        super().process_event(view, event)