import os
import ast
import pickle
import requests
import streamlit as st

from streamlit_extras.switch_page_button import switch_page

from src.mongodb_cls import MongoDB_cls
from src.thumbnail_decoder import thumbnail_decoder

mongodb = MongoDB_cls()

with open(os.path.join(os.getcwd(), 'style.css')) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def ingredient_main():
    st.session_state.load_recipe_info_nav_main = 2
    try:
        favorite_food_list = mongodb.load_user_favorite_food_list(st.session_state.key)
    except:
        switch_page("streamlit_app")
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

    if 'options' not in st.session_state:
        st.session_state.options = []

    # Multiselect to select ingredients from loaded_model
    options = st.multiselect('냉장고에 있는 재료들을 입력해주세요', loaded_model, st.session_state.options)

    # Update the options in session state with the selected ingredients
    st.session_state.options = options
    
    
    st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
    
    
    try:
        recommend_list_bm25 = st.session_state.recommend_list_bm25
    except:
        recommend_list_bm25 = []
    
    if True:
        st.session_state.options = options
        # -------------- url_bm25 model -------------- #
        url_bm25 = "http://101.101.219.32:30005/predict/bm25"
        # Convert ingre_list to a JSON string
        ingre_list_json = str(options)
        # Create the request payload (empty for this case)
        payload = {}
        # Add ingre_list as a JSON string to the query parameter
        params = {
            'ingre_list': ingre_list_json
        }
        response_bm25 = requests.post(url_bm25, params=params, json=payload)
        # POST request
        recommend_list_bm25= response_bm25.json()['data']
        # st.subheader('🌕 좋아하는 음식들의 카테고리 상호작용 데이터로 추천해드려요')
        st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
        st.session_state.recommend_list_bm25 = recommend_list_bm25
        # display_thumbnails(recommend_list_bm25, favorite_food_list, 'bm25')
        # --------------------------------------------- #
        
        url_bm25 = "http://101.101.219.32:30005/predict/jaccard"
        # Convert ingre_list to a JSON string
        ingre_list_json = str(options)
        # Create the request payload (empty for this case)
        payload_jaccard = {}
        # Add ingre_list as a JSON string to the query parameter
        params_jaccard = {
            'ingre_list': ingre_list_json
        }
        response_jaccard = requests.post(url_bm25, params=params_jaccard, json=payload_jaccard)
        # POST request
        try:
            recommend_list_jaccard= response_jaccard.json()['data']
            st.session_state.recommend_list_jaccard = recommend_list_jaccard
            # display_thumbnails(recommend_list_jaccard, favorite_food_list, 'jaccard')
        except:
            pass
        try:
            li = []
            li.extend(recommend_list_bm25)
            li.extend(recommend_list_jaccard)
        except:
            li = []
            li.extend(recommend_list_bm25)
        li = list(set(li))[:10]
        display_thumbnails(li, favorite_food_list, 'all')
        
    st.session_state.options = options

def display_thumbnails(thumbnail_ids, favorite_food_list, unique_str):
    # mongodb = MongoDB_cls()
    cols = st.columns(5)
    box_good_buttons = []
    box_move_buttons = []
    result = [False]

    for i, thumbnail_id in enumerate(thumbnail_ids):
        col = cols[i % 5]
        with col:
            thumbnail = thumbnail_decoder(mongodb.load_thumbnail(thumbnail_id))
            st.image(thumbnail, use_column_width=True)
            title = mongodb.load_title(thumbnail_id)
            if len(title) > 19:
                title = title[:19] + ".."  # 텍스트 길이 제한
            st.text(title)
            box_col_01, box_col_02 = st.columns(2)

            with box_col_01:
                toggle_state = st.session_state.get(f"toggle_{thumbnail_id}", thumbnail_id in favorite_food_list)
                if toggle_state:
                    button_text = ':heart:' #❌❎
                else:
                    button_text = ':white_heart:' #👍✅♡

                if st.button(button_text, key=f"box_good_{thumbnail_id}{unique_str}", use_container_width=True):
                    st.session_state[f"toggle_{thumbnail_id}"] = not toggle_state
                    if st.session_state[f"toggle_{thumbnail_id}"]:
                        if thumbnail_id not in favorite_food_list:
                            favorite_food_list.append(thumbnail_id)
                            st.session_state.recipe_id = thumbnail_id
                            mongodb.update_user_favorite_food_list(st.session_state.key, favorite_food_list)
                            mongodb.add_category_onehot(st.session_state.key, thumbnail_id)
                            switch_page("ingredient_page_reset")
                    else:
                        if thumbnail_id in favorite_food_list:
                            favorite_food_list.remove(thumbnail_id)
                            mongodb.update_user_favorite_food_list(st.session_state.key, favorite_food_list)
                            mongodb.sub_category_onehot(st.session_state.key, thumbnail_id)
                            switch_page("ingredient_page_reset")

                box_good_buttons.append(toggle_state)

            with box_col_02:
                box_move_button = st.button('자세히', key=f"box_move_{thumbnail_id}{unique_str}", use_container_width=True)
                box_move_buttons.append(box_move_button)
        if i % 5 == 4:
            st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
            cols = st.columns(5)

    result = [thumbnail_ids[i] for i in range(len(thumbnail_ids)) if box_move_buttons[i]]
    if sum(box_move_buttons) == 1:
        st.session_state.recipe_id = result[0]
        switch_page("load_recipe_info")

if __name__ == "__main__":
    ingredient_main()