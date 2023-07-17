import os
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from pages.login import login_page


def home():
    """
    Displays the main homepage and handles user login.
    """
    
    # load css
    with open(os.path.join(os.getcwd(), 'style.css')) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    # main page logo img
    st.image(os.path.join(os.getcwd(), 'img/logo.png'), use_column_width=True)

    # sidebar area setting
    st.sidebar.title("오늘의 레시피")
    st.sidebar.write(f'환영합니다')
    st.sidebar.write(f'로그인/회원가입을 해주세요')

    # login page load and handling login
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