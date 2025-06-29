"""
Slider UI element for SUILib
"""

import pygame
import math
from SUILib.guielement import GUIElement
from SUILib.events import SUIEvents
from SUILib.utils import overrides
from SUILib.colors import color_change
from SUILib.elements import Label


class Slider(GUIElement):
    """
    Represents a horizontal slider UI element for SUILib applications.

    The Slider allows users to select a value within a specified range by dragging a handle.
    The slider displays its current value as a label and supports customizable formatting,
    min/max constraints, and a value change callback.

    Attributes:
        label (Label): The label displaying the current slider value.
        min (float): The minimum value of the slider.
        max (float): The maximum value of the slider.
        position (float): The current x-position of the slider handle relative to the slider's width.
        format (str): String format for the label, using '#' for percentage and '@' for the numerical value.
    """
        
    def __init__(self, view, style: dict, number: float, min: float, max: float, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new Slider element.

        Args:
            view: The parent View instance where this slider is placed.
            style (dict): Dictionary containing style attributes for the slider.
                See config/styles.json for details.
            number (float): Initial value of the slider.
            min (float): Minimum value of the slider.
            max (float): Maximum value of the slider.
            width (int, optional): Width of the slider in pixels. Defaults to 0.
            height (int, optional): Height of the slider in pixels. Defaults to 0.
            x (int, optional): X coordinate of the slider. Defaults to 0.
            y (int, optional): Y coordinate of the slider. Defaults to 0.
        """
        self.label = None
        super().__init__(view, x, y, width, height, style, pygame.SYSTEM_CURSOR_SIZEWE)
        self.label = Label(view, super().get_style()["label"], " ", False, True)
        self.format = "@"
        self.min = min
        self.max = max
        self.set_number(number)

    def set_min(self, val: int):
        """
        Set the minimum value of the slider.

        Args:
            val (float): New minimum value.
        """
        self.min = val

    def set_max(self, val: int):
        """
        Set the maximum value of the slider.

        Args:
            val (float): New maximum value.
        """
        self.max = val

    def get_value(self) -> int:
        """
        Get the percentage value (0-100) of the slider based on handle position.

        Returns:
            float: The current value as a percentage.
        """
        dot_radius = super().get_height() / 2
        return (self.position - dot_radius) / (super().get_width() - dot_radius * 2) * 100

    def get_number(self) -> int:
        """
        Get the current number (min <= number <= max) represented by the slider.

        Returns:
            float: The current numerical value of the slider.
        """
        return self.get_value() / 100.0 * (self.max - self.min) + self.min

    def set_value(self, value: int):
        """
        Set the slider position by percentage value (0-100).

        Args:
            value (float): The value of the slider as a percentage (0-100).
        """
        if value is None:
            value = self.last_set_value
        if value is None:
            return
        if value < 0 or value > 100:
            return
        self.last_set_value = value
        dot_radius = super().get_height() / 2
        # set position
        self.position = dot_radius + value / 100.0 * \
            (super().get_width() - dot_radius * 2)

    def set_number(self, value: int):
        """
        Set the slider using a number in the range [min, max].

        Args:
            value (float): The value to set the slider to.
        """
        if value <= self.max and value >= self.min:
            value = (value - self.min) / (self.max - self.min) * 100
            self.set_value(value)

    def set_label_format(self, format: str):
        """
        Set the format string for the slider's label.

        Args:
            format (str): Format string; use '#' for percentage and '@' for numerical value.
        """
        self.format = format

    def refresh_label(self):
        """
        Update the slider label to display the current value using the format string.
        """
        if len(self.format) != 0:
            txt = self.format
            txt = txt.replace("#", '%.2f' % self.get_value())
            txt = txt.replace("@", '%.2f' % self.get_number())
            self.label.set_text(txt)

    @overrides(GUIElement)
    def update_view_rect(self):
        super().update_view_rect()
        if self.label is not None:
            self.label.set_x(super().get_x() + super().get_width() + 20)
            self.label.set_y(super().get_y() + super().get_height() / 2)

    @overrides(GUIElement)
    def set_width(self, width):
        super().set_width(width)
        self.set_value(None)
        self.refresh_label()

    @overrides(GUIElement)
    def set_height(self, height):
        super().set_height(height)
        self.set_value(None)
        self.refresh_label()

    @overrides(GUIElement)
    def draw(self, view, screen):
        # background
        pygame.draw.rect(screen, super().get_style()[
                         "background_color"], super().get_view_rect(), border_radius=10)
        # slider bar
        pygame.draw.rect(
            screen,
            color_change(super().get_style()["foreground_color"], 0.8),
            pygame.Rect(
                super().get_x(),
                super().get_y(),
                self.position,
                super().get_height()
            ),
            border_radius=10
        )
        # outline
        pygame.draw.rect(screen, super().get_style()[
                         "outline_color"], super().get_view_rect(), 2, border_radius=10)
        # slider
        pygame.draw.circle(
            screen,
            super().get_style()["foreground_color"],
            (super().get_x() + self.position,
             super().get_y() + super().get_height() / 2),
            super().get_height() * 0.8
        )
        # label with current value
        self.label.draw(view, screen)

    @overrides(GUIElement)
    def process_event(self, view, event):
        super().process_event(view, event)
        if event.type == pygame.MOUSEBUTTONUP:
            self.set_value(self.get_value())
        elif event.type == pygame.MOUSEMOTION:
            if super().is_focused():
                self.position = self.def_position + (event.pos[0] - self.drag_start)
                dot_radius = super().get_height() / 2
                self.position = min(
                    max(dot_radius, self.position), super().get_width() - dot_radius)
                self.refresh_label()
                super().trigger_event(SUIEvents.EVENT_ON_CHANGE, self.get_number())
