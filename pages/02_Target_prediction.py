from utils import run_predictions, ort_session, generate_file_content
from heatmap import generate_heatmap
import streamlit as st
import pandas as pd
import numpy as np

st.title("Target prediction heatmap")
st.write(
    f"Show a target prediction heatmap on a {len(ort_session.get_outputs())} ChEMBL targets pannel"
)

# File upload
uploaded_file = st.file_uploader(
    "Upload a CSV file with a **mol_id** and **SMILES** columns", type="csv"
)


@st.cache_data
def predict_all(df):
    df["preds"] = df["SMILES"].apply(run_predictions)
    return df


# Check if a file has been uploaded
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df = predict_all(df)
    data = np.stack(df["preds"].to_numpy())
    x_labels = [o.name for o in ort_session.get_outputs()]
    y_labels = [str(x) for x in df["mol_id"].to_numpy()]
    p = generate_heatmap(data, x_labels, y_labels)
    st.bokeh_chart(p, use_container_width=True)

    result = pd.DataFrame(data, columns=x_labels)
    result["mol_id"] = df["mol_id"]

    # Button to trigger file download
    f = generate_file_content(result)
    st.download_button(
        "Click to download the predictions",
        f,
        file_name="preds.csv",
        mime="text/csv",
    )
