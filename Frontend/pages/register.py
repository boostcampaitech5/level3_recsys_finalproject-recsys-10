import os
import streamlit as st

from streamlit_extras.switch_page_button import switch_page
from src.mongodb_cls import MongoDB_cls
from src.thumbnail_decoder import thumbnail_decoder

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
        st.subheader('선호하는 음식을 선택하세요 [5개 이상]')
        st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)


        thumbnail_ids = [6912734, 6843136, 7002443, 6996297, 6885909]

        cols = st.columns(5)
        checkboxes = []
        for i, thumbnail_id in enumerate(thumbnail_ids):
            col = cols[i]
            with col:
                thumbnail = thumbnail_decoder(mongodb.load_thumbnail(thumbnail_id))
                st.image(thumbnail, use_column_width=True)
                checkbox = st.checkbox(mongodb.load_title(thumbnail_id), key=f"check_box{i}")
                checkboxes.append(checkbox)

        register_button = st.form_submit_button("회원가입")

    if register_button:
        register_complete = register(new_username, new_password, checkboxes)
        if register_complete:
            switch_page("streamlit_app")

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    register_page()