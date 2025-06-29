"""
ToggleButton UI element for SUILib
"""

import pygame
from SUILib.guielement import GUIElement
from SUILib.events import SUIEvents
from SUILib.utils import overrides
from SUILib.elements.label import Label
from SUILib.colors import color_change


class ToggleButton(GUIElement):
    """
    Represents a toggle (switch) button UI element for SUILib applications.

    The ToggleButton acts as an ON/OFF switch with an optional label. It supports
    custom styles, click callbacks, and integrates with the View layout system.

    Attributes:
        label (Label): The label displayed next to the toggle button.
        status (bool): The ON/OFF state of the toggle.
    """

    def __init__(self, view, style: dict, text: str, status: bool = False, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new ToggleButton instance.

        Args:
            view: The parent View instance where this toggle button is placed.
            style (dict): Dictionary containing style attributes for the toggle.
                See config/styles.json for details.
            text (str): The text of the label next to the toggle.
            status (bool, optional): Initial ON/OFF state. Defaults to False (OFF).
            width (int, optional): Width of the toggle in pixels. Defaults to 0.
            height (int, optional): Height of the toggle in pixels. Defaults to 0.
            x (int, optional): X coordinate of the toggle. Defaults to 0.
            y (int, optional): Y coordinate of the toggle. Defaults to 0.
        """
        super().__init__(view, x, y, width, height, style)
        self.label = Label(view, super().get_style()["label"], text, False, True)
        self.status = status

    def set_text(self, text: str):
        """
        Set the text of the toggle's label.

        Args:
            text (str): New text for the label.
        """
        if self.label is not None:
            self.label.set_text(text)

    def get_status(self) -> bool:
        """
        Get the ON/OFF status of the toggle button.

        Returns:
            bool: True if ON, False if OFF.
        """
        return self.status

    def get_label(self) -> Label:
        """
        Get the Label object associated with this toggle.

        Returns:
            Label: The label instance.
        """
        return self.label

    @overrides(GUIElement)
    def draw(self, view, screen):
        # Background and outline
        if self.status:
            bg_color = color_change(super().get_style()["foreground_color"], 0.8)
        else:
            bg_color = super().get_style()["background_color"]
        pygame.draw.rect(
            screen,
            bg_color,
            super().get_view_rect(),
            border_radius=int(super().get_height() / 2)
        )
        pygame.draw.rect(
            screen,
            super().get_style()["outline_color"],
            super().get_view_rect(),
            2,
            border_radius=int(super().get_height() / 2)
        )
        # Toggle switch handle
        if self.status:
            pos = super().get_width() - super().get_height() / 2
            pygame.draw.circle(
                screen,
                super().get_style()["foreground_color"],
                (super().get_x() + pos, super().get_y() + super().get_height() / 2),
                super().get_height() / 2
            )
        else:
            pygame.draw.circle(
                screen,
                super().get_style()["foreground_color"],
                (super().get_x() + super().get_height() / 2, super().get_y() + super().get_height() / 2),
                super().get_height() / 2
            )
        # Label
        if self.label is not None:
            self.label.set_x(super().get_x() + super().get_width() + 5)
            self.label.set_y(super().get_y() + super().get_height() / 2)
            self.label.draw(view, screen)

    @overrides(GUIElement)
    def process_event(self, view, event):
        super().process_event(view, event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if super().get_view_rect().collidepoint(event.pos):
                self.status = not self.status
                super().trigger_event(SUIEvents.EVENT_ON_CHANGE, self.status)