import streamlit as st


def run():
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )

    st.write("# Hello! 👋")

    # st.sidebar.success("Select a demo above.")

    st.markdown(
        """
    """
    )


if __name__ == "__main__":
    run()
