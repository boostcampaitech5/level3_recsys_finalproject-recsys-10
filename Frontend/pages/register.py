import os
import yaml
import urllib.parse
import requests
import streamlit as st

from PIL import Image
from streamlit_extras.switch_page_button import switch_page

from src.mongodb_cls import MongoDB_cls

def register(username, password, check_list):
    mongodb = MongoDB_cls()
    collection = mongodb.get_collection('recipe_app_db', 'user_login_db')

    # 이미 존재하는 사용자인지 확인
    existing_user = collection.find_one({"username": username})
    if username.strip() == "" or password.strip() == "":
        st.error("Username 또는 Password를 입력하세요.")
        return False
    if existing_user:
        st.error("이미 존재하는 사용자입니다.")
        return False
    # 새로운 사용자 생성
    user = {
        "username": username,
        "password": password
    }
    collection.insert_one(user)
    st.success("회원가입이 완료되었습니다.")
    return True


def register_page():
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
        st.subheader('선호하는 음식을 선택하세요 [5개 이상]')
        st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
    
        col1, col2, col3, col4 = st.columns(4)
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
            check_04 = st.checkbox('checkbox',key="check04")
        
        register_button = st.form_submit_button("회원가입")
    check_list = [check_01, check_02, check_03, check_04]
    if register_button:
        print(check_list)
        register_complete = register(new_username, new_password, check_list)
        if register_complete:
            switch_page("streamlit_app")

if __name__ == "__main__":
    register_page()