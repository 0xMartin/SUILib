"""
TextArea UI element for SUILib
"""

import pygame
import re
import string
import time
from SUILib.guielement import GUIElement
from SUILib.utils import overrides, parser_udim, generate_signal
from SUILib.colors import color_change
from SUILib.events import SUIEvents
from SUILib.threadmanager import ThreadManager

class TextArea(GUIElement):
    """
    Represents a multi-line text input UI element for SUILib applications.

    The TextArea allows users to enter or edit multi-line text, supports caret navigation,
    selection, mouse-based caret positioning, and triggers an event when the text is changed.
    """

    def __init__(self, view, style: dict, text: str, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initializes the TextArea with the given parameters.
        
        Args:
            view (View): The parent view for this TextArea.
            style (dict): The style dictionary for the TextArea.
            text (str): Initial text content for the TextArea.
            width (int): Width of the TextArea. Defaults to 0.
            height (int): Height of the TextArea. Defaults to 0.
            x (int): X position of the TextArea. Defaults to 0.
            y (int): Y position of the TextArea. Defaults to 0.
        """
        super().__init__(view, x, y, width, height, style, pygame.SYSTEM_CURSOR_IBEAM)
        self._filter_pattern = None
        self._lines = text.split('\n')
        self._caret_row = len(self._lines) - 1
        self._caret_col = len(self._lines[-1]) if self._lines else 0
        self._font = pygame.font.SysFont(
            self.get_style()["font_name"],
            self.get_style()["font_size"],
            bold=self.get_style()["font_bold"]
        )
        self._scroll = 0
        self._caret_blink_thread = None
        self._selection_anchor = None  # (row, col) or None
        self._mouse_selecting = False

    def set_text(self, text: str):
        """
        Sets the text content of the TextArea and updates the caret position.

        Args:
            text (str): The new text content to set in the TextArea.
        """
        self._lines = text.split('\n')
        self._caret_row = len(self._lines) - 1
        self._caret_col = len(self._lines[-1]) if self._lines else 0
        self._selection_anchor = None

    def get_text(self):
        """
        Gets the current text content of the TextArea.

        Returns:
            str: The current text content of the TextArea.
        """
        return '\n'.join(self._lines)

    def set_filter_pattern(self, pattern: str):
        """
        Sets a regex pattern to filter the text input in the TextArea. 
        Use basic regex to define valid input.

        Args:
            pattern (str): The regex pattern to filter the text input.
        """
        self._filter_pattern = re.compile(pattern)

    def get_visible_lines(self):
        """
        Returns the currently visible lines in the TextArea based on the scroll
        position and the view rectangle along with the height of each line.

        Returns:
            tuple: A tuple containing a list of visible lines and the height of each line.
        """
        rect = self.get_view_rect()
        line_height = self._font.get_linesize()
        max_lines = max(rect.height // line_height, 1)
        return self._lines[self._scroll:self._scroll+max_lines], line_height

    def _caret_blink_loop(self, stop_event):
        """
        A loop that blinks the caret by requesting a repaint of the TextArea
        at regular intervals while the TextArea is focused.

        Args:
            stop_event (Event): An event that signals when to stop the caret blink loop.
        """
        while not stop_event.is_set():
            if self.is_focused():
                super().get_view().request_repaint()
            time.sleep(0.4)

    @overrides(GUIElement)
    def focus(self):
        super().focus()

        # Start the caret blink thread if it is not already running
        self._caret_blink_thread = ThreadManager.instance().run_task(self._caret_blink_loop)

    @overrides(GUIElement)
    def un_focus(self):
        super().un_focus()

        # Stop the caret blink thread if it exists
        if self._caret_blink_thread is not None:
            self._caret_blink_thread.stop()
        self._selection_anchor = None

        # Clear the text if it does not match the filter pattern
        if self._filter_pattern is not None:
            if not self._filter_pattern.match(self.get_text()):
                self.set_text("")
        self._clear_selection()

        # Trigger an event to notify that the text has changed
        self.trigger_event(SUIEvents.EVENT_ON_CHANGE, self.get_text())

    def _has_selection(self):
        """
        Checks if there is a text selection in the TextArea.

        Returns:
            bool: True if there is a selection, False otherwise.
        """
        return self._selection_anchor is not None and (self._selection_anchor != (self._caret_row, self._caret_col))

    def _get_selection_range(self):
        """
        Returns the range of the current text selection as a tuple of tuples.

        Returns:
            tuple: A tuple containing the start and end positions of the selection as ((row1, col1), (row2, col2)).
                   Returns None if there is no selection.
        """
        if not self._has_selection():
            return None
        (row1, col1) = self._selection_anchor
        (row2, col2) = (self._caret_row, self._caret_col)
        if (row1, col1) <= (row2, col2):
            return (row1, col1), (row2, col2)
        else:
            return (row2, col2), (row1, col1)

    def _clear_selection(self):
        """
        Clears the current text selection in the TextArea.
        Resets the selection anchor and caret position.
        """
        self._selection_anchor = None

    def _delete_selection(self):
        """
        Deletes the currently selected text in the TextArea.
        If there is a selection, it removes the selected text and updates the caret position.
        If the selection spans multiple lines, it merges the lines into one.
        """
        sel = self._get_selection_range()
        if sel:
            (r1, c1), (r2, c2) = sel
            if r1 == r2:
                self._lines[r1] = self._lines[r1][:c1] + self._lines[r1][c2:]
                self._caret_row, self._caret_col = r1, c1
            else:
                first = self._lines[r1][:c1]
                last = self._lines[r2][c2:]
                self._lines[r1:r2+1] = [first + last]
                self._caret_row, self._caret_col = r1, c1
            self._clear_selection()

    def _get_char_pos_from_mouse(self, mouse_x, mouse_y):
        """
        Calculate the character position in the text area based on mouse coordinates.
        
        Args:
            mouse_x (int): The x-coordinate of the mouse position.
            mouse_y (int): The y-coordinate of the mouse position.  
            
        Returns:
            tuple: A tuple containing the line index and column index of the character closest to the mouse position.
        """
        rect = self.get_view_rect()
        visible_lines, line_height = self.get_visible_lines()
        y = mouse_y - rect.y
        idx = int(y // line_height)
        idx = min(max(idx, 0), len(visible_lines) - 1)
        line_index = self._scroll + idx
        line = self._lines[line_index]
        rel_x = mouse_x - rect.x - 5  # 5px padding
        min_dist = float('inf')
        col = 0
        for i in range(len(line) + 1):
            char_x = self._font.size(line[:i])[0]
            dist = abs(char_x - rel_x)
            if dist < min_dist:
                min_dist = dist
                col = i
        return (line_index, col)

    @overrides(GUIElement)
    def draw(self, view, screen):
        orig_rect = self.get_view_rect()
        screen_rect = screen.get_rect()
        rect = orig_rect.clip(screen_rect)
        if rect.width == 0 or rect.height == 0:
            return

        surface = screen.subsurface(rect)
        dx = rect.x - orig_rect.x
        dy = rect.y - orig_rect.y

        corner_radius = parser_udim(self.get_style()["corner_radius"], orig_rect)

        # background
        if self.is_focused():
            c = self.get_style()["background_color"]
            pygame.draw.rect(
                surface,
                color_change(c, 0.4 if c[0] > 128 else 0.7),
                pygame.Rect(dx, dy, orig_rect.width, orig_rect.height),
                border_radius=corner_radius
            )
        else:
            pygame.draw.rect(
                surface,
                self.get_style()["background_color"],
                pygame.Rect(dx, dy, orig_rect.width, orig_rect.height),
                border_radius=corner_radius
            )

        # text clipping region
        visible_lines, line_height = self.get_visible_lines()
        y_offset = 0
        caret_x = caret_y = None

        # selection highlight
        if self._has_selection():
            (r1, c1), (r2, c2) = self._get_selection_range()
            for idx, line in enumerate(visible_lines):
                line_index = self._scroll + idx
                y = y_offset + dy
                if r1 <= line_index <= r2:
                    start_col = c1 if line_index == r1 else 0
                    end_col = c2 if line_index == r2 else len(self._lines[line_index])
                    x1 = 5 + dx + self._font.size(self._lines[line_index][:start_col])[0]
                    x2 = 5 + dx + self._font.size(self._lines[line_index][:end_col])[0]
                    pygame.draw.rect(
                        surface,
                        self.get_style().get("selection_color", (40, 120, 200, 120)),
                        (min(x1, x2), y, abs(x2 - x1), line_height)
                    )
                y_offset += line_height
            y_offset = 0  # reset for text

        # text and caret
        for idx, line in enumerate(visible_lines):
            text_surface = self._font.render(line, 1, self.get_style()["foreground_color"])
            surface.blit(text_surface, (5 + dx, y_offset + dy))
            if self.is_focused() and (self._caret_row - self._scroll) == idx:
                caret_x = 5 + dx + self._font.size(line[:self._caret_col])[0]
                caret_y = y_offset + dy
            y_offset += line_height

        # caret
        if self.is_focused() and caret_x is not None and caret_y is not None and generate_signal(400):
            pygame.draw.line(
                surface,
                self.get_style()["foreground_color"],
                (caret_x, caret_y - 3),
                (caret_x, caret_y + line_height - 3),
                2
            )

        # outline
        pygame.draw.rect(
            surface,
            self.get_style()["outline_color"],
            pygame.Rect(dx, dy, orig_rect.width, orig_rect.height),
            2,
            border_radius=corner_radius
        )

    @overrides(GUIElement)
    def process_event(self, view, event):
        super().process_event(view, event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the TextArea is focused, update the caret position
            # and start mouse selection if the button is pressed
            if self.get_view_rect().collidepoint(event.pos):
                (row, col) = self._get_char_pos_from_mouse(event.pos[0], event.pos[1])
                self._caret_row = row
                self._caret_col = col
                self._selection_anchor = (row, col)
                self._mouse_selecting = True

        elif event.type == pygame.MOUSEBUTTONUP:
            # Check if the mouse button is released over the TextArea
            self._mouse_selecting = False

        elif event.type == pygame.MOUSEMOTION:
            # If the mouse is moving while the button is pressed, update the caret position
            if self._mouse_selecting:
                (row, col) = self._get_char_pos_from_mouse(event.pos[0], event.pos[1])
                self._caret_row = row
                self._caret_col = col

        elif event.type == pygame.KEYDOWN:
            # Handle key events for text input, navigation, and editing
            if self.is_focused():
                shift = pygame.key.get_mods() & pygame.KMOD_SHIFT
                ctrl = pygame.key.get_mods() & pygame.KMOD_CTRL
                line = self._lines[self._caret_row]

                if event.key == pygame.K_RETURN:
                    # Insert a new line at the caret position
                    self._delete_selection() if self._has_selection() else None
                    before = line[:self._caret_col]
                    after = line[self._caret_col:]
                    self._lines[self._caret_row] = before
                    self._lines.insert(self._caret_row + 1, after)
                    self._caret_row += 1
                    self._caret_col = 0
                    self._clear_selection()

                elif event.key == pygame.K_BACKSPACE:
                    # Delete the character before the caret or selected text
                    if self._has_selection():
                        self._delete_selection()
                    elif self._caret_col > 0:
                        self._lines[self._caret_row] = line[:self._caret_col - 1] + line[self._caret_col:]
                        self._caret_col -= 1
                    elif self._caret_row > 0:
                        prev_len = len(self._lines[self._caret_row - 1])
                        self._lines[self._caret_row - 1] += self._lines[self._caret_row]
                        del self._lines[self._caret_row]
                        self._caret_row -= 1
                        self._caret_col = prev_len
                    self._clear_selection()

                elif event.key == pygame.K_DELETE:
                    # Delete the character after the caret or selected text
                    if self._has_selection():
                        self._delete_selection()
                    elif self._caret_col < len(line):
                        self._lines[self._caret_row] = line[:self._caret_col] + line[self._caret_col + 1:]
                    elif self._caret_row < len(self._lines) - 1:
                        self._lines[self._caret_row] += self._lines[self._caret_row + 1]
                        del self._lines[self._caret_row + 1]
                    self._clear_selection()

                elif event.key == pygame.K_LEFT:
                    # Move the caret left, with shift for selection
                    if shift:
                        if self._selection_anchor is None:
                            self._selection_anchor = (self._caret_row, self._caret_col)
                        if self._caret_col > 0:
                            self._caret_col -= 1
                        elif self._caret_row > 0:
                            self._caret_row -= 1
                            self._caret_col = len(self._lines[self._caret_row])
                    else:
                        if self._has_selection():
                            (row1, col1), (row2, col2) = self._get_selection_range()
                            self._caret_row, self._caret_col = row1, col1
                        else:
                            if self._caret_col > 0:
                                self._caret_col -= 1
                            elif self._caret_row > 0:
                                self._caret_row -= 1
                                self._caret_col = len(self._lines[self._caret_row])
                        self._clear_selection()

                elif event.key == pygame.K_RIGHT:
                    # Move the caret right, with shift for selection
                    if shift:
                        if self._selection_anchor is None:
                            self._selection_anchor = (self._caret_row, self._caret_col)
                        if self._caret_col < len(line):
                            self._caret_col += 1
                        elif self._caret_row < len(self._lines) - 1:
                            self._caret_row += 1
                            self._caret_col = 0
                    else:
                        if self._has_selection():
                            (row1, col1), (row2, col2) = self._get_selection_range()
                            self._caret_row, self._caret_col = row2, col2
                        else:
                            if self._caret_col < len(line):
                                self._caret_col += 1
                            elif self._caret_row < len(self._lines) - 1:
                                self._caret_row += 1
                                self._caret_col = 0
                        self._clear_selection()

                elif event.key == pygame.K_UP:
                    # Move the caret up, with shift for selection
                    if shift:
                        if self._selection_anchor is None:
                            self._selection_anchor = (self._caret_row, self._caret_col)
                        if self._caret_row > 0:
                            self._caret_row -= 1
                            self._caret_col = min(self._caret_col, len(self._lines[self._caret_row]))
                    else:
                        if self._caret_row > 0:
                            self._caret_row -= 1
                            self._caret_col = min(self._caret_col, len(self._lines[self._caret_row]))
                        self._clear_selection()

                elif event.key == pygame.K_DOWN:
                    # Move the caret down, with shift for selection
                    if shift:
                        if self._selection_anchor is None:
                            self._selection_anchor = (self._caret_row, self._caret_col)
                        if self._caret_row < len(self._lines) - 1:
                            self._caret_row += 1
                            self._caret_col = min(self._caret_col, len(self._lines[self._caret_row]))
                    else:
                        if self._caret_row < len(self._lines) - 1:
                            self._caret_row += 1
                            self._caret_col = min(self._caret_col, len(self._lines[self._caret_row]))
                        self._clear_selection()

                elif ctrl and event.key == pygame.K_a:
                    # select all
                    self._selection_anchor = (0, 0)
                    self._caret_row = len(self._lines) - 1
                    self._caret_col = len(self._lines[-1])

                else:
                    # Handle text input
                    if hasattr(event, "unicode") and event.unicode in string.printable and event.unicode != '':
                        if self._has_selection():
                            self._delete_selection()
                        line = self._lines[self._caret_row]
                        self._lines[self._caret_row] = line[:self._caret_col] + event.unicode + line[self._caret_col:]
                        self._caret_col += 1
                        self._clear_selection()