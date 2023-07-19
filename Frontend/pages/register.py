import os
import yaml
import streamlit as st

from streamlit_extras.switch_page_button import switch_page

from src.mongodb_cls import MongoDB_cls
from src.register_page import register
from src.thumbnail_decoder import thumbnail_decoder


def register_page():
    mongodb = MongoDB_cls()
    with open(os.path.join(os.getcwd(), 'style.css')) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    st.sidebar.title("오늘의 레시피")

    want_to_contribute = st.button("< 뒤로 가기")
    if want_to_contribute:
        switch_page("streamlit_app")

    st.title("회원가입")

    with st.form(key="입력 form"):
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        st.markdown('---')
        st.subheader('선호하는 음식을 선택하세요 [10개 이상]')
        st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)


        # cat4(food type) Top 3 views by type
        with open('_data/register_page_item_list.yaml') as config_file:
            config = yaml.safe_load(config_file)
        thumbnail_ids = config['register_page_item_list_cat3']

        cols = st.columns(5)
        checkboxes = []
        for i, thumbnail_id in enumerate(thumbnail_ids):
            col = cols[i%5]
            with col:
                thumbnail = thumbnail_decoder(mongodb.load_thumbnail(thumbnail_id))
                st.image(thumbnail, use_column_width=True)
                checkbox = st.checkbox(mongodb.load_title(thumbnail_id), key=f"check_box{i}")
                checkboxes.append(checkbox)
            if i%5 == 4:
                st.markdown('---')
                cols = st.columns(5)
        if i%5 != 4:
            st.markdown('---')

        register_button = st.form_submit_button("회원가입")


    if register_button:
        register_complete = register(new_username, new_password, thumbnail_ids, checkboxes)
        if register_complete:
            switch_page("streamlit_app")


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    register_page()