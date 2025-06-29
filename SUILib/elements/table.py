"""
Table UI element for SUILib
"""

import pygame
from SUILib.guielement import GUIElement, Container
from SUILib.events import SUIEvents
from SUILib.utils import overrides
from SUILib.colors import color_change
from SUILib.elements.vertical_scrollbar import VerticalScrollbar
from SUILib.elements.horizontal_scrollbar import HorizontalScrollbar


class Table(GUIElement, Container):
    """
    Represents a scrollable table UI element for SUILib applications.

    The Table displays a tabular dataset with headers and rows, supports both horizontal and vertical
    scrolling via integrated scrollbars, and dynamically sizes columns based on content and style.

    Attributes:
        header (list): List of column header strings.
        body (list): List of rows, each a list of cell strings.
        col_width (list): List of column widths in pixels.
        v_scroll (VerticalScrollbar): Vertical scrollbar for table body.
        h_scroll (HorizontalScrollbar): Horizontal scrollbar for table body.
        header_font (pygame.font.Font): Font for header cells.
        body_font (pygame.font.Font): Font for body cells.
        body_offset_x (float): Horizontal scroll offset.
        body_offset_y (float): Vertical scroll offset.
    """

    def __init__(self, view, style: dict, data: dict, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new Table element.

        Args:
            view: The parent View instance where this table is placed.
            style (dict): Dictionary containing style attributes for the table.
                See config/styles.json for details.
            data (dict): Dictionary with table data: {"header": [...], "body": [[...], ...]}.
            width (int, optional): Width of the table in pixels. Defaults to 0.
            height (int, optional): Height of the table in pixels. Defaults to 0.
            x (int, optional): X coordinate of the table. Defaults to 0.
            y (int, optional): Y coordinate of the table. Defaults to 0.
        """
        self.last_data = None
        self.body_offset_x = 0
        self.body_offset_y = 0
        super().__init__(view, x, y, width, height, style)
        # vertical scrollbar
        self.v_scroll = VerticalScrollbar(
            view,
            super().get_style()["scrollbar"],
            super().get_style()["body"]["scrollbar_width"]
        )
        self.v_scroll.add_event_callback(SUIEvents.EVENT_ON_CHANGE, self.table_scroll_vertical)
        # horizontal scrollbar
        self.h_scroll = HorizontalScrollbar(
            view,
            super().get_style()["scrollbar"],
            super().get_style()["body"]["scrollbar_width"]
        )
        self.h_scroll.add_event_callback(SUIEvents.EVENT_ON_CHANGE, self.table_scroll_horizontal)
        # initialize table data
        self.refresh_table(data)

    def table_scroll_vertical(self, position: float):
        """
        Handle vertical scroll event for table body.

        Args:
            position (float): Vertical position of table body (0.0 - 1.0).
        """
        header_height = self.header_font.get_height() * 1.8
        total_body_data_height = header_height + self.body_font.get_height() * 1.4 * len(self.body)
        h = super().get_height() - super().get_style()["body"]["scrollbar_width"]
        self.body_offset_y = -max(0, (total_body_data_height - h)) * position

    def table_scroll_horizontal(self, position: float):
        """
        Handle horizontal scroll event for table body.

        Args:
            position (float): Horizontal position of table body (0.0 - 1.0).
        """
        total_body_data_width = sum(self.col_width)
        w = super().get_width() - super().get_style()["body"]["scrollbar_width"]
        self.body_offset_x = -max(0, (total_body_data_width - w)) * position

    def refresh_table(self, data: dict = None):
        """
        Refresh or update the table data and recompute layout.

        Args:
            data (dict, optional): Dictionary with table data: {"header": [...], "body": [[...], ...]}.
                If None, uses the last data provided.
        """
        if data is None:
            data = self.last_data
        self.last_data = data
        if data is None:
            return

        self.header_font = pygame.font.SysFont(
            super().get_style()["header"]["font_name"],
            super().get_style()["header"]["font_size"],
            bold=super().get_style()["header"]["font_bold"]
        )
        self.body_font = pygame.font.SysFont(
            super().get_style()["body"]["font_name"],
            super().get_style()["body"]["font_size"],
            bold=super().get_style()["body"]["font_bold"]
        )
        self.header = data["header"]
        self.body = data["body"]

        scroll_size = super().get_style()["body"]["scrollbar_width"]

        # calculate max width for each col of table
        self.col_width = [0] * len(self.header)
        for row in self.body:
            for i, cell in enumerate(row):
                self.col_width[i] = max(self.body_font.size(cell)[0] + 10, self.col_width[i])
        for i, cell in enumerate(self.header):
            self.col_width[i] = max(self.header_font.size(cell)[0] + 10, self.col_width[i])
        if sum(self.col_width) <= super().get_width() - scroll_size:
            for i in range(len(self.header)):
                self.col_width[i] = super().get_width() / len(self.header)

        # vertical scrollbar
        self.v_scroll.set_x(
            super().get_x() + super().get_width() - 1 - scroll_size)
        self.v_scroll.set_y(super().get_y())
        self.v_scroll.set_width(scroll_size)
        self.v_scroll.set_height(super().get_height())
        header_height = self.header_font.get_height() * 1.8
        total_body_data_height = header_height + self.body_font.get_height() * 1.4 * len(self.body)
        self.v_scroll.set_scroller_size(
            (1.0 - max(0, total_body_data_height - super().get_height()) / total_body_data_height) * self.v_scroll.get_height())

        # horizontal scrollbar
        self.h_scroll.set_x(super().get_x())
        self.h_scroll.set_y(
            super().get_y() + super().get_height() - 1 - scroll_size)
        self.h_scroll.set_width(super().get_width() - scroll_size)
        self.h_scroll.set_height(scroll_size)
        total_body_data_width = sum(self.col_width)
        self.h_scroll.set_scroller_size(
            (1.0 - max(0, total_body_data_width - super().get_width()) / total_body_data_width) * self.h_scroll.get_width())

    @overrides(GUIElement)
    def update_view_rect(self):
        super().update_view_rect()
        self.refresh_table()

    @overrides(GUIElement)
    def draw(self, view, screen):
        # set clip
        screen.set_clip(
            pygame.Rect(
                super().get_x(),
                super().get_y(),
                super().get_width() - 1,
                super().get_height() - 1,
            )
        )

        # size of table body + header
        w = super().get_width() - super().get_style()["body"]["scrollbar_width"]
        h = super().get_height() - super().get_style()["body"]["scrollbar_width"]
        rect = pygame.Rect(
            super().get_x(),
            super().get_y(),
            w,
            h
        )
        # draw table body background
        pygame.draw.rect(
            screen,
            super().get_style()["body"]["background_color"],
            rect
        )
        # draw col lines
        offset = self.body_offset_x
        for i in range(len(self.header)):
            pygame.draw.line(
                screen,
                color_change(super().get_style()["body"]["background_color"], -0.5),
                (super().get_x() + offset, super().get_y()),
                (super().get_x() + offset, super().get_y() + h - 4),
                2
            )
            offset += self.col_width[i]

        # draw body data
        for j, row in enumerate(self.body):
            offset = self.body_offset_x
            for i, cell in enumerate(row):
                if len(cell) != 0:
                    text = self.body_font.render(
                        cell, 1, super().get_style()["body"]["foreground_color"])
                    header_offset = self.header_font.get_height() * 1.8
                    screen.blit(
                        text,
                        (
                            super().get_x() + 5 + offset,
                            super().get_y() + header_offset +
                            self.body_font.get_height() * 1.4 * j + self.body_offset_y
                        )
                    )
                    offset += self.col_width[i]

        # draw table header
        if self.header is not None:
            pygame.draw.rect(
                screen,
                super().get_style()["header"]["background_color"],
                pygame.Rect(
                    super().get_x(),
                    super().get_y(),
                    w,
                    self.header_font.get_height() * 1.8
                )
            )
            offset = self.body_offset_x
            for i, col in enumerate(self.header):
                if len(col) != 0:
                    text = self.header_font.render(
                        col, 1, super().get_style()["header"]["foreground_color"])
                    screen.blit(
                        text,
                        (
                            super().get_x() + 5 + offset,
                            super().get_y() + self.header_font.get_height() * 0.4
                        )
                    )
                    offset += self.col_width[i]

        # draw v_scrollbar
        self.v_scroll.draw(view, screen)
        # draw h_scrollbar
        self.h_scroll.draw(view, screen)

        # draw outline
        pygame.draw.rect(
            screen,
            super().get_style()["header"]["background_color"],
            rect,
            2
        )

        # reset clip
        screen.set_clip(None)

    @overrides(GUIElement)
    def process_event(self, view, event):
        self.v_scroll.process_event(view, event)
        self.h_scroll.process_event(view, event)

    @overrides(Container)  
    def get_childs(self):
        return [self.v_scroll, self.h_scroll]
