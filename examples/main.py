import random
import pygame

from SUILib import Application, View, AbsoluteLayout, RelativeLayout, StyleManager, overrides
from SUILib.elements import *

VIEW1_ID = 1
VIEW2_ID = 2

custom_btn_style = {
    "outline_color": (235, 100, 100),
    "foreground_color": (255, 255, 255),
    "background_color": (255, 120, 120),
    "font_name": "Verdena",
    "font_size": 32,
    "font_bold": False
}


class View1(View):
    def __init__(self):
        super().__init__("View 1", VIEW1_ID)

    @overrides(View)
    def createEvt(self):
        al = AbsoluteLayout(self)
        # label
        label = Label(self, None, "VIEW 1", True)
        al.addElement(label, ['50%', '5%'])

        # toggle button
        tb = ToggleButton(self, None, "Theme", False, 40, 20)
        tb.setValueChangedEvt(self.changeTheme)
        al.addElement(tb, ['5%', '5%'])

        # canvas
        canvas = Canvas(self, None)
        al.addElement(canvas, ['3%', '15%', '45%', '40%'])
        canvas.setPaintEvt(self.paint)

        # table
        data = {
            "header": ["Col 1", "Col 2", "Col 3", "Col 4"],
            "body": [
                ["A1", "B1", "C1", "D1"],
                ["A2", "B2", "C2", "D2"],
                ["A3", "B3", "C3", "D3"],
                ["A4", "B4", "C4", "D4"],
                ["A1", "B1", "C1", "D1"],
                ["A2", "B2", "C2", "D2"],
                ["A3", "B3", "C3", "D3"],
                ["A4", "B4", "C4", "D4"],
                ["A1", "B1", "C1", "D1"],
                ["A2", "B2", "C2", "D2"],
                ["A3", "B3", "C3", "D3"],
                ["A4", "B4", "C4", "D4"]
            ]
        }
        table = Table(self, None, data)
        al.addElement(table, ['52%', '15%', '45%', '40%'])

        # btn
        btn = Button(self, custom_btn_style, "Go to view 2")
        al.addElement(btn, ['25%', '60%', '50%', '40'])
        btn.setClickEvt(lambda btn: self.app.showViewWithID(VIEW2_ID))

        # checkbox
        rl = RelativeLayout(self, True)
        checkbox1 = CheckBox(self, None, "Check box 1", True, 20)
        al.addElement(checkbox1, ['10%', '75%'])
        rl.addElement(checkbox1, "parent")
        checkbox2 = CheckBox(self, None, "Check box 2", True, 20)
        rl.addElement(checkbox2, "child")
        checkbox3 = CheckBox(self, None, "Check box 3", True, 20)
        rl.addElement(checkbox3, "child")

        # slider
        slider = Slider(self, None, 40, 10, 50)
        slider.setNumber(33.33)
        slider.setLabelFormat("@ (#%)")
        al.addElement(slider, ['25%', '85%', '50%', '15'])

        self.addGUIElements(
            [btn, canvas, table, label, tb, checkbox1, checkbox2, checkbox3, slider])

    @overrides(View)
    def closeEvt(self):
        pass

    @overrides(View)
    def openEvt(self):
        pass

    @overrides(View)
    def hideEvt(self):
        pass

    @overrides(View)
    def reloadStyleEvt(self):
        pass

    def paint(self, surface, offset):
        for i in range(1, 25):
            pygame.draw.rect(
                surface,
                (random.randint(0, 255), random.randint(
                    0, 255), random.randint(0, 255)),
                pygame.Rect(
                    random.randint(-50, surface.get_width() - 50),
                    random.randint(-50, surface.get_height() - 50),
                    random.randint(40, 100),
                    random.randint(40, 100)
                ),
                2
            )

    def changeTheme(self, dark):
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
        # panel for tab 1
        panel1 = Panel(self, None)
        panel1.setLayoutManager(AbsoluteLayout(self))
        # combo box
        group = RadioButtonGroup([])
        combobox1 = RadioButton(self, None, "Option 1", group, 20)
        panel1.addElement(combobox1, ['15%', '5%'])
        combobox2 = RadioButton(self, None, "Option 2", group, 20)
        panel1.addElement(combobox2, ['40%', '5%'])
        combobox3 = RadioButton(self, None, "Option 3", group, 20)
        panel1.addElement(combobox3, ['65%', '5%'])
        # image
        img = Image(self, "test_img_1.jpg")
        panel1.addElement(img, ['5%', '20%', '45%', '75%'])
        # graph
        graph = Graph(self, None)
        graph.setFigureBuilderFunc(lambda f: Graph.builderFunc_pieGraph(
            f,
            ['A', 'B', 'C', 'D'],
            [1, 2, 3, 5],
            (0, 0.2, 0, 0)
        ))
        panel1.addElement(graph, ['50%', '8%', '45%', '90%'])

        # panel for tab 2
        panel2 = Panel(self, None)
        panel2.setLayoutManager(AbsoluteLayout(self))
        # button
        btn = Button(self, None, "Go to view 1")
        panel2.addElement(btn, ['25%', '85%', '50%', '40'])
        btn.setClickEvt(lambda btn: self.getApp().showViewWithID(VIEW1_ID))
        # text input
        txt = TextInput(self, None, "A1B2")
        txt.setFilterPattern("^([A-Z][0-9]+)+$")
        panel2.addElement(txt, ['25%', '5%', '50%', '40'])

        # tab panel
        tab = TabPanel(
            self,
            None,
            [
                Tab("Tab 1", panel1),
                Tab("Tab 2", panel2),
                Tab("Empty Tab", None)
            ]
        )
        al = AbsoluteLayout(self)
        al.addElement(tab, ['5%', '5%', '90%', '90%'])

        self.addGUIElements([tab])

    @overrides(View)
    def closeEvt(self):
        pass

    @overrides(View)
    def openEvt(self):
        pass

    @overrides(View)
    def hideEvt(self):
        pass

    @overrides(View)
    def reloadStyleEvt(self):
        pass


def main():
    view1 = View1()
    view2 = View2()
    app = Application([view1, view2], False)
    app.init(640, 400, "Application", "")
    app.run(view1)


if __name__ == "__main__":
    main()
