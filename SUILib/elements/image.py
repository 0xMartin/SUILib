"""
Image UI element for SUILib
"""

import pygame
from ..utils import *
from ..colors import *
from ..guielement import *


class Image(GUIElement):
    """
    Represents an image UI element for SUILib applications.

    The Image element displays a bitmap loaded from a file path, scaled to fit its assigned area.
    It supports dynamic image changes, integrates with the View layout system, and can be used
    for static icons, previews, or general-purpose image display within the UI.

    Attributes:
        image (pygame.Surface): The currently loaded image surface.
    """

    def __init__(self, view, image_path: str, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new Image element.

        Args:
            view: The parent View instance where this image is placed.
            image_path (str): The file path to the image to display.
            width (int, optional): Width of the image area in pixels. Defaults to 0.
            height (int, optional): Height of the image area in pixels. Defaults to 0.
            x (int, optional): X coordinate of the image. Defaults to 0.
            y (int, optional): Y coordinate of the image. Defaults to 0.
        """
        super().__init__(view, x, y, width, height, None)
        self.image = load_image(image_path)

    def set_image(self, image_path: str):
        """
        Set a new image to be displayed.

        Args:
            image_path (str): The file path to the new image.
        """
        self.image = load_image(image_path)

    def get_image(self) -> pygame.Surface:
        """
        Get the currently loaded image surface.

        Returns:
            pygame.Surface: The current image surface, or None if not loaded.
        """
        return self.image

    @overrides(GUIElement)
    def draw(self, view, screen):
        """
        Render the image onto the given Pygame surface, scaled to fit the element's area.

        Args:
            view: The parent View instance.
            screen (pygame.Surface): The surface to render the image onto.
        """
        if self.image is not None:
            screen.blit(
                pygame.transform.scale(self.image, (super().get_width(), super().get_height())),
                (super().get_x(), super().get_y())
            )

    @overrides(GUIElement)
    def process_event(self, view, event):
        """
        Handle Pygame events for the image element.

        Args:
            view: The parent View instance.
            event (pygame.event.Event): The event to process.
        """
        pass

    @overrides(GUIElement)
    def update(self, view):
        """
        Update logic for the image element.

        Args:
            view: The parent View instance.
        """
        pass
