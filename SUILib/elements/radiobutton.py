"""
RadioButton UI element for SUILib
"""

import pygame
from SUILib.guielement import GUIElement
from SUILib.events import SUIEvents
from SUILib.utils import overrides
from SUILib.colors import color_change
from SUILib.elements.label import Label

class RadioButton(GUIElement):
    """
    Represents a radio button UI element for SUILib applications.

    A radio button allows users to select a single option from a group. Only one radio button
    in a group can be checked at a time. Each radio button is associated with a label and a group,
    supports custom styles, click event callbacks, and integrates with the View layout system.
    """

    def __init__(self, view, style: dict, text: str, group, size=20, x: int = 0, y: int = 0):
        """
        Initialize a new RadioButton instance.

        Args:
            view: The parent View instance where this radio button is placed.
            style (dict): Dictionary containing style attributes for the radio button.
                See config/styles.json for details.
            text (str): Text to display as the radio button's label.
            group (RadioButtonGroup): Group to which this radio button belongs.
            size (int, optional): Diameter of the radio button in pixels. Defaults to 20.
            x (int, optional): X coordinate of the radio button. Defaults to 0.
            y (int, optional): Y coordinate of the radio button. Defaults to 0.
        """
        super().__init__(view, x, y, size, size, style)
        self._label = Label(view, super().get_style()["label"], text, x, y)
        self._label.set_anchor_y("50%")
        self._group = group
        self._group.add_radio_button(self)
        self._checked = False

    def set_text(self, text: str):
        """
        Set the text of the radio button's label.

        Args:
            text (str): New label text.
        """
        if self._label is not None:
            self._label.set_text(text)

    def get_label(self) -> Label:
        """
        Get the label object associated with this radio button.

        Returns:
            Label: The label instance.
        """
        return self._label

    def set_checked(self, checked: bool):
        """
        Set the checked state of this radio button.

        Args:
            checked (bool): True if the radio button should be checked, False otherwise.
        """
        self._checked = checked

    def is_checked(self) -> bool:
        """
        Return whether this radio button is currently checked.

        Returns:
            bool: True if checked, False otherwise.
        """
        return self._checked

    @overrides(GUIElement)
    def draw(self, view, screen):
        # Draw label
        if self._label is not None:
            self._label.set_x(super().get_x() + super().get_width() + 5)
            self._label.set_y(super().get_y() + super().get_height() / 2)
            self._label.draw(view, screen)
        # Draw radio button circle
        center = (
            super().get_x() + super().get_width() / 2,
            super().get_y() + super().get_width() / 2
        )
        if super().is_hovered():
            c = super().get_style()["background_color"]
            pygame.draw.circle(screen, color_change(c, -0.2 if c[0] > 128 else 0.6), center, super().get_width() / 2)
        else:
            pygame.draw.circle(screen, super().get_style()["background_color"], center, super().get_width() / 2)
        pygame.draw.circle(screen, super().get_style()["outline_color"], center, super().get_width() / 2, 2)
        # Draw check indicator if checked
        if self._checked:
            pygame.draw.circle(screen, super().get_style()["foreground_color"], center, super().get_width() / 4)

    @overrides(GUIElement)
    def process_event(self, view, event):
        super().process_event(view, event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if super().get_view_rect().collidepoint(event.pos):
                super().trigger_event(SUIEvents.EVENT_ON_CHANGE, self._label.get_text())
                self._group.check_radio_button(self)


class RadioButtonGroup:
    """
    Represents a group of RadioButton elements.

    The RadioButtonGroup manages a collection of radio buttons,
    ensuring that only one button in the group is checked at any time.
    """

    def __init__(self, radiobtns: list):
        """
        Initialize a new RadioButtonGroup.

        Args:
            radiobtns (list): List of RadioButton instances to add to the group.
        """
        self._radiobtns = []
        for r in radiobtns:
            if isinstance(r, RadioButton):
                self._radiobtns.append(r)

    def add_radio_button(self, radiobtn: RadioButton):
        """
        Add a RadioButton to this group.

        Args:
            radiobtn (RadioButton): The radio button to add.
        """
        if isinstance(radiobtn, RadioButton):
            self._radiobtns.append(radiobtn)

    def remove_radio_button(self, radiobtn: RadioButton):
        """
        Remove a RadioButton from this group.

        Args:
            radiobtn (RadioButton): The radio button to remove.
        """
        self._radiobtns.remove(radiobtn)

    def get_radio_button(self):
        """
        Return the currently checked radio button in the group.

        Returns:
            RadioButton: The checked radio button, or None if none is checked.
        """
        for r in self._radiobtns:
            if r.is_checked():
                return r

    def check_radio_button(self, radiobtn: RadioButton):
        """
        Set the specified radio button as checked and uncheck all others in the group.

        Args:
            radiobtn (RadioButton): The radio button to check.
        """
        if isinstance(radiobtn, RadioButton):
            for r in self._radiobtns:
                if r != radiobtn:
                    r.set_checked(False)
                else:
                    r.set_checked(True)