import numpy as np
import streamlit as st
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool
import pandas as pd


@st.cache_data
def fetch_data():
    df = pd.read_csv("docs.csv")
    df = df[["np_likeness_score", "journal"]]
    return df


st.title("Distribution of natural product likeness score by Journals")

st.markdown(
    """ Dataset extracted using the following SQL query:

```sql
select
	distinct cr.molregno,
	cp.np_likeness_score ,
	docs.journal
from
	docs
join compound_records cr on
	docs.doc_id = cr.doc_id
join compound_properties cp on
	cr.molregno = cp.molregno
where
	cr.src_id = 1
	and docs.journal is not null
	and cp.np_likeness_score is not null;
```
"""
)

num_journals = 20

df = fetch_data()

# get the journal names sorted by np_likeness_score median value
agg = df.groupby("journal")["np_likeness_score"].median().sort_values(ascending=False)
all_journals = list(agg.keys())

top_n = all_journals[0:num_journals]

options = st.multiselect(
    "Select desired Journals (showing by default top 10 journals by mean np_likeness_score)",
    all_journals,
    top_n,
)
all_options = st.checkbox(
    "Select all options (overrides the multiselect, to be seen in full screen)"
)

if all_options:
    options = all_journals

grouped = df[df["journal"].isin(options)].groupby("journal")
journals = options


# find the quartiles and IQR for each category
q1 = grouped.quantile(q=0.25)
q2 = grouped.quantile(q=0.5)
q3 = grouped.quantile(q=0.75)
iqr = q3 - q1
upper = q3 + 1.5 * iqr
lower = q1 - 1.5 * iqr


# find the outliers for each journal
def outliers(group):
    journal = group.name
    return group[
        (group.np_likeness_score > upper.loc[journal]["np_likeness_score"])
        | (group.np_likeness_score < lower.loc[journal]["np_likeness_score"])
    ]["np_likeness_score"]


out = grouped.apply(outliers).dropna()

# prepare outlier data for plotting, we need coordinates for every outlier.
if not out.empty:
    outx = list(out.index.get_level_values(0))
    outy = list(out.values)


# journals = sorted(journals, key=lambda x: q2.loc[x, "np_likeness_score"], reverse=True)

p = figure(
    background_fill_color="#ffffff",
    x_range=journals,  # toolbar_location=None, tools=""
)

# if no outliers, shrink lengths of stems to be no longer than the minimums or maximums
qmin = grouped.quantile(q=0.00)
qmax = grouped.quantile(q=1.00)
upper.np_likeness_score = [
    min([x, y])
    for (x, y) in zip(list(qmax.loc[:, "np_likeness_score"]), upper.np_likeness_score)
]
lower.np_likeness_score = [
    max([x, y])
    for (x, y) in zip(list(qmin.loc[:, "np_likeness_score"]), lower.np_likeness_score)
]

# Sort the data frames for whiskers and stems
upper = upper.loc[journals]
lower = lower.loc[journals]

# stems
p.segment(
    journals,
    upper.np_likeness_score,
    journals,
    q3.loc[journals].np_likeness_score,
    line_color="black",
)
p.segment(
    journals,
    lower.np_likeness_score,
    journals,
    q1.loc[journals].np_likeness_score,
    line_color="black",
)


boxes_data = pd.concat(
    [
        q1.loc[journals].rename(columns={"np_likeness_score": "q1"}),
        q2.loc[journals].rename(columns={"np_likeness_score": "q2"}),
        q3.loc[journals].rename(columns={"np_likeness_score": "q3"}),
        iqr.loc[journals].rename(columns={"np_likeness_score": "iqr"}),
    ],
    axis=1,
)
boxes_source = ColumnDataSource(boxes_data)

# boxes
top_box = p.vbar(
    "journal",
    0.7,
    "q2",
    "q3",
    # fill_color="#E08E79",
    fill_alpha=0.0,
    line_color="blue",
    source=boxes_source,
)
bottom_box = p.vbar(
    "journal",
    0.7,
    "q1",
    "q2",
    # fill_color="#3B8686",
    fill_alpha=0.0,
    line_color="blue",
    source=boxes_source,
)


# add hover just to the two box renderers
box_hover = HoverTool(
    renderers=[top_box, bottom_box],
    tooltips=[
        ("Journal", "@journal"),
        ("q1", "@q1"),
        ("q2", "@q2"),
        ("q3", "@q3"),
        ("IQR", "@iqr"),
    ],
)
p.add_tools(box_hover)

# whiskers (almost-0 height rects simpler than segments)
p.rect(journals, lower.np_likeness_score, 0.2, 0.01, line_color="black")
p.rect(journals, upper.np_likeness_score, 0.2, 0.01, line_color="black")

# outliers
if not out.empty:
    p.circle(outx, outy, size=6, color="black", fill_alpha=0.0)


p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = "black"
# p.grid.grid_line_width = 2
# p.xaxis.major_label_text_font_size = "16px"
p.xaxis.major_label_orientation = np.pi / 2.5

st.bokeh_chart(p, use_container_width=True)
