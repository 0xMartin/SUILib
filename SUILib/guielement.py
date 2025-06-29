"""
Base classes for GUI elements in SUILib

This module defines the core abstract base classes for GUI elements and containers
used in the SUILib framework. It provides the foundational interface and functionality
for all graphical elements (buttons, panels, sliders, etc.) in a multi-view
pygame-based application.
"""

import pygame
from typing import Callable, Dict, List, Optional
import abc
import inspect
from .events import SUIEvents

class GUIElement(metaclass=abc.ABCMeta):
    """
    Abstract base class for all GUI elements in SUILib.

    Provides position, size, style, visibility, selection state, and required
    abstract interface for rendering, event processing, and updates.

    Attributes:
        view: Reference to parent View.
        x (int): X position.
        y (int): Y position.
        width (int): Width of the element.
        height (int): Height of the element.
        style (dict): Style dictionary.
        focused_cursor: Pygame cursor type shown when this element is focused.
        visible (bool): Visibility of the element.
        focused (bool): Whether the element is currently focused.
        hovered (bool): Whether the element is currently hovered.
        rect (pygame.Rect): Rectangle representing the element's position and size.
    """

    def __init__(
        self,
        view,
        x: int,
        y: int,
        width: int,
        height: int,
        style: dict,
        focused_cursor=pygame.SYSTEM_CURSOR_HAND
    ):
        """
        Initialize a new GUIElement.

        Args:
            view: Parent View where the element is placed.
            x (int): X position.
            y (int): Y position.
            width (int): Width in pixels.
            height (int): Height in pixels.
            style (dict): Style dictionary. If None, will be resolved by class name.
            selected_cursor: Pygame cursor type to show when element is selected.
        """
        self.view = view
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.focused_cursor = focused_cursor

        # Default action variables
        self.hovered = False
        self.visible = True
        self.focused = False

        sm = view.get_app().get_style_manager()
        if style is None:
            self.style = sm.get_style_with_name(self.__class__.__name__)
            if not self.style:
                for base in inspect.getmro(self.__class__)[1:]:
                    if base is object:
                        continue
                    style = sm.get_style_with_name(base.__name__)
                    if style:
                        self.style = style
                        break
        else:
            self.style = style

        self.update_view_rect()
        # register of all event callbacks
        # Initialize with empty lists for each standard event
        self._event_callbacks: Dict[str, List[Callable]] = {evt: [] for evt in SUIEvents.STANDARD_EVENTS}

    def set_visibility(self, visible: bool):
        """
        Set visibility of this element.

        Args:
            visible (bool): True to make element visible, False to hide.
        """
        self.visible = visible

    def is_visible(self) -> bool:
        """
        Check visibility of this element.

        Returns:
            bool: True if visible, False otherwise.
        """
        return self.visible
    
    def is_hovered(self) -> bool:
        """
        Check if this element is currently hovered by the mouse.

        Returns:
            bool: True if hovered, False otherwise.
        """
        return self.hovered

    def set_focused_cursor(self, cursor):
        """
        Set the cursor type to use when this element is focused.

        Args:
            cursor: Pygame cursor type constant.
        """
        self.focused_cursor = cursor

    def get_focused_cursor(self):
        """
        Get the cursor type to use when this element is focused.

        Returns:
            int: Pygame cursor type constant.
        """
        return self.focused_cursor

    def get_view(self):
        """
        Get reference to the parent View.

        Returns:
            View: The parent view object.
        """
        return self.view

    def get_x(self) -> int:
        """Get X position of this element."""
        return self.x

    def get_y(self) -> int:
        """Get Y position of this element."""
        return self.y

    def get_width(self) -> int:
        """Get width of this element."""
        return self.width

    def get_height(self) -> int:
        """Get height of this element."""
        return self.height

    def get_style(self) -> dict:
        """Get style dictionary of this element."""
        return self.style

    def set_x(self, x: int):
        """
        Set the X position of this element.

        Args:
            x (int): New X position.
        """
        self.x = x
        self.update_view_rect()

    def set_y(self, y: int):
        """
        Set the Y position of this element.

        Args:
            y (int): New Y position.
        """
        self.y = y
        self.update_view_rect()

    def set_width(self, width: int):
        """
        Set the width of this element.

        Args:
            width (int): New width in pixels.
        """
        if width >= 0:
            self.width = width
            self.update_view_rect()

    def set_height(self, height: int):
        """
        Set the height of this element.

        Args:
            height (int): New height in pixels.
        """
        if height >= 0:
            self.height = height
            self.update_view_rect()

    def set_style(self, style: dict):
        """
        Set the style dictionary for this element.

        Args:
            style (dict): New style.
        """
        self.style = style

    def update_view_rect(self):
        """
        Update the pygame.Rect representing this element's area.
        """
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def get_view_rect(self) -> pygame.Rect:
        """
        Get the pygame.Rect representing the element's area.

        Returns:
            pygame.Rect: The rectangle for drawing and hit-testing.
        """
        return self.rect

    def focus(self):
        """Mark this element as focused."""
        self.focused = True

    def un_focus(self):
        """Mark this element as unfocused."""
        self.focused = False

    def is_focused(self) -> bool:
        """
        Check if this element is currently focused.

        Returns:
            bool: True if focused, False otherwise.
        """
        return self.focused

    def draw(self, view, screen: pygame.Surface):
        """
        Draw the element on the pygame surface.

        Args:
            view: The parent View calling the draw method.
            screen (pygame.Surface): The surface to draw on.
        """
        pass

    def process_event(self, view, event):
        """
        Process a pygame event sent from the parent view.

        Args:
            view: The parent View sending the event.
            event: The pygame event object.
        """
        if not self.visible:
            return

        # Aktuální pozice myši
        mouse_pos = pygame.mouse.get_pos()

        # MOUSE ENTER/LEAVE (detekce při každém eventu)
        if self.get_view_rect().collidepoint(mouse_pos):
            if not self.hovered:
                self.hovered = True
                self.trigger_event(SUIEvents.EVENT_ON_MOUSE_ENTER, event)
        else:
            if self.hovered:
                self.hovered = False
                self.trigger_event(SUIEvents.EVENT_ON_MOUSE_LEAVE, event)

        # Zpracování podle typu eventu
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.get_view_rect().collidepoint(event.pos):
                self.trigger_event(SUIEvents.EVENT_ON_MOUSE_DOWN, event)
                if event.button == 1:
                    self.trigger_event(SUIEvents.EVENT_ON_CLICK, event)
                    if not self.focused:
                        self.focused = True
                        self.trigger_event(SUIEvents.EVENT_ON_FOCUS, event)
                elif event.button == 3:
                    self.trigger_event(SUIEvents.EVENT_ON_RIGHT_CLICK, event)
            else:
                if self.focused:
                    self.focused = False
                    self.trigger_event(SUIEvents.EVENT_ON_BLUR, event)
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.get_view_rect().collidepoint(event.pos):
                self.trigger_event(SUIEvents.EVENT_ON_MOUSE_UP, event)
        elif event.type == pygame.MOUSEMOTION:
            if self.get_view_rect().collidepoint(event.pos):
                self.trigger_event(SUIEvents.EVENT_ON_MOUSE_MOVE, event)
        elif event.type == pygame.KEYDOWN:
            self.trigger_event(SUIEvents.EVENT_ON_KEY_DOWN, event)
        elif event.type == pygame.KEYUP:
            self.trigger_event(SUIEvents.EVENT_ON_KEY_UP, event)

    def update(self, view):
        """
        Update the element's state.

        Args:
            view: The parent View updating this element.
        """
        pass

    def add_event_callback(self, event_name: str, callback: Callable):
        """
        Add a callback for a specific event.
        
        Args:
            event_name (str): Name of the event to listen for. Check events module for supported events.
            callback (Callable): Function to call when the event is triggered.
            
        Raises:
            ValueError: If the event name is not supported.
        """
        if event_name not in self._event_callbacks:
            raise ValueError(f"Unsupported event: {event_name}")
        self._event_callbacks[event_name].append(callback)

    def remove_event_callback(self, event_name: str, callback: Callable):
        """
        Remove a callback for a specific event.

        Args:
            event_name (str): Name of the event.
            callback (Callable): Callback function to remove.
        
        Raises:
            ValueError: If the event name is not supported or callback not found.
        """
        if event_name in self._event_callbacks and callback in self._event_callbacks[event_name]:
            self._event_callbacks[event_name].remove(callback)

    def clear_event_callbacks(self, event_name: Optional[str] = None):
        """
        Remove all callbacks for a specific event or all events.

        Args:
            event_name (Optional[str]): Name of the event to clear callbacks for.
                If None, clears all callbacks for all events.
        """
        if event_name:
            if event_name in self._event_callbacks:
                self._event_callbacks[event_name] = []
        else:
            for evt in self._event_callbacks:
                self._event_callbacks[evt] = []

    def trigger_event(self, event_name: str, *args, **kwargs):
        """Spustí všechny callbacky pro daný event."""
        for callback in self._event_callbacks.get(event_name, []):
            callback(*args, **kwargs)


class Container(metaclass=abc.ABCMeta):
    """
    Abstract base class for a container of GUI elements.

    Any class inheriting from Container must implement get_childs().

    Methods:
        get_childs(): Returns a list of child GUI elements.
    """

    @abc.abstractmethod
    def get_childs(self) -> list:
        """
        Get child GUI elements of the container.

        Returns:
            list: List of contained child elements.
        """
        pass