import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from src.mongodb_cls import MongoDB_cls

def login_page():
    st.title("로그인")
    with st.form(key="입력 form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        col1, col2 = st.columns(2)
        with col1:
            login_button = st.form_submit_button("로그인", use_container_width=True)
        with col2:
            register_button = st.form_submit_button("회원가입", use_container_width=True)
    login_result = st.empty()  # 결과를 표시할 빈 상자 생성

    if register_button:
        switch_page("register")

    if login_button:
        if username.strip() == "" or password.strip() == "":
            st.error("Username 또는 Password를 입력하세요.")
        else:
            # mongodb connect
            mongodb = MongoDB_cls()
            authenticated = mongodb.login(username, password)
            if authenticated:
                login_result.success("로그인 성공")  # 빈 상자에 내용 업데이트
                return (True, username)
            else:
                login_result.error("로그인 실패")  # 빈 상자에 내용 업데이트
                return False
