import streamlit as st  # type: ignore

def main():
    st.set_page_config(layout="centered")

    image_files = {
        "Room Front View (3D)": "views/front_view_3d.png",
        "Room Front View": "views/front_view.png",
        "Room Top View": "views/top_view.png"
    }

    tabs = st.tabs(list(image_files.keys()))

    for tab, (label, img_path) in zip(tabs, image_files.items()):
        with tab:
            st.subheader(label)
            st.image(img_path) 

if __name__ == "__main__":
    main()
