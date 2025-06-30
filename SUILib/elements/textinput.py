"""
TextInput UI element for SUILib
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

class TextInput(GUIElement):
    """
    Represents a single-line text input UI element for SUILib applications.

    The TextInput allows users to enter or edit a string, supports caret navigation,
    optional input filtering via regex, and triggers a callback when the text is changed/committed.
    Supports mouse-based caret positioning and text selection.
    """

    def __init__(self, view, style: dict, text: str, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        super().__init__(view, x, y, width, height, style, pygame.SYSTEM_CURSOR_IBEAM)
        self._filter_pattern = None
        self._text = text
        self._caret_position = len(text)
        self._selection_anchor = None   # None = no selection, else int
        self._caret_blink_thread = None
        self._font = pygame.font.SysFont(
            super().get_style()["font_name"],
            super().get_style()["font_size"],
            bold=super().get_style()["font_bold"]
        )
        self._mouse_selecting = False

    def set_text(self, text: str):
        self._text = text
        self._caret_position = len(text)
        self._selection_anchor = None

    def get_text(self):
        return self._text

    def set_filter_pattern(self, pattern: str):
        self._filter_pattern = re.compile(pattern)

    def _caret_blink_loop(self, stop_event):
        while not stop_event.is_set():
            if self.is_focused():
                super().get_view().request_repaint()
            time.sleep(0.4)

    @overrides(GUIElement)
    def focus(self):
        super().focus()
        self._caret_blink_thread = ThreadManager.instance().run_task(self._caret_blink_loop)

    @overrides(GUIElement)
    def un_focus(self):
        super().un_focus()
        if self._caret_blink_thread is not None:
            self._caret_blink_thread.stop()

    def _get_text_offset(self):
        """Returns scroll offset in pixels for text rendering."""
        caret_offset = self._font.size(self._text[:self._caret_position])[0]
        text_offset = max(caret_offset + 20 - super().get_width(), 0)
        return text_offset

    def _get_caret_x(self, pos=None, text_offset=None):
        """Returns X pixel of caret for given pos (or current), minus scroll offset."""
        if pos is None:
            pos = self._caret_position
        if text_offset is None:
            text_offset = self._get_text_offset()
        return 5 - text_offset + self._font.size(self._text[:pos])[0]

    def _get_char_pos_from_mouse(self, mouse_x):
        """Get caret position (int) from mouse x coordinate (relative to widget)."""
        text_offset = self._get_text_offset()
        rel_x = mouse_x - super().get_view_rect().x - 5 + text_offset
        # Find nearest character
        min_dist = float('inf')
        pos = 0
        for i in range(len(self._text)+1):
            char_x = self._font.size(self._text[:i])[0]
            dist = abs(char_x - rel_x)
            if dist < min_dist:
                min_dist = dist
                pos = i
        return pos

    def _has_selection(self):
        return self._selection_anchor is not None and self._selection_anchor != self._caret_position

    def _get_selection_range(self):
        if not self._has_selection():
            return None
        a, b = self._caret_position, self._selection_anchor
        return min(a, b), max(a, b)

    def _delete_selection(self):
        "Delete selected text, set caret and clear anchor."
        sel = self._get_selection_range()
        if sel:
            self._text = self._text[:sel[0]] + self._text[sel[1]:]
            self._caret_position = sel[0]
            self._selection_anchor = None

    @overrides(GUIElement)
    def draw(self, view, screen):
        corner_radius = parser_udim(super().get_style()["corner_radius"], super().get_view_rect())
        rect = super().get_view_rect()

        # background
        if super().is_focused():
            c = super().get_style()["background_color"]
            pygame.draw.rect(
                screen, 
                color_change(c, 0.2 if c[0] > 128 else 0.7), 
                rect, 
                border_radius=corner_radius
            )
        else:
            pygame.draw.rect(
                screen, 
                super().get_style()["background_color"], 
                rect, 
                border_radius=corner_radius
            )

        # create subsurface for text (clipping)
        surface = screen.subsurface(rect)
        text_offset = self._get_text_offset()
        caret_offset = self._font.size(self._text[0: self._caret_position])[0]
        y_center = (super().get_height() - self._font.get_height()) / 2

        # selection highlight
        if self._has_selection():
            sel_start, sel_end = self._get_selection_range()
            x1 = self._get_caret_x(sel_start, text_offset)
            x2 = self._get_caret_x(sel_end, text_offset)
            pygame.draw.rect(
                surface,
                super().get_style().get("selection_color", (40, 120, 200, 120)),
                (min(x1, x2), y_center, abs(x2-x1), self._font.get_height())
            )

        # text
        if len(self._text) != 0:
            text_surface = self._font.render(
                self._text,
                1,
                super().get_style()["foreground_color"]
            )
            surface.blit(
                text_surface, (5 - text_offset, y_center)
            )

        # caret
        if super().is_focused() and generate_signal(400):
            x = self._get_caret_x()
            y = surface.get_height() * 0.2
            pygame.draw.line(surface, super().get_style()["foreground_color"], (x, y), (x, surface.get_height() - y), 2)

        # outline
        pygame.draw.rect(
            screen, 
            super().get_style()["outline_color"], 
            rect, 
            2, 
            border_radius=corner_radius
        )

    @overrides(GUIElement)
    def process_event(self, view, event):
        super().process_event(view, event)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if super().get_view_rect().collidepoint(event.pos):
                rel_x = event.pos[0]
                new_pos = self._get_char_pos_from_mouse(rel_x)
                self._caret_position = new_pos
                self._selection_anchor = new_pos
                self._mouse_selecting = True
            else:
                self.unselect_text_input()
        elif event.type == pygame.MOUSEBUTTONUP:
            self._mouse_selecting = False
        elif event.type == pygame.MOUSEMOTION:
            if self._mouse_selecting:
                rel_x = event.pos[0]
                new_pos = self._get_char_pos_from_mouse(rel_x)
                self._caret_position = new_pos
        elif event.type == pygame.KEYDOWN:
            if super().is_focused():
                shift = pygame.key.get_mods() & pygame.KMOD_SHIFT
                ctrl = pygame.key.get_mods() & pygame.KMOD_CTRL
                if event.key == pygame.K_RETURN:
                    self.unselect_text_input()
                elif event.key == pygame.K_BACKSPACE:
                    if self._has_selection():
                        self._delete_selection()
                    else:
                        i = self._caret_position
                        if i > 0 and len(self._text) > 0:
                            self._text = self._text[:i-1] + self._text[i:]
                            self._caret_position = max(0, self._caret_position - 1)
                    self._selection_anchor = None
                elif event.key == pygame.K_DELETE:
                    if self._has_selection():
                        self._delete_selection()
                    else:
                        i = self._caret_position
                        if i < len(self._text):
                            self._text = self._text[:i] + self._text[i+1:]
                    self._selection_anchor = None
                elif event.key == pygame.K_LEFT:
                    if shift:
                        if self._selection_anchor is None:
                            self._selection_anchor = self._caret_position
                        if self._caret_position > 0:
                            self._caret_position -= 1
                    else:
                        if self._has_selection():
                            self._caret_position = min(self._caret_position, self._selection_anchor)
                        else:
                            self._caret_position = max(0, self._caret_position - 1)
                        self._selection_anchor = None
                elif event.key == pygame.K_RIGHT:
                    if shift:
                        if self._selection_anchor is None:
                            self._selection_anchor = self._caret_position
                        if self._caret_position < len(self._text):
                            self._caret_position += 1
                    else:
                        if self._has_selection():
                            self._caret_position = max(self._caret_position, self._selection_anchor)
                        else:
                            self._caret_position = min(len(self._text), self._caret_position + 1)
                        self._selection_anchor = None
                elif ctrl and event.key == pygame.K_a:
                    # Select all
                    self._caret_position = len(self._text)
                    self._selection_anchor = 0
                else:
                    if hasattr(event, "unicode") and event.unicode in string.printable and event.unicode != '':
                        if self._has_selection():
                            self._delete_selection()
                        i = self._caret_position
                        self._text = self._text[:i] + event.unicode + self._text[i:]
                        self._caret_position += 1
                        self._selection_anchor = None

    def unselect_text_input(self):
        """
        Handle un focusing the text input, call text changed event, and validate filter if set.
        """
        if self._filter_pattern is not None:
            if not self._filter_pattern.match(self._text):
                # clear text if invalid
                self._text = ""
        self._selection_anchor = None
        super().trigger_event(SUIEvents.EVENT_ON_CHANGE, self._text)