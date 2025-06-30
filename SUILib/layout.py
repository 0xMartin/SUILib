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


class VBoxLayout(Layout):
    """
    Layout manager for arranging elements vertically relative to a parent.

    Elements are marked as "parent" or "child". The parent remains in its
    position, while child elements are stacked vertically starting from the parent.

    Example usage:
        vb = VBoxLayout(self)
        vb.add_element(parent_widget, "parent")
        vb.add_element(child_widget, "child")

    """

    def __init__(self, view):
        """
        Initialize VBoxLayout for a given View.

        Args:
            view (View): View instance for which the layout manager is registered.
        """
        super().__init__(view)

    @overrides(Layout)
    def update_layout(self, width, height):
        """
        Update positions of parent/child elements vertically.

        Args:
            width (int): Width of the view/screen.
            height (int): Height of the view/screen.
        """
        elements = super().get_layout_elements()
        cnt = len(elements)
        if cnt == 0:
            return

        parent = next((el for el in elements
                      if el["propt"] == "parent"), None)
        if parent is None:
            return
        parent = parent["element"]

        h_step = (height - parent.get_y()) / cnt if cnt > 0 else 0

        i = 1
        for el in elements:
            if el["propt"] == "child":
                gui_el = el["element"]
                if gui_el != parent:
                    i += 1
                    gui_el.set_x(parent.get_x())
                gui_el.set_y(parent.get_y() + i * h_step)

class HBoxLayout(Layout):
    """
    Layout manager for arranging elements horizontally relative to a parent.

    Elements are marked as "parent" or "child". The parent remains in its
    position, while child elements are stacked horizontally starting from the parent.

    Example usage:
        hb = HBoxLayout(self)
        hb.add_element(parent_widget, "parent")
        hb.add_element(child_widget, "child")
    """

    def __init__(self, view):
        """
        Initialize HBoxLayout for a given View.

        Args:
            view (View): View instance for which the layout manager is registered.
        """
        super().__init__(view)

    @overrides(Layout)
    def update_layout(self, width, height):
        """
        Update positions of parent/child elements horizontally.

        Args:
            width (int): Width of the view/screen.
            height (int): Height of the view/screen.
        """
        elements = super().get_layout_elements()
        cnt = len(elements)
        if cnt == 0:
            return

        parent = next((el for el in elements
                      if el["propt"] == "parent"), None)
        if parent is None:
            return
        parent = parent["element"]

        w_step = (width - parent.get_x()) / cnt if cnt > 0 else 0

        i = 1
        for el in elements:
            if el["propt"] == "child":
                gui_el = el["element"]
                gui_el.set_x(parent.get_x() + i * w_step)
                if gui_el != parent:
                    i += 1
                    gui_el.set_y(parent.get_y())

class GridLayout(Layout):
    """
    Layout manager for arranging elements in a grid.

    Elements are added row-wise. Specify the number of columns.
    Example usage:
        grid = GridLayout(self, columns=3)
        grid.add_element(widget1)
        grid.add_element(widget2)
        ...
    """

    def __init__(self, view, columns):
        """
        Initialize GridLayout for a given View.

        Args:
            view (View): View instance for which the layout manager is registered.
            columns (int): Number of columns in the grid.
        """
        super().__init__(view)
        self.columns = columns

    @overrides(Layout)
    def update_layout(self, width, height):
        elements = super().get_layout_elements()
        cnt = len(elements)
        if cnt == 0:
            return
        rows = (cnt + self.columns - 1) // self.columns
        cell_w = width / self.columns
        cell_h = height / rows

        for idx, el in enumerate(elements):
            gui_el = el["element"]
            row = idx // self.columns
            col = idx % self.columns
            gui_el.set_x(col * cell_w)
            gui_el.set_y(row * cell_h)