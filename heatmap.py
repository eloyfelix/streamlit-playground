from bokeh.io import output_file, show
from bokeh.models import LinearColorMapper, BasicTicker, ColorBar, HoverTool
from bokeh.plotting import figure
from bokeh.transform import transform
from bokeh.models import ColumnDataSource
import scipy.cluster.hierarchy as sch
import numpy as np


def generate_heatmap(data, x_labels, y_labels):
    # Create a color mapper
    color_mapper = LinearColorMapper(
        palette="Viridis256", low=np.min(data), high=np.max(data)
    )

    # Set up the plot
    p = figure(
        title="Target predictions heatmap",
        # plot_width=1200,
        # plot_height=600,
        x_range=[0, data.shape[1]],
        y_range=[0, data.shape[0]],
        x_axis_label="Targets",
        y_axis_label="Compounds",
    )

    # Create the heatmap
    source = ColumnDataSource(
        data=dict(x=[], y=[], color=[], value=[], xcoord=[], ycoord=[])
    )
    rects = p.rect(
        x="x",
        y="y",
        width=1,
        height=1,
        source=source,
        line_color=None,
        fill_color=transform("color", color_mapper),
    )

    # Add hover tooltip
    hover_tool = HoverTool(
        renderers=[rects],
        tooltips=[("Target", "@xcoord"), ("Compound", "@ycoord"), ("Prediction", "@value")],
        mode="mouse",
    )
    p.add_tools(hover_tool)

    # Add color bar
    color_bar = ColorBar(
        color_mapper=color_mapper,
        ticker=BasicTicker(desired_num_ticks=10),
        label_standoff=12,
        border_line_color=None,
        location=(0, 0),
    )
    p.add_layout(color_bar, "right")

    # Generate data coordinates and values
    x_coords, y_coords = np.meshgrid(
        range(data.shape[1]), range(data.shape[0])
    )

    source.data = dict(
        x=x_coords.flatten(),
        y=y_coords.flatten(),
        color=data.flatten(),
        value=data.flatten(),
        xcoord=x_labels * data.shape[0],
        ycoord=np.repeat(y_labels, data.shape[1]),
    )

    # Add string legends to x and y axes
    p.xaxis.ticker = BasicTicker(desired_num_ticks=10, base=0)
    p.xaxis.major_label_overrides = dict(zip(range(len(x_labels)), x_labels))
    p.xaxis.major_label_orientation = np.pi / 4  # Rotate by 45 degrees
    p.yaxis.ticker = BasicTicker(desired_num_ticks=10, base=0)
    p.yaxis.major_label_overrides = dict(zip(range(len(y_labels)), y_labels))

    return p
