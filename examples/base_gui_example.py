import random
import pygame
import os

from SUILib.application import Application, View
from SUILib.events import SUIEvents
from SUILib.layout import AbsoluteLayout, HBoxLayout
from SUILib.stylemanager import StyleManager
from SUILib.utils import overrides, run_task_async
from SUILib.elements import *

VIEW1_ID = 1
VIEW2_ID = 2

# Custom button style for demonstration
CUSTOM_BTN_STYLE = {
    "outline_color": (235, 100, 100),
    "foreground_color": (255, 255, 255),
    "background_color": (255, 120, 120),
    "font_name": "Verdana",
    "font_size": 32,
    "font_bold": True
}


class View1(View):
    def __init__(self):
        super().__init__("View 1", VIEW1_ID)

    @overrides(View)
    def create_evt(self):
        layout = AbsoluteLayout(self)

        # Header label
        label = Label(self, None, "VIEW 1", True)
        label.set_anchor("50%", 0)
        layout.add_element(label, ['50%', '5%'])

        # Theme toggle button
        theme_toggle = ToggleButton(self, None, "Theme", False, 40, 20)
        theme_toggle.add_event_callback(SUIEvents.EVENT_ON_CHANGE, self.change_theme)
        layout.add_element(theme_toggle, ['5%', '5%'])

        # Canvas with random rectangles
        canvas = Canvas(self, None)
        layout.add_element(canvas, ['3%', '15%', '45%', '40%'])
        canvas.add_paint_evt(self.paint)

        # Data for table
        table_data = {
            "header": ["Col 1", "Col 2", "Col 3", "Col 4"],
            "body": [
                ["A1", "B1", "C1", "D1"],
                ["A2", "B2", "C2", "D2"],
                ["A3", "B3", "C3", "D3"],
                ["A4", "B4", "C4", "D4"],
            ] * 10  # Repeat rows for demonstration
        }
        table = Table(self, None, table_data)
        layout.add_element(table, ['52%', '15%', '45%', '40%'])

        # Navigation button
        nav_btn = Button(self, CUSTOM_BTN_STYLE, "Go to view 2")
        nav_btn.add_event_callback(SUIEvents.EVENT_ON_CLICK,
                                   lambda btn: self.get_app().show_view_with_id(VIEW2_ID))
        layout.add_element(nav_btn, ['25%', '60%', '50%', '40'])

        # Checkboxes using HBoxLayout
        rel_layout = HBoxLayout(self)
        checkbox1 = CheckBox(self, None, "Check box 1", True, 20)
        rel_layout.add_element(checkbox1, "parent")
        layout.add_element(checkbox1, ['10%', '75%'])
        checkbox2 = CheckBox(self, None, "Check box 2", True, 20)
        rel_layout.add_element(checkbox2, "child")
        checkbox3 = CheckBox(self, None, "Check box 3", True, 20)
        rel_layout.add_element(checkbox3, "child")

        # Slider
        slider = Slider(self, None, 40, 10, 50)
        slider.set_number(33.33)
        slider.set_label_format("@ (#%)")
        layout.add_element(slider, ['25%', '85%', '50%', '15'])

        self.add_gui_elements([
            label, theme_toggle, canvas, table, nav_btn,
            checkbox1, checkbox2, checkbox3, slider
        ])

    @overrides(View)
    def close_evt(self): pass

    @overrides(View)
    def open_evt(self): pass

    @overrides(View)
    def hide_evt(self): pass

    @overrides(View)
    def reload_style_evt(self): pass

    def paint(self, surface, offset):
        # Paints random rectangles for demonstration
        for _ in range(24):
            color = tuple(random.randint(0, 255) for _ in range(3))
            rect = pygame.Rect(
                random.randint(-50, surface.get_width() - 50),
                random.randint(-50, surface.get_height() - 50),
                random.randint(40, 100),
                random.randint(40, 100)
            )
            pygame.draw.rect(surface, color, rect, 2)

    def change_theme(self, dark):
        sm = self.get_app().get_style_manager()
        if dark:
            self.get_app().reload_style_sheet(StyleManager.DARK_THEME_CONFIG)
        else:
            self.get_app().reload_style_sheet(StyleManager.LIGHT_THEME_CONFIG)
        self.get_app().reload_element_styles()


class View2(View):
    def __init__(self):
        super().__init__("View 2", VIEW2_ID)

    @overrides(View)
    def create_evt(self):
        # Tab 1 Panel
        panel1 = Panel(self, None)
        panel1.set_layout_manager(AbsoluteLayout(self))
        group = RadioButtonGroup([])

        rb1 = RadioButton(self, None, "Option 1", group, 20)
        rb2 = RadioButton(self, None, "Option 2", group, 20)
        rb3 = RadioButton(self, None, "Option 3", group, 20)
        panel1.add_element(rb1, ['15%', '5%'])
        panel1.add_element(rb2, ['40%', '5%'])
        panel1.add_element(rb3, ['65%', '5%'])

        module_path = os.path.dirname(os.path.abspath(__file__))
        image = Image(self, os.path.join(module_path, "./test_img_1.jpg"))
        panel1.add_element(image, ['5%', '20%', '45%', '75%'])

        graph = Graph(self, None)
        graph.set_figure_builder_func(lambda f: Graph.builder_func_pie_graph(
            f, ['A', 'B', 'C', 'D'], [1, 2, 3, 5], (0, 0.2, 0, 0)
        ))
        panel1.add_element(graph, ['50%', '8%', '45%', '90%'])

        # --------------------------------------------------------------------
        # Tab 2 Panel
        panel2 = Panel(self, None)
        panel2.set_layout_manager(AbsoluteLayout(self))
        btn = Button(self, None, "Go to view 1")
        btn.add_event_callback(SUIEvents.EVENT_ON_CLICK, 
                               lambda btn: self.get_app().show_view_with_id(VIEW1_ID))
        panel2.add_element(btn, ['25%', '85%', '50%', '40'])

        txt = TextInput(self, None, "A1B2")
        txt.set_filter_pattern(r"^([A-Z][0-9]+)+$")
        panel2.add_element(txt, ['25%', '5%', '50%', '40'])

        box = ComboBox(self, None, ["Option 1", "Option 2", "Option 3", "Option 4", "Option 5", "Option 6"])
        panel2.add_element(box, ['25%', '25%', '50%', '40'])

        # --------------------------------------------------------------------
        # Tab 3 Panel
        panel3 = Panel(self, None)
        panel3.set_layout_manager(AbsoluteLayout(self))

        self.progress_bar = ProgressBar(self, None, 0, 0, 100)
        self.progress_bar.set_label_format("@ (#%)")
        self.progress_bar.set_anchor("50%", "50%")
        panel3.add_element(self.progress_bar, ['50%', '50%', '50%', '10%'])

        # --------------------------------------------------------------------
        # Tab panel
        tab_panel = TabPanel(self, None, [
            Tab("Tab 1", panel1),
            Tab("Tab 2", panel2),
            Tab("Tab 3", panel3),
            Tab("Empty tab", None)  
        ])

        layout = AbsoluteLayout(self)
        layout.add_element(tab_panel, ['5%', '5%', '90%', '90%'])
        self.add_gui_elements([tab_panel])

    @overrides(View)
    def close_evt(self): pass

    @overrides(View)
    def open_evt(self):
        run_task_async(self.progress_bar_animation)

    @overrides(View)
    def hide_evt(self): pass

    @overrides(View)
    def reload_style_evt(self): pass

    def progress_bar_animation(self, stop_event):
        value = self.progress_bar.get_min()
        for _ in range(self.progress_bar.get_max() + 1):
            if stop_event.is_set():
                break
            self.progress_bar.set_value(value)
            value += 1
            if self.progress_bar.is_visible():
                self.request_repaint()
            pygame.time.delay(50)
        self.request_repaint()
        print("Progress bar animation finished.")


def main():
    # Initialize views and run the application
    view1 = View1()
    view2 = View2()
    app = Application([view1, view2], dark=False)
    app.init_application(640, 400, "SUILib Example", "")
    app.run_application(view1)


if __name__ == "__main__":
    main()