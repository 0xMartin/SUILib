"""
Panel UI element for SUILib
"""

import pygame
import copy
from SUILib.guielement import GUIElement, Container
from SUILib.application import Layout
from SUILib.utils import overrides, parser_udim

class Panel(GUIElement, Layout, Container):
    """
    Represents a container panel UI element for SUILib applications.

    The Panel serves as a flexible container for layout of multiple child elements. It supports
    custom layout managers, background and outline rendering, and event delegation to contained elements.
    Panels are typically used to organize groups of controls or visual content within an interface.
    """

    def __init__(self, view, style: dict, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new Panel element.

        Args:
            view: The parent View instance where this panel is placed.
            style (dict): Dictionary containing style attributes for the panel.
                See config/styles.json for details.
            width (int, optional): Width of the panel in pixels. Defaults to 0.
            height (int, optional): Height of the panel in pixels. Defaults to 0.
            x (int, optional): X coordinate of the panel. Defaults to 0.
            y (int, optional): Y coordinate of the panel. Defaults to 0.
        """
        GUIElement.__init__(self, view, x, y, width, height, style)
        Layout.__init__(self, view)
        self._layoutmanager = None

    def set_layout_manager(self, layoutmanager: Layout):
        """
        Set the layout manager for arranging elements inside the panel.

        Args:
            layoutmanager (Layout): The layout manager instance.
        """
        self._layoutmanager = layoutmanager
        self.get_view().unregister_layout_manager(self._layoutmanager)

    @overrides(GUIElement)
    def draw(self, view, screen):
        corner_radius = parser_udim(super().get_style()["corner_radius"], super().get_view_rect())

        # Draw background
        pygame.draw.rect(screen, super().get_style()["background_color"], super().get_view_rect(), border_radius=corner_radius)

        # Draw child elements within panel area
        if len(self.get_layout_elements()) != 0:
            panel_screen = screen.subsurface(
                pygame.Rect(
                    super().get_x() + 5,
                    super().get_y() + 5,
                    min(max(super().get_width() - 10, 10), screen.get_width() - super().get_x() - 5),
                    min(max(super().get_height() - 10, 10), screen.get_height() - super().get_y() - 5)
                )
            )
            for el in self.get_layout_elements():
                el["element"].draw(view, panel_screen)

        # Draw outline
        pygame.draw.rect(screen, super().get_style()["outline_color"], super().get_view_rect(), 2, border_radius=corner_radius)

    @overrides(GUIElement)
    def process_event(self, view, event):
        if len(self.get_layout_elements()) != 0:
            panel_evt = pygame.event.Event(event.type, **copy.deepcopy(event.dict))

            # Offset event position for child elements
            if panel_evt.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN):
                panel_evt.pos = (
                    panel_evt.pos[0] - super().get_x(),
                    panel_evt.pos[1] - super().get_y()
                )

            # Propagate event to each child element
            for el in self.get_layout_elements():
                el["element"].process_event(view, panel_evt)

            # Restore event position
            if panel_evt.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN):
                panel_evt.pos = (
                    panel_evt.pos[0] + super().get_x(),
                    panel_evt.pos[1] + super().get_y()
                )

    @overrides(GUIElement)
    def update(self, view):
        for el in self.get_layout_elements():
            el["element"].update(view)

    @overrides(Layout)
    def update_layout(self, width, height):
        if self._layoutmanager is not None:
            self._layoutmanager.set_elements(self.get_layout_elements())
            self._layoutmanager.update_layout(
                self.get_width() - 10, self.get_height() - 10
            )

    @overrides(Container)
    def get_childs(self):
        elements = []
        for le in self.get_layout_elements():
            elements.append(le["element"])
        return elements