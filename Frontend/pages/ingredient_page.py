import os
import pickle
import streamlit as st

from streamlit_extras.switch_page_button import switch_page

with open(os.path.join(os.getcwd(), 'style.css')) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def ingredient_main():
    st.sidebar.title("오늘의 레시피")
    try:
        st.sidebar.write(f'{st.session_state.key}님, 환영합니다')
    except:
        switch_page("streamlit_app")
        pass
    want_to_contribute = st.sidebar.button("logout")
    if want_to_contribute:
        switch_page("streamlit_app")

    want_to_contribute = st.button("< 뒤로 가기")
    if want_to_contribute:
        switch_page("main")

    st.title(":ice_cube: 나만의 냉장고 추천")
    st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)


    # Load the pickled model
    with open('_data/ingredients_list15.pkl', 'rb') as file:
        loaded_model = pickle.load(file)

    
    col_1, col_2 = st.columns([5,1])
    with col_1:
        options = st.multiselect('냉장고에 있는 재료들을 입력해주세요', loaded_model)
        # st.empty()
    with col_2:
        st.write('')
        st.write('')
        submit_btn = st.button('선택 완료', use_container_width=True)
    
    if submit_btn:
        st.write('You selected:', options)

    st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)

if __name__ == "__main__":
    ingredient_main()