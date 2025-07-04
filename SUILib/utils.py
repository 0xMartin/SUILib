"""
Utility functions for SUILib framework

This module provides miscellaneous utility functions and helpers for the SUILib
multi-view game application framework, including geometry, image loading, config
parsing, async execution, and matplotlib graph rendering for pygame integration.
"""

import pygame
import os.path
import json
import threading
import numpy as np
from time import time
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg
import pylab

def overrides(interface_class):
    """
    Decorator to indicate that a method overrides a method in a superclass.

    Args:
        interface_class (type): The base class to check against.

    Returns:
        function: The decorated method.

    Raises:
        AssertionError: If the method name does not exist in the base class.
    """
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider


def in_rect(x: int, y: int, rect: pygame.Rect) -> bool:
    """
    Check if the point (x, y) is within a given pygame.Rect.

    Args:
        x (int): X coordinate.
        y (int): Y coordinate.
        rect (pygame.Rect): Rectangle to check against.

    Returns:
        bool: True if the point is inside the rectangle, False otherwise.
    """
    if x >= rect.left and y >= rect.top and x <= rect.left + rect.width and y <= rect.top + rect.height:
        return True
    else:
        return False


def generate_signal(ms_periode: int) -> bool:
    """
    Generate a periodic boolean signal: (ms_periode) True -> (ms_periode) False -> ...

    Args:
        ms_periode (int): Half-period of the signal in milliseconds.

    Returns:
        bool: Alternates True/False every ms_periode.
    """
    return round((time() * 1000) / ms_periode) % 2 == 0


def load_image(img_path: str) -> pygame.Surface:
    """
    Load an image from the filesystem as a pygame Surface.

    Args:
        img_path (str): Path to the image file.

    Returns:
        pygame.Surface: Loaded image, or None if file not found.
    """
    if os.path.isfile(img_path):
        return pygame.image.load(img_path)
    else:
        return None

def draw_graph(fig: matplotlib.figure, dark: bool = False):
    """
    Render a matplotlib figure to a pygame Surface.

    Args:
        fig (matplotlib.figure.Figure): The matplotlib figure to render.
        dark (bool): True for dark mode, False for default (light).

    Returns:
        pygame.Surface: The rendered graph as a pygame Surface.
    """
    matplotlib.use("Agg")
    if dark == "dark":
        plt.style.use('dark_background')
    else:
        plt.style.use('default')

    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.buffer_rgba()
    plt.close()

    return pygame.image.frombuffer(raw_data, canvas.get_width_height(), "RGBA")


def load_config(path: str) -> str:
    """
    Load a JSON config file.

    Args:
        path (str): Path to the file.

    Returns:
        dict: Parsed JSON as dictionary, or None if file not found.
    """
    if not os.path.isfile(path):
        return None
    f = open(path)
    data = json.load(f)
    f.close()
    return data


def get_display_width() -> int:
    """
    Get width of the current pygame display surface.

    Returns:
        int: Width in pixels.
    """
    return pygame.display.get_surface().get_size().get_width()

def get_display_height() -> int:
    """
    Get height of the current pygame display surface.

    Returns:
        int: Height in pixels.
    """
    return pygame.display.get_surface().get_size().get_height()

def run_task_async(task):
    """
    Run a function asynchronously in a new thread.

    Args:
        task (function): Function to be run in a separate thread, expected to accept a single argument.
    """
    task = threading.Thread(target=task, args=(1,))
    task.start()