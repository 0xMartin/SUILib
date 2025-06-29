"""
This module defines standard events for GUI elements in a Pygame UI library.
These events can be used to handle user interactions with GUI elements such as buttons, labels, etc.
"""

EVENT_ON_CLICK = "on_click"
"""str: Event triggered when the element is clicked by the user."""

EVENT_ON_DOUBLE_CLICK = "on_double_click"
"""str: Event triggered when the element is double-clicked."""

EVENT_ON_RIGHT_CLICK = "on_right_click"
"""str: Event triggered when the element is right-clicked."""

EVENT_ON_MOUSE_DOWN = "on_mouse_down"
"""str: Event triggered when a mouse button is pressed down on the element."""

EVENT_ON_MOUSE_UP = "on_mouse_up"
"""str: Event triggered when a mouse button is released on the element."""

EVENT_ON_MOUSE_ENTER = "on_mouse_enter"
"""str: Event triggered when the mouse pointer enters the element's area."""

EVENT_ON_MOUSE_LEAVE = "on_mouse_leave"
"""str: Event triggered when the mouse pointer leaves the element's area."""

EVENT_ON_MOUSE_MOVE = "on_mouse_move"
"""str: Event triggered when the mouse pointer moves over the element."""

EVENT_ON_KEY_DOWN = "on_key_down"
"""str: Event triggered when a keyboard key is pressed while the element is focused."""

EVENT_ON_KEY_UP = "on_key_up"
"""str: Event triggered when a keyboard key is released while the element is focused."""

EVENT_ON_FOCUS = "on_focus"
"""str: Event triggered when the element receives focus."""

EVENT_ON_BLUR = "on_blur"
"""str: Event triggered when the element loses focus."""

EVENT_ON_CHANGE = "on_change"
"""str: Event triggered when the element's value changes."""

EVENT_ON_HOVER = "on_hover"
"""str: Event triggered when the mouse hovers over the element."""

STANDARD_EVENTS = [
    EVENT_ON_CLICK,
    EVENT_ON_DOUBLE_CLICK,
    EVENT_ON_RIGHT_CLICK,
    EVENT_ON_MOUSE_DOWN,
    EVENT_ON_MOUSE_UP,
    EVENT_ON_MOUSE_ENTER,
    EVENT_ON_MOUSE_LEAVE,
    EVENT_ON_MOUSE_MOVE,
    EVENT_ON_KEY_DOWN,
    EVENT_ON_KEY_UP,
    EVENT_ON_FOCUS,
    EVENT_ON_BLUR,
    EVENT_ON_CHANGE,
    EVENT_ON_HOVER
]
"""list[str]: All standard event names supported by GUI elements."""