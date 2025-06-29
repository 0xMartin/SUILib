"""
Canvas UI element for SUILib
"""

import pygame
from ..utils import *
from ..colors import *
from ..guielement import *


class Canvas(GUIElement):
    """
    Represents a drawable canvas UI element for custom rendering and mouse-interactive content.

    The Canvas provides an area within the UI where custom graphics can be drawn, either
    statically or dynamically. It supports mouse interaction for controlling the drawing
    offset (useful for panning or other transformations), and allows the user to define a
    paint callback for custom content rendering.

    Attributes:
        callback (callable): Paint callback function for custom drawing.
        control (bool): Whether mouse control (panning) is enabled.
        mouse_sensitivity (float): Adjusts the responsiveness of mouse movement.
        offset (list): Current drawing offset [x, y].
        font (pygame.font.Font): Font used for any text rendering inside the canvas.
    """

    def __init__(self, view, style: dict, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new Canvas instance.

        Args:
            view: The parent View instance where this canvas is placed.
            style (dict): Dictionary containing style attributes for the canvas.
                See config/styles.json for details.
            width (int, optional): Width of the canvas in pixels. Defaults to 0.
            height (int, optional): Height of the canvas in pixels. Defaults to 0.
            x (int, optional): X coordinate of the canvas. Defaults to 0.
            y (int, optional): Y coordinate of the canvas. Defaults to 0.
        """
        super().__init__(view, x, y, width, height, style, pygame.SYSTEM_CURSOR_SIZEALL)
        self.callback = None
        self.control = False
        self.mouse_sensitivity = 2.0
        self.offset = [0, 0]
        self.font = pygame.font.SysFont(
            super().get_style()["font_name"],
            super().get_style()["font_size"],
            bold=super().get_style()["font_bold"]
        )

    def enable_mouse_control(self):
        """
        Enable mouse control for the canvas.

        When enabled, mouse drag events within the canvas area can be used to modify
        the drawing offset (e.g., for panning or rotating the content).
        """
        self.control = True

    def disable_mouse_control(self):
        """
        Disable mouse control for the canvas.

        When disabled, mouse events will not affect the drawing offset or transformations.
        """
        self.control = False

    def set_mouse_sensitivity(self, mouse_sensitivity: float):
        """
        Set the sensitivity for mouse-based canvas control.

        Args:
            mouse_sensitivity (float): Multiplier for how much the offset changes per pixel moved.
        """
        self.mouse_sensitivity = mouse_sensitivity

    def get_mouse_sensitivity(self) -> float:
        """
        Get the current mouse sensitivity value.

        Returns:
            float: The mouse sensitivity multiplier.
        """
        return self.mouse_sensitivity

    def set_offset(self, offset: list):
        """
        Set the drawing offset for the canvas.

        Args:
            offset (list): List of two values [x, y] representing the offset.
        """
        self.offset = offset

    def get_offset(self) -> list:
        """
        Get the current drawing offset.

        Returns:
            list: The current offset [x, y].
        """
        return self.offset

    def set_paint_evt(self, callback):
        """
        Set the paint event callback for the canvas.

        The callback should be a function accepting (surface, offset) and will be called
        whenever the canvas needs to be redrawn.

        Args:
            callback (callable): Function to be called for custom drawing.
        """
        self.callback = callback

    @overrides(GUIElement)
    def draw(self, view, screen):
        """
        Render the canvas and call the user-provided paint callback.

        Args:
            view: The parent View instance.
            screen (pygame.Surface): The surface to render the canvas onto.
        """
        # Draw canvas background
        pygame.draw.rect(screen, super().get_style()["background_color"], super().get_view_rect())

        # Create a subsurface for drawing
        surface = screen.subsurface(
            pygame.Rect(
                super().get_x(),
                super().get_y(),
                min(max(super().get_width(), 10), screen.get_width() - super().get_x()),
                min(max(super().get_height(), 10), screen.get_height() - super().get_y())
            )
        )
        # Call the paint callback if set
        if self.callback is not None:
            self.callback(surface, self.offset)

        # Draw canvas outline
        pygame.draw.rect(screen, super().get_style()["outline_color"], super().get_view_rect(), 2)

    @overrides(GUIElement)
    def process_event(self, view, event):
        """
        Process Pygame events for mouse-based canvas interaction.

        Args:
            view: The parent View instance.
            event (pygame.event.Event): The Pygame event to process.
        """
        if self.control:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if in_rect(event.pos[0], event.pos[1], super().get_view_rect()):
                    super().select()
                    self.mouse_motion = True
            elif event.type == pygame.MOUSEBUTTONUP:
                super().un_select()
            elif event.type == pygame.MOUSEMOTION:
                if in_rect(event.pos[0], event.pos[1], super().get_view_rect()):
                    if self.is_selected():
                        if self.mouse_motion:
                            self.last_pos = event.pos
                        else:
                            self.offset[0] += (event.pos[0] - self.last_pos[0]) * self.mouse_sensitivity
                            self.offset[1] += (event.pos[1] - self.last_pos[1]) * self.mouse_sensitivity
                        self.mouse_motion = not self.mouse_motion

    @overrides(GUIElement)
    def update(self, view):
        """
        Update logic for the canvas.

        This method is a placeholder for future extensions;
        currently, it does not perform any updates.

        Args:
            view: The parent View instance.
        """
        pass