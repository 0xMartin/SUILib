"""
CheckBox UI element for SUILib
"""

import pygame
from SUILib.guielement import GUIElement, Container
from SUILib.utils import overrides
from SUILib.colors import color_change
from SUILib.elements.label import Label


class CheckBox(GUIElement, Container):
    """
    Represents a checkbox UI element with a label for SUILib applications.

    The CheckBox allows users to toggle a boolean state (checked/unchecked) and displays
    an associated label. It supports custom styles, click event callbacks, and integrates
    seamlessly within the View layout system.
    """

    def __init__(self, view, style: dict, text: str, checked: bool, size: int = 20, x: int = 0, y: int = 0):
        """
        Initialize a new CheckBox instance.

        Args:
            view: The parent View instance where this checkbox is placed.
            style (dict): Dictionary containing style attributes for the checkbox.
                See config/styles.json for details.
            text (str): Text to display as the checkbox label.
            checked (bool): Initial checked state of the checkbox.
            size (int, optional): Width and height of the checkbox square in pixels. Defaults to 20.
            x (int, optional): X coordinate of the checkbox. Defaults to 0.
            y (int, optional): Y coordinate of the checkbox. Defaults to 0.
        """
        self._label = None
        super().__init__(view, x, y, size, size, style)
        self._label = Label(view, super().get_style()["label"], text, x, y)
        self._label.set_anchor_y("50%")
        self._checked = checked

    def set_text(self, text: str):
        """
        Set the text of the checkbox label.

        Args:
            text (str): New label text.
        """
        if self._label is not None:
            self._label.set_text(text)

    def get_label(self) -> Label:
        """
        Get the label object associated with this checkbox.

        Returns:
            Label: The label instance.
        """
        return self._label

    def set_checked(self, checked: bool):
        """
        Set the checked state of this checkbox.

        Args:
            checked (bool): True if the checkbox should be checked, False otherwise.
        """
        self._checked = checked

    def is_checked(self) -> bool:
        """
        Return whether this checkbox is currently checked.

        Returns:
            bool: True if checked, False otherwise.
        """
        return self._checked

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
        # Position and draw the label
        if self._label is not None:
            self._label.draw(view, screen)
        # Draw checkbox background
        if super().is_hovered():
            c = super().get_style()["background_color"]
            pygame.draw.rect(
                screen,
                color_change(c, -0.2 if c[0] > 128 else 0.6),
                super().get_view_rect(),
                border_radius=6
            )
        else:
            pygame.draw.rect(
                screen,
                super().get_style()["background_color"],
                super().get_view_rect(),
                border_radius=5
            )
        # Draw checkbox outline
        pygame.draw.rect(
            screen,
            super().get_style()["outline_color"],
            super().get_view_rect(),
            2,
            border_radius=5
        )
        # Draw checkmark if checked
        if self._checked:
            pts = [
                (super().get_x() + super().get_width() * 0.2, super().get_y() + super().get_width() * 0.5),
                (super().get_x() + super().get_width() * 0.4, super().get_y() + super().get_width() * 0.75),
                (super().get_x() + super().get_width() * 0.8, super().get_y() + super().get_width() * 0.2)
            ]
            pygame.draw.lines(
                screen,
                super().get_style()["foreground_color"],
                False,
                pts,
                round(7 * super().get_width() / 40)
            )

    @overrides(GUIElement)
    def process_event(self, view, event):
        super().process_event(view, event)
        if self.is_focused() and event.type == pygame.MOUSEBUTTONDOWN:
            self._checked = not self._checked

    @overrides(Container)  
    def get_childs(self):
        return [self._label]
