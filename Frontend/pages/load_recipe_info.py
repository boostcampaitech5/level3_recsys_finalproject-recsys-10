import os
import ast
import streamlit as st

from streamlit_extras.switch_page_button import switch_page

from src.mongodb_cls import MongoDB_cls
from src.thumbnail_decoder import thumbnail_decoder


def recipe_info():
    with open(os.path.join(os.getcwd(), 'style.css')) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        
    want_to_back = st.button("< 뒤로 가기")
    if want_to_back:
        if st.session_state.load_recipe_info_nav_main:
            switch_page("main")
        else:
            switch_page("book_mark")
        
    st.sidebar.title("오늘의 레시피")
    try:
        st.sidebar.write(f'{st.session_state.key}님, 환영합니다')
    except:
        switch_page("streamlit_app")
        pass
    want_to_contribute = st.sidebar.button("logout")
    if want_to_contribute:
        switch_page("streamlit_app")

    recipe_id = st.session_state.recipe_id

    mongodb = MongoDB_cls()
    title = mongodb.load_title(recipe_id)
    thumbnail = thumbnail_decoder(mongodb.load_thumbnail(recipe_id))

    # ingredient data output processing
    ingredients, ingredient_quantity, process = mongodb.load_recipe_info(recipe_id)

    ingredients_list = ast.literal_eval(ingredients)
    ingredient_quantity_list = ast.literal_eval(ingredient_quantity)
    process_list = ast.literal_eval(process)

    half_length = len(ingredients_list) // 2
    ingredient_data1 = {"재료": ingredients_list[:half_length], "용량": ingredient_quantity_list[:half_length]}
    ingredient_data2 = {"재료": ingredients_list[half_length:], "용량": ingredient_quantity_list[half_length:]}


    st.header(title)
    st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
    cols = st.columns([1, 2])
    with cols[0]:
        st.image(thumbnail, use_column_width=True)
    with cols[1]:
        st.subheader('[재료]')
        ingre_cols = st.columns(2)
        with ingre_cols[0]:
            st.dataframe(ingredient_data1, hide_index=True, use_container_width=True)
        with ingre_cols[1]:
            st.dataframe(ingredient_data2, hide_index=True, use_container_width=True)
        st.subheader(f'[조리 순서]')
        for index, process_string in enumerate(process_list):
            st.info(f'{index + 1}. {process_string}')
    st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)


if __name__ == "__main__":
    recipe_info()