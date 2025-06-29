"""
Layout managers for SUILib GUI framework

This module provides layout manager classes for arranging GUI elements within a View.
It includes AbsoluteLayout for pixel/percentage-based positioning and sizing,
and RelativeLayout for stacking elements relative to a parent in horizontal or vertical fashion.
"""

from .utils import *
from .colors import *
from .application import Layout   


class AbsoluteLayout(Layout):
    """
    Layout manager for absolute positioning and sizing of GUI elements.

    Allows setting element positions and sizes in pixels or percentages
    (e.g., "50%", "120"). Percentage values are recalculated to pixels
    on layout update, enabling responsive or fixed layouts.

    Example usage:
        al = AbsoluteLayout(self)
        label = Label(self, None, "Label 1", True)
        al.add_element(label, ['50%', '5%'])  # Centered horizontally, near top
        button = Button(self, None, "Button 1", True)
        al.add_element(button, ['50%', '5%', '30%', '10%'])  # Centered horizontally, 30% width, 10% height

    Attributes:
        Inherited from Layout.
    """

    def __init__(self, view):
        """
        Initialize AbsoluteLayout for a given View.

        Args:
            view (View): View instance for which the layout manager is registered.
        """
        super().__init__(view)

    @overrides(Layout)
    def update_layout(self, width, height):
        """
        Update positions and sizes of all managed GUI elements.

        Args:
            width (int): Width of the view/screen.
            height (int): Height of the view/screen.
        """
        for el in super().get_layout_elements():
            gui_el = el["element"]
            propts = el["propt"]
            if propts is not None:
                for i, propt in enumerate(propts):
                    if propt[-1] == '%':
                        val = float(propt[0:-1])
                        if i % 2 == 0:
                            val = val / 100.0 * width
                        else:
                            val = val / 100.0 * height
                    else:
                        val = float(propt)
                    if i == 0:
                        gui_el.set_x(val)
                    elif i == 1:
                        gui_el.set_y(val)
                    elif i == 2:
                        gui_el.set_width(val)
                    else:
                        gui_el.set_height(val)


class RelativeLayout(Layout):
    """
    Layout manager for arranging elements relative to a parent.

    Elements are marked as "parent" or "child". The parent remains in its
    position, while child elements are stacked horizontally or vertically
    starting from the parent.

    Example usage:
        rl = RelativeLayout(self, horizontal=True)
        rl.add_element(parent_widget, "parent")
        rl.add_element(child_widget, "child")

    Attributes:
        horizontal (bool): If True, stack horizontally; else vertically.
    """

    def __init__(self, view, horizontal):
        """
        Initialize RelativeLayout for a given View.

        Args:
            view (View): View instance for which the layout manager is registered.
            horizontal (bool): If True, stack children horizontally; else vertically.
        """
        super().__init__(view)
        self.horizontal = horizontal

    @overrides(Layout)
    def update_layout(self, width, height):
        """
        Update positions of parent/child elements according to stacking direction.

        Args:
            width (int): Width of the view/screen.
            height (int): Height of the view/screen.
        """
        cnt = len(super().get_layout_elements())
        if cnt == 0:
            return

        parent = next((el for el in super().get_layout_elements()
                      if el["propt"] == "parent"), None)
        if parent is None:
            return
        parent = parent["element"]

        if self.horizontal:
            w_step = (width - parent.get_x()) / (cnt)
            h_step = height / (cnt)
        else:
            w_step = width / (cnt)
            h_step = (height - parent.get_y()) / (cnt)

        i = 1
        for el in super().get_layout_elements():
            if el["propt"] is not None:
                if el["propt"] == "child":
                    gui_el = el["element"]
                    if self.horizontal:
                        gui_el.set_x(parent.get_x() + i * w_step)
                        if gui_el != parent:
                            i = i + 1
                            gui_el.set_y(parent.get_y())
                    else:
                        if gui_el != parent:
                            i = i + 1
                            gui_el.set_x(parent.get_x())
                        gui_el.set_y(parent.get_y() + i * h_step)