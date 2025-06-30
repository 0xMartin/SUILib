"""
ToggleButton UI element for SUILib
"""

import pygame
from SUILib.guielement import GUIElement, Container
from SUILib.events import SUIEvents
from SUILib.utils import overrides
from SUILib.elements.label import Label
from SUILib.colors import color_change


class ToggleButton(GUIElement, Container):
    """
    Represents a toggle (switch) button UI element for SUILib applications.

    The ToggleButton acts as an ON/OFF switch with an optional label. It supports
    custom styles, click callbacks, and integrates with the View layout system.
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
        self._label = None
        super().__init__(view, x, y, width, height, style)
        self._label = Label(view, super().get_style()["label"], text)
        self._label.set_anchor_y("50%")
        self._status = status

    def set_text(self, text: str):
        """
        Set the text of the toggle's label.

        Args:
            text (str): New text for the label.
        """
        if self._label is not None:
            self._label.set_text(text)

    def get_status(self) -> bool:
        """
        Get the ON/OFF status of the toggle button.

        Returns:
            bool: True if ON, False if OFF.
        """
        return self._status

    def get_label(self) -> Label:
        """
        Get the Label object associated with this toggle.

        Returns:
            Label: The label instance.
        """
        return self._label

    @overrides(GUIElement)
    def update_view_rect(self):
        super().update_view_rect()
        if self._label is not None:
            self._label.set_position(
                super().get_x() + super().get_width() + 5, 
                super().get_y() + super().get_height() / 2
            )

    @overrides(GUIElement)
    def draw(self, view, screen):
        # Background and outline
        if self._status:
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
        if self._status:
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
        if self._label is not None:
            self._label.draw(view, screen)

    @overrides(GUIElement)
    def process_event(self, view, event):
        super().process_event(view, event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if super().get_view_rect().collidepoint(event.pos):
                self._status = not self._status
                super().trigger_event(SUIEvents.EVENT_ON_CHANGE, self._status)
    
    @overrides(Container)  
    def get_childs(self):
        return [self._label]