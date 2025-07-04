"""
TabPanel UI element for SUILib
"""

import pygame
from ..utils import *
from ..colors import *
from ..guielement import *
from ..application import *


class TabPanel(GUIElement, Container):
    """
    Represents a tabbed panel UI element for SUILib applications.

    The TabPanel displays multiple child panels, each accessible by a tab header at the top.
    Only one tab's content is visible at a time. Supports custom styles, arbitrary tab content,
    and integrates with the View layout system.

    Attributes:
        tabs (list): List of Tab objects (each with a name and content element).
        selected_tab (int): Index of the currently selected tab.
        font (pygame.font.Font): Font used for rendering tab headers.
    """

    def __init__(self, view, style: dict, tabs: list, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new TabPanel instance.

        Args:
            view: The parent View instance where this tab panel is placed.
            style (dict): Dictionary describing the style for the panel.
                See config/styles.json for details.
            tabs (list): List of Tab objects.
            width (int, optional): Width of the panel in pixels. Defaults to 0.
            height (int, optional): Height of the panel in pixels. Defaults to 0.
            x (int, optional): X coordinate of the panel. Defaults to 0.
            y (int, optional): Y coordinate of the panel. Defaults to 0.
        """
        GUIElement.__init__(self, view, x, y, width, height, style)
        self.layoutmanager = None
        self.selected_tab = 0
        self.font = pygame.font.SysFont(
            super().get_style()["font_name"],
            super().get_style()["font_size"],
            bold=super().get_style()["font_bold"]
        )
        self.tabs = []
        for t in tabs:
            if isinstance(t, Tab):
                self.add_tab(t)

    def set_tabs(self, tabs: list):
        """
        Set the panel's tabs.

        Args:
            tabs (list): List of Tab objects.
        """
        self.tabs = []
        for t in tabs:
            if isinstance(t, Tab):
                self.add_tab(t)

    def set_selected_tab(self, index: int):
        """
        Set the selected tab by index.

        Args:
            index (int): The index of the tab to select.
        """
        self.selected_tab = index

    def add_tab(self, tab):
        """
        Add a new tab to the panel.

        Args:
            tab (Tab): The Tab object to add.
        """
        if isinstance(tab, Tab):
            self.tabs.append(tab)
            self.update_tab_size(tab)

    def update_tab_size(self, tab):
        """
        Update the size of the content of a tab to match the TabPanel.

        Args:
            tab (Tab): The Tab whose content size should be updated.
        """
        content = tab.get_content()
        if content is not None:
            tab_header_height = self.font.render(
                "W", 1, super().get_style()["foreground_color"]
            ).get_height() + 10
            content.set_x(0)
            content.set_y(0)
            content.set_width(super().get_width())
            content.set_height(super().get_height() - tab_header_height)
            if isinstance(content, Layout) and content.get_width() > 0 and content.get_height() > 0:
                content.update_layout(0, 0)

    def remove_tab(self, tab):
        """
        Remove a tab from the panel.

        Args:
            tab (Tab): The Tab object to remove.
        """
        self.tabs.remove(tab)

    @overrides(GUIElement)
    def set_width(self, width):
        super().set_width(width)
        for tab in self.tabs:
            self.update_tab_size(tab)

    @overrides(GUIElement)
    def set_height(self, height):
        super().set_height(height)
        for tab in self.tabs:
            self.update_tab_size(tab)

    @overrides(GUIElement)
    def draw(self, view, screen):
        if len(self.tabs) == 0:
            return

        tab_header_height = 0
        selected_x = [0, 0]
        x_offset = 5 + super().get_x()
        # Draw tab headers
        for i, tab in enumerate(self.tabs):
            if len(tab.get_name()) != 0:
                text = self.font.render(
                    tab.get_name(),
                    1,
                    super().get_style()["foreground_color"]
                )
                tab_header_height = max(tab_header_height, text.get_height() + 10)
                x1 = x_offset
                x2 = x_offset + text.get_width() + 10
                if i == self.selected_tab:
                    pygame.draw.rect(
                        screen,
                        super().get_style()["background_color"],
                        pygame.Rect(
                            x1,
                            super().get_y(),
                            x2 - x1,
                            tab_header_height
                        )
                    )
                    selected_x = [x1 + 2, x2 - 1]
                pygame.draw.lines(
                    screen,
                    super().get_style()["outline_color"],
                    False,
                    [
                        (x1, super().get_y() + tab_header_height),
                        (x1, super().get_y()),
                        (x2, super().get_y()),
                        (x2, super().get_y() + tab_header_height)
                    ],
                    2
                )
                screen.blit(
                    text,
                    (x_offset + 5, 5 + super().get_y())
                )
                x_offset += text.get_width() + 10

        rect = pygame.Rect(
            super().get_x(),
            super().get_y() + tab_header_height,
            super().get_width(),
            super().get_height() - tab_header_height
        )

        # Draw tab content background
        pygame.draw.rect(
            screen,
            super().get_style()["background_color"],
            rect,
            border_radius=5
        )
        pygame.draw.rect(
            screen,
            super().get_style()["outline_color"],
            rect,
            2,
            border_radius=5
        )
        # Draw content of selected tab
        if self.selected_tab >= 0 and self.selected_tab < len(self.tabs):
            tab_screen = screen.subsurface(rect)
            content = self.tabs[self.selected_tab].get_content()
            if content is not None:
                content.draw(view, tab_screen)
        # Draw line under selected tab header to blend it with background
        pygame.draw.line(
            screen,
            super().get_style()["background_color"],
            (selected_x[0], super().get_y() + tab_header_height),
            (selected_x[1], super().get_y() + tab_header_height),
            2
        )

    @overrides(GUIElement)
    def process_event(self, view, event):
        # Handle tab header clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            x_offset = 5 + super().get_x()
            for i, tab in enumerate(self.tabs):
                if len(tab.get_name()) != 0:
                    text = self.font.render(
                        tab.get_name(),
                        1,
                        super().get_style()["foreground_color"]
                    )
                    x1 = x_offset
                    x2 = x_offset + text.get_width() + 10
                    rect = pygame.Rect(
                        x1,
                        super().get_y(),
                        x2 - x1,
                        text.get_height() + 10
                    )
                    x_offset += text.get_width() + 10
                    if in_rect(event.pos[0], event.pos[1], rect):
                        self.selected_tab = i
                        break

        # Offset event for content (so children receive proper local coords)
        tab_header_height = self.font.render(
            "W", 1, super().get_style()["foreground_color"]
        ).get_height() + 10
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN):
            event.pos = (
                event.pos[0] - super().get_x(),
                event.pos[1] - super().get_y() - tab_header_height
            )
        # Propagate event to selected tab content
        if self.selected_tab >= 0 and self.selected_tab < len(self.tabs):
            content = self.tabs[self.selected_tab].get_content()
            if content is not None:
                content.process_event(view, event)
        # Restore event position
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN):
            event.pos = (
                event.pos[0] + super().get_x(),
                event.pos[1] + super().get_y() + tab_header_height
            )

    @overrides(GUIElement)
    def update(self, view):
        """
        Update logic for the tab panel and its child contents.

        Args:
            view: The parent View instance.
        """
        for tab in self.tabs:
            if tab.get_content() is not None:
                tab.get_content().update(view)

    @overrides(Container)
    def get_childs(self):
        """
        Return the content elements of all tabs as children.

        Returns:
            list: List of tab content GUIElement objects.
        """
        result = []
        for tab in self.tabs:
            if tab.get_content() is not None:
                result.append(tab.get_content())
        return result


class Tab:
    """
    Represents a single tab in a TabPanel.

    Attributes:
        name (str): Tab label.
        content (GUIElement): Content element displayed when this tab is selected.
    """

    def __init__(self, name: str, content: GUIElement):
        self.name = name
        if isinstance(content, GUIElement):
            self.content = content
        else:
            self.content = None

    def get_name(self):
        """
        Return the tab's label.
        """
        return self.name

    def set_name(self, name: str):
        """
        Set the tab's label.
        """
        self.name = name

    def get_content(self):
        """
        Return the content GUIElement of the tab.
        """
        return self.content

    def set_content(self, content: GUIElement):
        """
        Set the content GUIElement of the tab.
        """
        if isinstance(content, GUIElement):
            self.content = content
