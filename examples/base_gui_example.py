import random
import pygame
import os

from SUILib.application import Application, View
from SUILib.layout import AbsoluteLayout, RelativeLayout
from SUILib.stylemanager import StyleManager
from SUILib.utils import overrides
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
    def createEvt(self):
        layout = AbsoluteLayout(self)

        # Header label
        label = Label(self, None, "VIEW 1", True)
        layout.addElement(label, ['50%', '5%'])

        # Theme toggle button
        theme_toggle = ToggleButton(self, None, "Theme", False, 40, 20)
        theme_toggle.setValueChangedEvt(self.changeTheme)
        layout.addElement(theme_toggle, ['5%', '5%'])

        # Canvas with random rectangles
        canvas = Canvas(self, None)
        layout.addElement(canvas, ['3%', '15%', '45%', '40%'])
        canvas.setPaintEvt(self.paint)

        # Data for table
        table_data = {
            "header": ["Col 1", "Col 2", "Col 3", "Col 4"],
            "body": [
                ["A1", "B1", "C1", "D1"],
                ["A2", "B2", "C2", "D2"],
                ["A3", "B3", "C3", "D3"],
                ["A4", "B4", "C4", "D4"],
            ] * 3  # Repeat rows for demonstration
        }
        table = Table(self, None, table_data)
        layout.addElement(table, ['52%', '15%', '45%', '40%'])

        # Navigation button
        nav_btn = Button(self, CUSTOM_BTN_STYLE, "Go to view 2")
        nav_btn.setClickEvt(lambda btn: self.app.showViewWithID(VIEW2_ID))
        layout.addElement(nav_btn, ['25%', '60%', '50%', '40'])

        # Checkboxes using RelativeLayout
        rel_layout = RelativeLayout(self, True)
        checkbox1 = CheckBox(self, None, "Check box 1", True, 20)
        rel_layout.addElement(checkbox1, "parent")
        layout.addElement(checkbox1, ['10%', '75%'])
        checkbox2 = CheckBox(self, None, "Check box 2", True, 20)
        rel_layout.addElement(checkbox2, "child")
        checkbox3 = CheckBox(self, None, "Check box 3", True, 20)
        rel_layout.addElement(checkbox3, "child")

        # Slider
        slider = Slider(self, None, 40, 10, 50)
        slider.setNumber(33.33)
        slider.setLabelFormat("@ (#%)")
        layout.addElement(slider, ['25%', '85%', '50%', '15'])

        self.addGUIElements([
            label, theme_toggle, canvas, table, nav_btn,
            checkbox1, checkbox2, checkbox3, slider
        ])

    @overrides(View)
    def closeEvt(self): pass

    @overrides(View)
    def openEvt(self): pass

    @overrides(View)
    def hideEvt(self): pass

    @overrides(View)
    def reloadStyleEvt(self): pass

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

    def changeTheme(self, dark):
        sm = self.getApp().getStyleManager()
        if dark:
            self.getApp().reloadStyleSheet(StyleManager.DARK_THEME_CONFIG)
        else:
            self.getApp().reloadStyleSheet(StyleManager.LIGHT_THEME_CONFIG)
        self.getApp().reloadElementStyles()


class View2(View):
    def __init__(self):
        super().__init__("View 2", VIEW2_ID)

    @overrides(View)
    def createEvt(self):
        # Tab 1 Panel
        panel1 = Panel(self, None)
        panel1.setLayoutManager(AbsoluteLayout(self))
        group = RadioButtonGroup([])

        rb1 = RadioButton(self, None, "Option 1", group, 20)
        rb2 = RadioButton(self, None, "Option 2", group, 20)
        rb3 = RadioButton(self, None, "Option 3", group, 20)
        panel1.addElement(rb1, ['15%', '5%'])
        panel1.addElement(rb2, ['40%', '5%'])
        panel1.addElement(rb3, ['65%', '5%'])

        module_path = os.path.dirname(os.path.abspath(__file__))
        image = Image(self, os.path.join(module_path, "./test_img_1.jpg"))
        panel1.addElement(image, ['5%', '20%', '45%', '75%'])

        graph = Graph(self, None)
        graph.setFigureBuilderFunc(lambda f: Graph.builderFunc_pieGraph(
            f, ['A', 'B', 'C', 'D'], [1, 2, 3, 5], (0, 0.2, 0, 0)
        ))
        panel1.addElement(graph, ['50%', '8%', '45%', '90%'])

        # Tab 2 Panel
        panel2 = Panel(self, None)
        panel2.setLayoutManager(AbsoluteLayout(self))
        btn = Button(self, None, "Go to view 1")
        btn.setClickEvt(lambda btn: self.getApp().showViewWithID(VIEW1_ID))
        panel2.addElement(btn, ['25%', '85%', '50%', '40'])

        txt = TextInput(self, None, "A1B2")
        txt.setFilterPattern(r"^([A-Z][0-9]+)+$")
        panel2.addElement(txt, ['25%', '5%', '50%', '40'])

        # Tab panel
        tab_panel = TabPanel(self, None, [
            Tab("Tab 1", panel1),
            Tab("Tab 2", panel2),
            Tab("Empty Tab", None)
        ])

        layout = AbsoluteLayout(self)
        layout.addElement(tab_panel, ['5%', '5%', '90%', '90%'])
        self.addGUIElements([tab_panel])

    @overrides(View)
    def closeEvt(self): pass

    @overrides(View)
    def openEvt(self): pass

    @overrides(View)
    def hideEvt(self): pass

    @overrides(View)
    def reloadStyleEvt(self): pass


def main():
    # Initialize views and run the application
    view1 = View1()
    view2 = View2()
    app = Application([view1, view2], dark=False)
    app.init(640, 400, "SUILib Example", "")
    app.run(view1)


if __name__ == "__main__":
    main()