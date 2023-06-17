from streamlit_ketcher import st_ketcher
import streamlit as st
from utils import similarity_search, generate_file_content
import pandas as pd


st.title("Similarity search")
smiles = st_ketcher()

similarity_threshold = st.slider("Similarity threshold:", min_value=0.0, max_value=1.0)


if smiles:
    try:
        results = similarity_search(smiles, similarity_threshold)
    except:
        results = None
    df = pd.DataFrame(results)
    st.dataframe(df)

    # Button to trigger file download
    f = generate_file_content(df)
    st.download_button(
        "Click to download similarity results",
        f,
        file_name="similarities.csv",
        mime="text/csv",
    )
