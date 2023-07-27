import os
import ast
import streamlit as st

from streamlit_extras.switch_page_button import switch_page

from src.mongodb_cls import MongoDB_cls
from src.thumbnail_decoder import thumbnail_decoder
from src.thumbnail_decoder import image_from_url


def recipe_info():
    with open(os.path.join(os.getcwd(), 'style.css')) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        
    want_to_back = st.button("< 뒤로 가기")
    if want_to_back:
        if st.session_state.load_recipe_info_nav_main == 0:
            switch_page("main")
        elif st.session_state.load_recipe_info_nav_main == 1:
            switch_page("book_mark")
        else:
            switch_page("ingredient_page")
        
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

    ## type 1 UI
    # st.header(':notebook_with_decorative_cover: '+title)
    # st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
    # cols = st.columns([1, 2])
    # with cols[0]:
    #     st.image(thumbnail, use_column_width=True)
    # with cols[1]:
    #     st.subheader('[재료]')
    #     ingre_cols = st.columns(2)
    #     with ingre_cols[0]:
    #         st.dataframe(ingredient_data1, hide_index=True, use_container_width=True)
    #     with ingre_cols[1]:
    #         st.dataframe(ingredient_data2, hide_index=True, use_container_width=True)
    #     st.subheader(f'[조리 순서]')
    #     for index, process_string in enumerate(process_list):
    #         st.info(f'{index + 1}. {process_string}')
    # st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)

    # type2 UI
    st.header(':notebook_with_decorative_cover: '+title)
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

    st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
    st.subheader(f'[조리 순서]')
    recipe_thumb_list = mongodb.load_image_link(recipe_id)
    if len(recipe_thumb_list) == len(process_list):
        for index, (image_link, process_string) in enumerate(zip(recipe_thumb_list, process_list)):
            cols = st.columns([1, 2])
            with cols[0]:
                st.image(image_from_url(image_link), use_column_width=True)
            with cols[1]:
                st.info(f'{index + 1}. {process_string}')
    else:
        for index, (image_link, process_string) in enumerate(zip(recipe_thumb_list, process_list)):
            st.info(f'{index + 1}. {process_string}')
    st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)


if __name__ == "__main__":
    recipe_info()