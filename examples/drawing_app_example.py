import pygame
import os
import datetime
from SUILib.utils import inRect
from SUILib.application import Application, View
from SUILib.layout import AbsoluteLayout
from SUILib.stylemanager import StyleManager
from SUILib.utils import overrides
from SUILib.elements import *

VIEW_CANVAS = 1
VIEW_GALLERY = 2

DEFAULT_BRUSH_COLOR = (0, 0, 0)
DEFAULT_BG_COLOR = (255, 255, 255)
DEFAULT_BRUSH_SIZE = 8

class DrawingCanvas(Canvas):
    def __init__(self, parent, style=None, width=600, height=400):
        super().__init__(parent, style)
        super().enableMouseControl()
        self.width = width
        self.height = height
        self.drawing = False
        self.last_pos = None
        self.brush_color = DEFAULT_BRUSH_COLOR
        self.brush_size = DEFAULT_BRUSH_SIZE
        self.eraser = False
        self.history = []
        self.redo_stack = []
        self.clear_canvas()

    def clear_canvas(self):
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.image.fill(DEFAULT_BG_COLOR)
        self.redraw()
        self.history.clear()
        self.redo_stack.clear()

    def redraw(self):
        self.setPaintEvt(self.paint)

    def paint(self, surface, offset):
        surface.blit(self.image, (0, 0))

    def save_state(self):
        self.history.append(self.image.copy())
        if len(self.history) > 50:
            self.history.pop(0)
        self.redo_stack.clear()

    def undo(self):
        if self.history:
            self.redo_stack.append(self.image.copy())
            self.image = self.history.pop()
            self.redraw()

    def redo(self):
        if self.redo_stack:
            self.history.append(self.image.copy())
            self.image = self.redo_stack.pop()
            self.redraw()

    def set_brush_color(self, color):
        self.brush_color = color

    def set_brush_size(self, size):
        self.brush_size = size

    def set_eraser(self, eraser_on):
        self.eraser = eraser_on

    @overrides(Canvas)
    def processEvent(self, view, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if inRect(event.pos[0], event.pos[1], super().getViewRect()):
                self.drawing = True
                self.last_pos = [event.pos[0] - super().getViewRect().topleft[0], event.pos[1] - super().getViewRect().topleft[1]]
                self.save_state()
        elif event.type == pygame.MOUSEMOTION:
            if self.drawing and inRect(event.pos[0], event.pos[1], super().getViewRect()):
                color = DEFAULT_BG_COLOR if self.eraser else self.brush_color
                pygame.draw.line(self.image, color, self.last_pos, [event.pos[0] - super().getViewRect().topleft[0], event.pos[1] - super().getViewRect().topleft[1]], self.brush_size)
                self.last_pos = [event.pos[0] - super().getViewRect().topleft[0], event.pos[1] - super().getViewRect().topleft[1]]
                self.redraw()
        elif event.type == pygame.MOUSEBUTTONUP:
            self.drawing = False
            self.last_pos = None

    # do not decorate with @overrides(View)

class CanvasView(View):
    def __init__(self):
        super().__init__("Drawing Canvas", VIEW_CANVAS)

    @overrides(View)
    def createEvt(self):
        layout = AbsoluteLayout(self)
        self.registerLayoutManager(layout)

        # Drawing area
        self.canvas = DrawingCanvas(self, None, width=600, height=400)
        layout.addElement(self.canvas, ['2%', '15%', '76%', '75%'])

        # Brush color picker
        color_label = Label(self, None, "Brush Color:")
        layout.addElement(color_label, ['80%', '18%'])
        self.colorbox = ComboBox(self, None, ["Black", "Red", "Green", "Blue", "Yellow", "Magenta", "Cyan"])
        layout.addElement(self.colorbox, ['85%', '18%', '10%', '7%'])
        self.colorbox.setValueChangedEvt(self.change_color)

        # Brush size slider
        size_label = Label(self, None, "Brush Size:")
        layout.addElement(size_label, ['80%', '28%'])
        self.size_slider = Slider(self, None, 1, 1, 32)
        self.size_slider.setNumber(DEFAULT_BRUSH_SIZE)
        self.size_slider.setOnValueChanged(self.change_brush_size)
        layout.addElement(self.size_slider, ['85%', '28%', '10%', '7%'])

        # Eraser toggle
        self.eraser_btn = ToggleButton(self, None, "Eraser", False, 80, 30)
        self.eraser_btn.setValueChangedEvt(self.toggle_eraser)
        layout.addElement(self.eraser_btn, ['80%', '38%', '15%', '7%'])

        # Undo/redo
        undo_btn = Button(self, None, "Undo")
        undo_btn.setClickEvt(lambda btn: self.canvas.undo())
        layout.addElement(undo_btn, ['80%', '48%', '7%', '7%'])
        redo_btn = Button(self, None, "Redo")
        redo_btn.setClickEvt(lambda btn: self.canvas.redo())
        layout.addElement(redo_btn, ['88%', '48%', '7%', '7%'])

        # Clear
        clear_btn = Button(self, None, "Clear")
        clear_btn.setClickEvt(lambda btn: self.canvas.clear_canvas())
        layout.addElement(clear_btn, ['80%', '58%', '15%', '7%'])

        # Save
        save_btn = Button(self, None, "Save")
        save_btn.setClickEvt(self.save_canvas)
        layout.addElement(save_btn, ['80%', '68%', '15%', '7%'])

        # Theme switch
        theme_btn = ToggleButton(self, None, "Dark Theme", False, 120, 30)
        theme_btn.setValueChangedEvt(self.set_theme)
        layout.addElement(theme_btn, ['80%', '78%', '15%', '7%'])

        # Gallery switch
        gallery_btn = Button(self, None, "Gallery")
        gallery_btn.setClickEvt(lambda btn: self.getApp().showViewWithID(VIEW_GALLERY))
        layout.addElement(gallery_btn, ['80%', '88%', '15%', '7%'])

        self.addGUIElements([
            self.canvas, self.colorbox, self.size_slider, self.eraser_btn,
            undo_btn, redo_btn, clear_btn, save_btn, theme_btn,
            gallery_btn
        ])

    def change_color(self, value):
        color_map = {
            "Black": (0,0,0), "Red": (255,0,0), "Green": (0,255,0),
            "Blue": (0,0,255), "Yellow": (255,255,0), "Magenta": (255,0,255), "Cyan": (0,255,255)
        }
        self.canvas.set_brush_color(color_map.get(value, (0,0,0)))

    def change_brush_size(self, val):
        self.canvas.set_brush_size(int(val))

    def toggle_eraser(self, state):
        self.canvas.set_eraser(state)

    def save_canvas(self, btn):
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(os.getcwd(), f"drawing_{now}.png")
        pygame.image.save(self.canvas.image, save_path)

    def set_theme(self, dark):
        sm = self.getApp().getStyleManager()
        if dark:
            self.getApp().reloadStyleSheet(StyleManager.DARK_THEME_CONFIG)
        else:
            self.getApp().reloadStyleSheet(StyleManager.LIGHT_THEME_CONFIG)
        self.getApp().reloadElementStyles()

    # handleEvt is NOT declared in View, so do NOT use @overrides(View)
    def handleEvt(self, event):
        # Forward mouse events to the canvas for drawing
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            mx, my = pygame.mouse.get_pos()
            # Adjust if your layout is offset
            rel_pos = (mx - self.canvas.rect.x, my - self.canvas.rect.y)
            self.canvas.handle_event(event, rel_pos)
        # If you have a base handler, call it, otherwise remove the line below
        # super().handleEvt(event)

    @overrides(View)
    def closeEvt(self): pass

    @overrides(View)
    def openEvt(self): pass

    @overrides(View)
    def hideEvt(self): pass

    @overrides(View)
    def reloadStyleEvt(self): pass

class GalleryView(View):
    def __init__(self):
        super().__init__("Gallery", VIEW_GALLERY)

    @overrides(View)
    def createEvt(self):
        layout = AbsoluteLayout(self)
        self.registerLayoutManager(layout)
        label = Label(self, None, "Gallery (images saved in current folder)")
        layout.addElement(label, ['5%', '5%', '90%', '10%'])
        back_btn = Button(self, None, "Back to Canvas")
        back_btn.setClickEvt(lambda btn: self.getApp().showViewWithID(VIEW_CANVAS))
        layout.addElement(back_btn, ['80%', '88%', '15%', '7%'])
        # Optionally, you could display thumbnails of saved images

        self.addGUIElements([label, back_btn])

    @overrides(View)
    def closeEvt(self): pass

    @overrides(View)
    def openEvt(self): pass

    @overrides(View)
    def hideEvt(self): pass

    @overrides(View)
    def reloadStyleEvt(self): pass

def main():
    view1 = CanvasView()
    view2 = GalleryView()
    app = Application([view1, view2], dark=False)
    app.init(800, 500, "SUILib Drawing App", "")
    app.run(view1)

if __name__ == "__main__":
    main()