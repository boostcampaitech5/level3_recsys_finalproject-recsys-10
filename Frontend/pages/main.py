import os
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

import requests
from PIL import Image

with open(os.path.join(os.getcwd(), 'style.css')) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    st.sidebar.title("오늘의 레시피")
    try:
        st.sidebar.write(f'{st.session_state.key}님, 환영합니다')
    except:
        switch_page("streamlit_app")
        pass
    want_to_contribute = st.sidebar.button("logout")
    if want_to_contribute:
        switch_page("streamlit_app")

    st.header(f'{st.session_state.key}님을 위한 레시피 추천')
    st.markdown("---")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        # ----------- 하드 코딩 ------------ #
        response = requests.get("https://recipe1.ezmember.co.kr/cache/recipe/2019/05/25/39ac1e73e998e88da300d38663242f0a1_m.jpg", stream=True)
        image = Image.open(response.raw)
        st.image(image, use_column_width=True)
        check_01 = st.checkbox('checkbox',key="check01")
    with col2:
        response = requests.get("https://recipe1.ezmember.co.kr/cache/recipe/2016/02/16/d74c6731fce3dc72c5579b24083185f11_m.jpg", stream=True)
        image = Image.open(response.raw)
        st.image(image, use_column_width=True)
        check_02 = st.checkbox('checkbox',key="check02")
    with col3:
        response = requests.get("https://recipe1.ezmember.co.kr/cache/recipe/2023/05/18/44c74d970c984f419d0e01a736542c421_m.jpg", stream=True)
        image = Image.open(response.raw)
        st.image(image, use_column_width=True)
        check_03 = st.checkbox('checkbox',key="check03")
    with col4:
        response = requests.get("https://recipe1.ezmember.co.kr/cache/recipe/2023/02/02/41942668ad91ccfb305c4cab9dee030f1_m.jpg", stream=True)
        image = Image.open(response.raw)
        st.image(image, use_column_width=True)
        box_col_01, box_col_02 = st.columns(2)
        with box_col_01:
            box_good_04 = st.button('좋아요', key="box_good_04", use_container_width=True)
        with box_col_02:
            box_move_04 = st.button('자세히', key="box_move_04", use_container_width=True)
    with col5:
        response = requests.get("https://recipe1.ezmember.co.kr/cache/recipe/2018/03/22/779982ef4e8f9c32c472297e632789a91_m.jpg", stream=True)
        image = Image.open(response.raw)
        st.image(image, use_column_width=True)
        box_col_01, box_col_02 = st.columns(2)
        with box_col_01:
            box_good_05 = st.button('좋아요', key="box_good_05", use_container_width=True)
        with box_col_02:
            box_move_05 = st.button('자세히', key="box_move_05", use_container_width=True)



if __name__ == "__main__":
    main()