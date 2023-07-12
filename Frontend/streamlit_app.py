import os
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from pymongo import MongoClient
from pages.login import login_page



def home():
    with open(os.path.join(os.getcwd(), 'style.css')) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    st.sidebar.title("오늘의 레시피")
    st.sidebar.write(f'환영합니다')
    st.sidebar.write(f'로그인/회원가입을 해주세요')
    login_result = login_page()
    try:
        if login_result[0] == True:
            st.session_state.key = login_result[1]
            switch_page("main")
    except Exception as e:
        pass

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    home()