"""
Button UI element for SUILib
"""

import pygame
from ..utils import *
from ..colors import *
from ..guielement import *


class Button(GUIElement):
    """
    Represents a clickable button UI element for SUILib applications.

    The Button displays customizable text, supports style configuration,
    and triggers a callback function when clicked. It handles rendering
    with hover and selection effects, and automatically adjusts its size
    to fit the text content.

    Attributes:
        text (str): The text displayed on the button.
        callbacks (list): List of functions to be called when the button is clicked.
        hover (bool): Indicates whether the button is currently hovered.
        font (pygame.font.Font): Font object used for rendering button text.
    """

    def __init__(self, view, style: dict, text: str, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new Button instance.

        Args:
            view: The parent View instance where this button is placed.
            style (dict): Dictionary containing style attributes for the button.
                See config/styles.json for details.
            text (str): The text to display on the button.
            width (int, optional): Width of the button in pixels. Defaults to 0 (auto).
            height (int, optional): Height of the button in pixels. Defaults to 0 (auto).
            x (int, optional): X coordinate of the button. Defaults to 0.
            y (int, optional): Y coordinate of the button. Defaults to 0.
        """
        super().__init__(view, x, y, width, height, style)
        self.text = text
        self.callbacks = []
        self.hover = False
        self.font = pygame.font.SysFont(
            super().get_style()["font_name"],
            super().get_style()["font_size"],
            bold=super().get_style()["font_bold"]
        )

    def set_text(self, text: str):
        """
        Set the button's display text.

        Args:
            text (str): New text to display on the button.
        """
        self.text = text

    def get_text(self) -> str:
        """
        Get the current text displayed on the button.

        Returns:
            str: The button's display text.
        """
        return self.text

    def add_click_evt(self, callback):
        """
        Set the callback function to be called when the button is clicked.

        Args:
            callback (callable): Function to be invoked on click event.
                The function should accept a single argument: the Button instance.
        """
        self.callbacks.append(callback)

    @overrides(GUIElement)
    def draw(self, view, screen):
        """
        Draw the button on the given screen surface.

        Args:
            view: The parent View instance.
            screen (pygame.Surface): The surface to render the button onto.
        """
        # Draw button background with selection effect
        if self.is_selected():
            c = super().get_style()["background_color"]
            pygame.draw.rect(
                screen,
                color_change(c, -0.2 if c[0] > 128 else 0.6),
                super().get_view_rect(),
                border_radius=10
            )
        else:
            pygame.draw.rect(
                screen,
                super().get_style()["background_color"],
                super().get_view_rect(),
                border_radius=10
            )
        # Draw button text
        if len(self.text) != 0:
            text_surface = self.font.render(
                self.text, True, super().get_style()["foreground_color"]
            )
            # Auto-resize button to fit text if needed
            if text_surface.get_height() + 4 > super().get_height():
                super().set_height(text_surface.get_height() + 4)
            if text_surface.get_width() + 4 > super().get_width():
                super().set_width(text_surface.get_width() + 4)
            screen.blit(
                text_surface,
                (
                    super().get_x() + (super().get_width() - text_surface.get_width()) / 2,
                    super().get_y() + (super().get_height() - text_surface.get_height()) / 2
                )
            )
        # Draw button outline
        pygame.draw.rect(
            screen,
            super().get_style()["outline_color"],
            super().get_view_rect(),
            2,
            border_radius=10
        )

    @overrides(GUIElement)
    def process_event(self, view, event):
        """
        Process a Pygame event related to the button.

        Handles mouse button down and mouse motion events to manage
        selection/hover state and trigger the click callback.

        Args:
            view: The parent View instance.
            event (pygame.event.Event): The Pygame event to process.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if in_rect(event.pos[0], event.pos[1], super().get_view_rect()):
                for callback in self.callbacks:
                    callback(self)
        elif event.type == pygame.MOUSEMOTION:
            if in_rect(event.pos[0], event.pos[1], super().get_view_rect()):
                self.select()
            else:
                self.un_select()

    @overrides(GUIElement)
    def update(self, view):
        """
        Update logic for the button.

        This method is a placeholder for future extensions;
        currently, it does not perform any updates.

        Args:
            view: The parent View instance.
        """
        pass