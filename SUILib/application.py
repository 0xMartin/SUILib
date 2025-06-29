"""
Main application and view management for SUILib

This module provides the core Application and View classes for the SUILib
framework, supporting multiple switchable views, style management, event loop,
window handling, and scheduling of repaint and rendering logic.

Classes:
    Application: Main class managing the application window, views, rendering, and events.
    View: Abstract base class for a content page shown in the application window.
    Layout: Abstract base class for layout managers that arrange GUI elements in a view.
"""

import pygame
import abc
from typing import final
import os

from .colors import *
from .utils import *
from .guielement import GUIElement, Container
from .stylemanager import StyleManager

# Event konstanty
REPAINT_EVENT = pygame.USEREVENT + 1

class Application:
    """
    Main SUILib application class managing views, window, styles and event loop.

    Attributes:
        views (list): List of View objects managed by the application.
        visible_view (View): Currently visible View.
        inited (bool): True if the application window is initialized.
        running (bool): True if the event loop is running.
        stylemanager (StyleManager): Style manager instance.
        fill_color (tuple): Default background color for views.
        draw_queue (list): Queue for deferred draw callbacks.
    """

    def __init__(self, views, dark=False):
        """
        Initialize the application and load styles/themes.

        Args:
            views (list): List of View objects to register.
            dark (bool): True for dark theme, False for light theme.
        """
        self._periodic_repaint_enabled = False  
        self._periodic_repaint_fps = 60  
        self._needs_repaint = True 
        self.views = []
        self.draw_queue = []
        self.visible_view = None
        self.inited = False
        self.running = False
        module_path = os.path.dirname(os.path.abspath(__file__))
        if dark:
            self.stylemanager = StyleManager(
                os.path.join(module_path, StyleManager.DARK_THEME_CONFIG))
        else:
            self.stylemanager = StyleManager(
                os.path.join(module_path, StyleManager.LIGHT_THEME_CONFIG))
        self.set_fill_color(WHITE)
        for v in views:
            if isinstance(v, View):
                v.set_application(self)
                self.views.append(v)

    def set_fill_color(self, color: tuple):
        """
        Set default fill color for views in the application.

        Args:
            color (tuple): RGB color tuple.
        """
        self.fill_color = color

    def add_view(self, view) -> bool:
        """
        Add a new view to the application.

        Args:
            view (View): The view to add.

        Returns:
            bool: True on success, False if not a valid View.
        """
        if(isinstance(view, View)):
            view.set_application(self)
            self.views.append(view)
            # call create event (only if app is running)
            if self.inited:
                view.createEvt_base(self.screen.get_width(),
                                    self.screen.get_height())
            return True
        else:
            return False

    def get_style_manager(self) -> StyleManager:
        """
        Get the application's style manager.

        Returns:
            StyleManager: The style manager instance.
        """
        return self.stylemanager

    def reload_style_sheet(self, styles_path: str):
        """
        Reload stylesheet from a file.

        Args:
            styles_path (str): Path to the stylesheet JSON file.
        """
        self.stylemanager.load_style_sheet(styles_path)

    def reload_element_styles(self):
        """
        Reload styles of all GUI elements in all views.
        """
        fill_color = self.stylemanager.get_style_with_name("default")[
            "fill_color"]
        for view in self.views:
            view.set_fill_color(fill_color)
            view.reload_element_style()

    def remove_view(self, view) -> bool:
        """
        Remove a view from the application.

        Args:
            view (View): The view to remove.

        Returns:
            bool: True on success, False if not a valid View.
        """
        if(isinstance(view, View)):
            self.views.remove(view)
            return True
        else:
            return False

    def get_screen(self) -> pygame.Surface:
        """
        Get the pygame Surface representing the application window.

        Returns:
            pygame.Surface: The application window surface.
        """
        return self.screen

    def init(self, width: int, height: int, name: str, icon: str):
        """
        Initialize the application window and resources.

        Args:
            width (int): Window width in pixels.
            height (int): Window height in pixels.
            name (str): Window/application title.
            icon (str): Path to window icon image.
        """
        self.width = max(width, 50)
        self.height = max(height, 50)
        self.name = name
        self.icon = icon

        self.stylemanager.init()

        pygame.init()
        self.default_font = pygame.font.SysFont("Verdana", 35, bold=True)
        pygame.display.set_caption(name)
        img = load_image(self.icon)
        if img is None:
            module_path = os.path.dirname(os.path.abspath(__file__))
            img = load_image(os.path.join(module_path, "./assets/icon.png"))
        if img is not None:
            pygame.display.set_icon(img)
        self.screen = pygame.display.set_mode(
            (width, height), 
            pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.SRCALPHA | pygame.RESIZABLE, 
            vsync=1)
        self.inited = True

    def run(self, start_view=None) -> bool:
        """
        Start the main event loop and rendering.

        Args:
            start_view (View, optional): View to show first.

        Returns:
            bool: True if the loop exited normally, False if not initialized.
        """
        if not self.inited:
            return False

        self.running = True

        # call start event for each view
        for view in self.views:
            view.createEvt_base(self.screen.get_width(), self.screen.get_height())

        if start_view is not None:
            self.show_view(start_view)

        # Enable periodic repaint if requested
        if self._periodic_repaint_enabled:
            pygame.time.set_timer(REPAINT_EVENT, int(1000 / self._periodic_repaint_fps))

        while self.running:
            event = pygame.event.wait()

            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == REPAINT_EVENT:
                self._needs_repaint = True
            else:
                if self.visible_view is not None:
                    self.visible_view.process_evt(event)
                    self.visible_view.update()
                self._needs_repaint = True  # repaint after every event

            if self._needs_repaint and self.visible_view is not None:
                if self.visible_view.get_fill_color() is None:
                    self.screen.fill(self.fill_color)
                else:
                    self.screen.fill(self.visible_view.get_fill_color())
                self.visible_view.render(self.screen)
                pygame.display.flip()
                self._needs_repaint = False  # repaint done

        pygame.quit()
        return True
    
    def request_repaint(self):
        """
        Request an immediate repaint of the active view.
        """
        self._needs_repaint = True
        if self.visible_view is not None:
            if self.visible_view.get_fill_color() is None:
                self.screen.fill(self.fill_color)
            else:
                self.screen.fill(self.visible_view.get_fill_color())
            self.visible_view.render(self.screen)
            pygame.display.flip()
            self._needs_repaint = False

    def enable_periodic_repaint(self, fps=60):
        """
        Enable periodic repaint at a given FPS.

        Args:
            fps (int): Frames per second for forced repaint.
        """
        self._periodic_repaint_enabled = True
        self._periodic_repaint_fps = fps
        pygame.time.set_timer(REPAINT_EVENT, int(1000 / fps))

    def disable_periodic_repaint(self):
        """
        Disable periodic repaint. Repaint will only happen on user/event/request.
        """
        self._periodic_repaint_enabled = False
        pygame.time.set_timer(REPAINT_EVENT, 0)

    def close(self):
        """
        Close the application and clean up views.

        Side Effects:
            Calls close_evt on all views and clears the views list.
        """
        self.running = False
        for view in self.views:
            view.close_evt()
        self.views = []

    def show_view(self, view) -> bool:
        """
        Display a specific view in the application.

        Args:
            view (View): The view to display.

        Returns:
            bool: True on success, False otherwise.
        """
        if not self.running:
            return False

        if view in self.views:
            # hide current visible view
            if self.visible_view is not None:
                self.visible_view.set_visibility(False)
                self.visible_view.hide_evt()
            # show new view
            view.set_visibility(True)
            view.openEvt_base(self.screen.get_width(),
                              self.screen.get_height())
            self.visible_view = view
            # change window title
            if len(view.name) == 0:
                pygame.display.set_caption(self.name)
            else:
                pygame.display.set_caption(self.name + " - " + view.name)
            return True
        else:
            return False

    def show_view_with_name(self, name: str) -> bool:
        """
        Show a view with a specific name.

        Args:
            name (str): Name of the view.

        Returns:
            bool: True on success, False otherwise.
        """
        for view in self.views:
            if view.name == name:
                return self.show_view(view)

    def show_view_with_id(self, id: int) -> bool:
        """
        Show a view by its unique ID.

        Args:
            id (int): ID of the view.

        Returns:
            bool: True on success, False otherwise.
        """
        for view in self.views:
            if view.ID == id:
                return self.show_view(view)

    def draw_later(self, z_index, draw_callback):
        """
        Add a draw callback to the queue for deferred drawing.

        Args:
            z_index (int): Z-INDEX; higher values will be drawn above lower ones.
            draw_callback (callable): Function to call for drawing (signature: draw(self, view, screen)).
        """
        self.draw_queue.append({"Z-INDEX": z_index, "CALLBACK": draw_callback})

# **************************************************************************************************************
# Base View 
# **************************************************************************************************************

class View(metaclass=abc.ABCMeta):
    """
    Abstract base class representing a single page or content view in the application window.

    The View class defines the interface and core logic for all views in the SUILib framework. 
    A view is a logical page or screen which the user can see and interact with; only one view 
    is visible at a time. Each view manages its own GUI elements, layouts, appearance, and event 
    handling, and can be shown, hidden, or updated by the Application.

    Attributes:
        name (str): Human-readable name of the view (may appear in the window title).
        ID (int): Unique identifier for navigation or referencing views.
        visible (bool): Whether the view is currently visible.
        fill_color (tuple): Background fill color for the view (RGB).
        filter (dict or None): If set, restricts event processing to a specific GUI element.
        GUIElements (list): List of GUIElement objects contained in this view.
        layout_manager_list (list): List of registered layout managers for this view.
        cursor: The default system cursor for this view.
        app (Application): Reference to the parent Application (set via set_application()).
    """

    def __init__(self, name: str, id: int):
        """
        Initialize a new view instance.

        Args:
            name (str): Name of the view (used in window title).
            id (int): Unique ID for the view (for navigation).
        """
        self.name = name
        self.ID = id
        self.visible = False
        self.fill_color = None
        self.filter = None
        self.GUIElements = []
        self.layout_manager_list = []
        self.set_default_cursor()

    def set_id(self, id: int):
        """
        Set the unique ID of the view.

        Args:
            id (int): New ID for the view.
        """
        self.ID = id

    def add_gui_elements(self, elements):
        """
        Add one or more GUI elements to this view.

        Args:
            elements (list): List of GUIElement instances to add.
        """
        for el in elements:
            if isinstance(el, GUIElement):
                self.GUIElements.append(el)

    def remove_gui_element(self, element):
        """
        Remove a GUI element from this view.

        Args:
            element (GUIElement): The GUI element to remove.
        """
        self.GUIElements.remove(element)

    def request_repaint(self):
        """
        Request a repaint of this view (only if it is currently visible/active).
        Triggers the repaint mechanism in the parent application.
        """
        if hasattr(self, "app") and self.app is not None and self.app.visible_view == self:
            self.app._needs_repaint = True
            self.app.request_repaint()

    @final
    def get_app(self):
        """
        Get the parent application instance.

        Returns:
            Application: Reference to the parent Application.
        """
        return self.app

    def register_layout_manager(self, layout_manager) -> bool:
        """
        Register a layout manager with this view.

        Args:
            layout_manager (Layout): The layout manager to add.

        Returns:
            bool: True if successfully registered, False otherwise.
        """
        if isinstance(layout_manager, Layout):
            self.layout_manager_list.append(layout_manager)
            return True
        else:
            return False

    def unregister_layout_manager(self, layout_manager):
        """
        Unregister a layout manager from this view.

        Args:
            layout_manager (Layout): The layout manager to remove.
        """
        self.layout_manager_list.remove(layout_manager)

    @final
    def get_gui_elements(self) -> list:
        """
        Get a list of all GUI elements in this view.

        Returns:
            list: List of GUIElement instances.
        """
        return self.GUIElements

    def set_default_cursor(self, cursor=pygame.SYSTEM_CURSOR_ARROW):
        """
        Set the default cursor for this view.

        Args:
            cursor: Pygame system cursor constant.
        """
        self.cursor = cursor

    def set_fill_color(self, color: tuple):
        """
        Set the background fill color for this view.

        Args:
            color (tuple): An RGB color tuple.
        """
        self.fill_color = color

    @final
    def get_fill_color(self) -> tuple:
        """
        Get the current fill color of this view.

        Returns:
            tuple: RGB color tuple or None if not set.
        """
        return self.fill_color

    def set_visibility(self, visible: bool):
        """
        Set this view's visibility.

        Args:
            visible (bool): True to show, False to hide.
        """
        self.visible = visible

    def set_application(self, app: Application):
        """
        Assign this view to a parent application.

        Args:
            app (Application): The parent Application instance.

        Returns:
            bool: True if set successfully, False otherwise.
        """
        if(isinstance(app, Application)):
            self.app = app
            return True
        else:
            return False

    def set_filter_process_only(self, element):
        """
        Restrict event processing to a single GUI element.

        Args:
            element (GUIElement): The GUI element to process exclusively.
        """
        if element is not None:
            self.filter = {"type": "process_only", "element": element}

    def clear_filter(self):
        """
        Clear the event processing filter, so all elements will process events.
        """
        self.filter = None

    @final
    def reload_element_style(self, list=None):
        """
        Reload the style for all GUI elements in the view.

        Args:
            list (list, optional): List of GUI elements to reload. If None, reloads all.
        """
        if list is None:
            list = self.GUIElements
        for el in list:
            if el is None:
                continue
            style = self.app.get_style_manager().get_style_with_name(el.__class__.__name__)
            if style is not None:
                el.set_style(style)
            if isinstance(el, Container):
                self.reload_element_style(el.get_childs())
        self.reload_style_evt()

    @final
    def createEvt_base(self, width: int, height: int):
        """
        Internal: Called when application starts or view is added, and updates layout.

        Args:
            width (int): Width of the view window.
            height (int): Height of the view window.
        """
        self.create_evt()
        if self.fill_color is None:
            self.fill_color = self.get_app().get_style_manager(
            ).get_style_with_name("default")["fill_color"]
        for lm in self.layout_manager_list:
            lm.update_layout(width, height)

    @abc.abstractmethod
    def create_evt(self):
        """
        Abstract: Called when the application starts or the view is created.
        Implement view-specific initialization logic here.
        """
        pass

    @abc.abstractmethod
    def close_evt(self):
        """
        Abstract: Called when the application closes.
        Implement view-specific cleanup logic here.
        """
        pass

    @final
    def openEvt_base(self, width: int, height: int):
        """
        Internal: Called when this view becomes visible, updates layout, and unselects all elements.

        Args:
            width (int): Width of the view window.
            height (int): Height of the view window.
        """
        for lm in self.layout_manager_list:
            lm.update_layout(width, height)
        for el in self.GUIElements:
            el.un_focus()
        self.open_evt()

    @abc.abstractmethod
    def open_evt(self):
        """
        Abstract: Called when this view is shown (becomes active).
        Implement logic to run when a view is activated.
        """
        pass

    @abc.abstractmethod
    def hide_evt(self):
        """
        Abstract: Called when this view is hidden (becomes inactive).
        Implement logic to run when a view is deactivated.
        """
        pass

    @abc.abstractmethod
    def reload_style_evt(self):
        """
        Abstract: Called when styles are reloaded for this view.
        Implement logic for style updates.
        """
        pass

    @final
    def process_evt(self, event):
        """
        Process a single event from the application and dispatch to GUI elements.

        Args:
            event: A pygame event object.
        """
        if self.app is not None:
            if self.filter is None:
                for el in self.GUIElements:
                    el.process_event(self, event)
            else:
                self.filter["element"].process_event(self, event)
        selected = self.find_element(
            self.GUIElements, lambda el: el.is_focused())
        if selected is not None:
            pygame.mouse.set_cursor(selected.get_focus_cursor())
        else:
            pygame.mouse.set_cursor(self.cursor)

    def find_element(self, list, procces_function=None):
        """
        Find the first element in a list of GUI elements for which a process function returns True.

        Args:
            list (list): List of GUIElement (or Container) objects.
            procces_function (callable): Function accepting a GUIElement and returning bool.

        Returns:
            GUIElement or None: The first matching element, or None if not found.
        """
        if procces_function is None or list is None:
            return None
        ret = None
        for el in list:
            if isinstance(el, Container):
                ret_container = self.find_element(
                    el.get_childs(), procces_function)
                if ret_container is not None:
                    ret = ret_container
                    break
            else:
                if procces_function(el):
                    ret = el
                    break
        return ret

    def render(self, screen: pygame.Surface):
        """
        Render the view's GUI elements to the given surface.

        Args:
            screen (pygame.Surface): Pygame surface to draw on.
        """
        if self.app is not None:
            for el in self.GUIElements:
                if el.is_visible():
                    el.draw(self, screen)

    def update(self):
        """
        Update all visible GUI elements in this view.
        """
        if self.app is not None:
            for el in self.GUIElements:
                if el.is_visible():
                    el.update(self)

# **************************************************************************************************************
# base layout manager class
# **************************************************************************************************************

class Layout(metaclass=abc.ABCMeta):
    """
    Abstract base class for layout managers in SUILib.

    The Layout class manages a list of layout elements, each consisting of a reference to a GUI element 
    and its properties relevant to the specific layout manager. 
    Layout elements are stored as dictionaries: {"element": ..., "propt": ...}.

    Subclasses should implement the update_layout() method to arrange elements according to their own rules.

    Attributes:
        view (View): The associated View instance for this layout manager.
        layout_elements (list): List of layout elements managed by this layout manager.
    """

    def __init__(self, view: View, register: bool = True):
        """
        Initialize the base layout class and optionally register it with the view.

        Args:
            view (View): The View instance this layout manager is associated with.
            register (bool): If True (default), automatically register with the view.
        """
        if isinstance(view, View):
            self.view = view
        self.layout_elements = []
        # register
        if register:
            view.register_layout_manager(self)

    @final
    def get_layout_elements(self) -> list:
        """
        Get the list of layout elements managed by this layout manager.

        Returns:
            list: List of layout element dictionaries.
        """
        return self.layout_elements

    def set_elements(self, layout_elements):
        """
        Replace the current list of layout elements.

        Args:
            layout_elements (list): New list of layout elements.
        """
        self.layout_elements = layout_elements

    def add_element(self, element: GUIElement, propt: bool = None):
        """
        Add a new layout element to this layout manager.

        Args:
            element (GUIElement): The GUI element to add.
            propt (any, optional): Property of element for this manager (e.g., position, alignment).
        """
        if isinstance(element, GUIElement):
            self.layout_elements.append({"element": element, "propt": propt})

    @abc.abstractmethod
    def update_layout(self, width: int, height: int):
        """
        Abstract method to arrange all GUI elements managed by this layout.

        Args:
            width (int): Width of the view or screen.
            height (int): Height of the view or screen.
        """
        pass

    @final
    def get_view(self):
        """
        Get the View instance associated with this layout manager.

        Returns:
            View: The associated view.
        """
        return self.view