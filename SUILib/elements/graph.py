"""
Graph UI element for SUILib
"""

import pygame
from ..utils import *
from ..colors import *
from ..guielement import *

class Graph(GUIElement):
    """
    Represents a data visualization widget for displaying various types of graphs (line, bar, pie, scatter, dot) using Matplotlib and Pygame.

    The Graph element renders a matplotlib figure into a Pygame surface, allowing dynamic graph content
    inside SUILib views. The user supplies a figure builder function which draws the graph using matplotlib.

    Attributes:
        graph (pygame.Surface): The rendered graph as a Pygame surface.
        fig_builder (callable): The user-supplied function for building the matplotlib figure.
    """

    def __init__(self, view, style: dict, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new Graph instance.

        Args:
            view: The parent View instance where this graph is placed.
            style (dict): Dictionary describing the style for this graph.
            width (int, optional): Width of the graph in pixels. Defaults to 0.
            height (int, optional): Height of the graph in pixels. Defaults to 0.
            x (int, optional): X coordinate of the graph. Defaults to 0.
            y (int, optional): Y coordinate of the graph. Defaults to 0.
        """
        super().__init__(view, x, y, width, height, style)
        self.graph = None
        self.fig_builder = None

    def set_figure_builder_func(self, func):
        """
        Set the function responsible for building the matplotlib figure.

        Args:
            func (callable): Builder function with signature `def builder(fig): ...`
                - The function receives a matplotlib.figure.Figure instance and
                  should draw the desired graph on it.
        """
        self.fig_builder = func

    @overrides(GUIElement)
    def set_width(self, width):
        """
        Set the width of the graph and refresh the rendered figure.

        Args:
            width (int): New width in pixels.
        """
        super().set_width(width)
        self.refresh_graph()

    @overrides(GUIElement)
    def set_height(self, height):
        """
        Set the height of the graph and refresh the rendered figure.

        Args:
            height (int): New height in pixels.
        """
        super().set_height(height)
        self.refresh_graph()

    def refresh_graph(self):
        """
        Redraw and re-render the matplotlib figure to the Pygame surface.
        Called automatically when the size of the graph changes or the builder function is set.
        """
        if self.fig_builder is not None and super().get_width() > 50 and super().get_height() > 50:
            fig = pylab.figure(
                figsize=[self.get_width()/100, self.get_height()/100], dpi=100)
            fig.patch.set_alpha(0.0)
            self.fig_builder(fig)
            self.graph = draw_graph(
                fig,
                super().get_style()["theme"]
            )

    @overrides(GUIElement)
    def draw(self, view, screen):
        """
        Render the graph onto the given Pygame surface.

        Args:
            view: The parent View instance.
            screen (pygame.Surface): The surface to render the graph onto.
        """
        if self.graph is not None:
            screen.blit(
                pygame.transform.scale(self.graph, (super().get_width(), super().get_height())),
                (super().get_x(), super().get_y())
            )

    @overrides(GUIElement)
    def process_event(self, view, event):
        """
        Handle Pygame events for the graph.

        Args:
            view: The parent View instance.
            event (pygame.event.Event): The event to process.
        """
        pass

    @overrides(GUIElement)
    def update(self, view):
        """
        Update logic for the graph.

        Args:
            view: The parent View instance.
        """
        pass

    @staticmethod
    def builderFunc_lineGraph(fig, x_label, y_label, values, legend=None):
        """
        Builder function for Graph: Plot line graph.

        Args:
            fig: The matplotlib Figure object to plot on.
            x_label (str): Label for X axis.
            y_label (str): Label for Y axis.
            values (list): List of lists, each representing Y values of a line.
            legend (list, optional): List of legend strings.

        Example:
            Graph.builderFunc_lineGraph(
                f,
                "X axis",
                "Y axis",
                [[1, 2, 3, 4], [2, 4, 10, 8], [3, 7, 17, 12]],
                ['A', 'B', 'C']
            )
        """
        ax = fig.gca()
        for i, line in enumerate(values):
            line_plot, = ax.plot(line)
            if legend and i < len(legend):
                line_plot.set_label(legend[i])
                ax.legend()
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

    @staticmethod
    def builderFunc_pieGraph(fig, labels, values, explode=None):
        """
        Builder function for Graph: Plot pie graph.

        Args:
            fig: The matplotlib Figure object to plot on.
            labels (list): Labels for the pie sections.
            values (list): Values for each section.
            explode (list, optional): Offsets for each section.

        Example:
            Graph.builderFunc_pieGraph(
                f,
                ['A', 'B', 'C', 'D'],
                [1, 2, 3, 5],
                (0, 0.2, 0, 0)
            )
        """
        ax = fig.gca()
        ax.pie(values, explode=explode, labels=labels, autopct='%1.1f%%',
               shadow=True, startangle=90)
        ax.axis('equal')

    @staticmethod
    def builderFunc_dotGraph(fig, x_label, y_label, values, legend=None):
        """
        Builder function for Graph: Dot graph.

        Args:
            fig: The matplotlib Figure object to plot on.
            x_label (str): Label for X axis.
            y_label (str): Label for Y axis.
            values (list): List of lists, each representing Y values of a line.
            legend (list, optional): List of legend strings.

        Example:
            Graph.builderFunc_dotGraph(
                f,
                "X axis",
                "Y axis",
                [[1, 2, 3, 4], [2, 4, 10, 8], [3, 7, 17, 12]],
                ['A', 'B', 'C']
            )
        """
        ax = fig.gca()
        for i, line in enumerate(values):
            line_plot, = ax.plot(line, '.')
            if legend and i < len(legend):
                line_plot.set_label(legend[i])
                ax.legend()
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

    @staticmethod
    def builderFunc_barGraph(fig, labels, values):
        """
        Builder function for Graph: Bar graph.

        Args:
            fig: The matplotlib Figure object to plot on.
            labels (list): Labels for bars.
            values (list): Values for each bar.

        Example:
            Graph.builderFunc_barGraph(
                f,
                ['A', 'B', 'C', 'D'],
                [2, 4, 10, 8]
            )
        """
        ax = fig.gca()
        ax.bar(labels, values, width=1, edgecolor="white", linewidth=0.7)

    @staticmethod
    def builderFunc_scatterGraph(fig, values, xlim, ylim):
        """
        Builder function for Graph: Scatter graph.

        Args:
            fig: The matplotlib Figure object to plot on.
            values (list): List of (x, y) tuples for each point.
            xlim (tuple): (min, max) for x axis.
            ylim (tuple): (min, max) for y axis.

        Example:
            Graph.builderFunc_scatterGraph(
                f,
                [(1, 2), (4, 5), (4, 7), (6, 1), (4, 3)],
                (0, 8),
                (0, 8)
            )
        """
        ax = fig.gca()
        x = [pt[0] for pt in values]
        y = [pt[1] for pt in values]
        sizes = np.random.uniform(15, 80, len(x))
        colors = np.random.uniform(15, 80, len(x))
        ax.scatter(x, y, s=sizes, c=colors, vmin=0, vmax=100)
        ax.set(xlim=xlim, ylim=ylim)