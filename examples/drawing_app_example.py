import pygame
import os
import datetime
from SUILib.utils import in_rect
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
        super().enable_mouse_control()
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
        self.set_paint_evt(self.paint)

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
    def process_event(self, view, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if in_rect(event.pos[0], event.pos[1], super().get_view_rect()):
                self.drawing = True
                self.last_pos = [event.pos[0] - super().get_view_rect().topleft[0], event.pos[1] - super().get_view_rect().topleft[1]]
                self.save_state()
        elif event.type == pygame.MOUSEMOTION:
            if self.drawing and in_rect(event.pos[0], event.pos[1], super().get_view_rect()):
                color = DEFAULT_BG_COLOR if self.eraser else self.brush_color
                pygame.draw.line(self.image, color, self.last_pos, [event.pos[0] - super().get_view_rect().topleft[0], event.pos[1] - super().get_view_rect().topleft[1]], self.brush_size)
                self.last_pos = [event.pos[0] - super().get_view_rect().topleft[0], event.pos[1] - super().get_view_rect().topleft[1]]
                self.redraw()
        elif event.type == pygame.MOUSEBUTTONUP:
            self.drawing = False
            self.last_pos = None

    # do not decorate with @overrides(View)

class CanvasView(View):
    def __init__(self):
        super().__init__("Drawing Canvas", VIEW_CANVAS)

    @overrides(View)
    def create_evt(self):
        layout = AbsoluteLayout(self)
        self.register_layout_manager(layout)

        # Drawing area
        self.canvas = DrawingCanvas(self, None, width=600, height=400)
        layout.add_element(self.canvas, ['2%', '15%', '76%', '75%'])

        # Brush color picker
        color_label = Label(self, None, "Brush Color:")
        layout.add_element(color_label, ['80%', '18%'])
        self.colorbox = ComboBox(self, None, ["Black", "Red", "Green", "Blue", "Yellow", "Magenta", "Cyan"])
        layout.add_element(self.colorbox, ['85%', '18%', '10%', '7%'])
        self.colorbox.set_value_changed_evt(self.change_color)

        # Brush size slider
        size_label = Label(self, None, "Brush Size:")
        layout.add_element(size_label, ['80%', '28%'])
        self.size_slider = Slider(self, None, 1, 1, 32)
        self.size_slider.set_number(DEFAULT_BRUSH_SIZE)
        self.size_slider.set_on_value_changed(self.change_brush_size)
        layout.add_element(self.size_slider, ['85%', '28%', '10%', '7%'])

        # Eraser toggle
        self.eraser_btn = ToggleButton(self, None, "Eraser", False, 80, 30)
        self.eraser_btn.set_value_changed_evt(self.toggle_eraser)
        layout.add_element(self.eraser_btn, ['80%', '38%', '15%', '7%'])

        # Undo/redo
        undo_btn = Button(self, None, "Undo")
        undo_btn.add_click_evt(lambda btn: self.canvas.undo())
        layout.add_element(undo_btn, ['80%', '48%', '7%', '7%'])
        redo_btn = Button(self, None, "Redo")
        redo_btn.add_click_evt(lambda btn: self.canvas.redo())
        layout.add_element(redo_btn, ['88%', '48%', '7%', '7%'])

        # Clear
        clear_btn = Button(self, None, "Clear")
        clear_btn.add_click_evt(lambda btn: self.canvas.clear_canvas())
        layout.add_element(clear_btn, ['80%', '58%', '15%', '7%'])

        # Save
        save_btn = Button(self, None, "Save")
        save_btn.add_click_evt(self.save_canvas)
        layout.add_element(save_btn, ['80%', '68%', '15%', '7%'])

        # Theme switch
        theme_btn = ToggleButton(self, None, "Dark Theme", False, 120, 30)
        theme_btn.set_value_changed_evt(self.set_theme)
        layout.add_element(theme_btn, ['80%', '78%', '15%', '7%'])

        # Gallery switch
        gallery_btn = Button(self, None, "Gallery")
        gallery_btn.add_click_evt(lambda btn: self.get_app().show_view_with_id(VIEW_GALLERY))
        layout.add_element(gallery_btn, ['80%', '88%', '15%', '7%'])

        self.add_gui_elements([
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
        sm = self.get_app().get_style_manager()
        if dark:
            self.get_app().reload_style_sheet(StyleManager.DARK_THEME_CONFIG)
        else:
            self.get_app().reload_style_sheet(StyleManager.LIGHT_THEME_CONFIG)
        self.get_app().reload_element_styles()

    # handle_evt is NOT declared in View, so do NOT use @overrides(View)
    def handle_evt(self, event):
        # Forward mouse events to the canvas for drawing
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            mx, my = pygame.mouse.get_pos()
            # Adjust if your layout is offset
            rel_pos = (mx - self.canvas.rect.x, my - self.canvas.rect.y)
            self.canvas.handle_event(event, rel_pos)
        # If you have a base handler, call it, otherwise remove the line below
        # super().handle_evt(event)

    @overrides(View)
    def close_evt(self): pass

    @overrides(View)
    def open_evt(self): pass

    @overrides(View)
    def hide_evt(self): pass

    @overrides(View)
    def reload_style_evt(self): pass

class GalleryView(View):
    def __init__(self):
        super().__init__("Gallery", VIEW_GALLERY)

    @overrides(View)
    def create_evt(self):
        layout = AbsoluteLayout(self)
        self.register_layout_manager(layout)
        label = Label(self, None, "Gallery (images saved in current folder)")
        layout.add_element(label, ['5%', '5%', '90%', '10%'])
        back_btn = Button(self, None, "Back to Canvas")
        back_btn.add_click_evt(lambda btn: self.get_app().show_view_with_id(VIEW_CANVAS))
        layout.add_element(back_btn, ['80%', '88%', '15%', '7%'])
        # Optionally, you could display thumbnails of saved images

        self.add_gui_elements([label, back_btn])

    @overrides(View)
    def close_evt(self): pass

    @overrides(View)
    def open_evt(self): pass

    @overrides(View)
    def hide_evt(self): pass

    @overrides(View)
    def reload_style_evt(self): pass

def main():
    view1 = CanvasView()
    view2 = GalleryView()
    app = Application([view1, view2], dark=False)
    app.init(800, 500, "SUILib Drawing App", "")
    app.run(view1)

if __name__ == "__main__":
    main()