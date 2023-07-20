import os
import ast
import requests
import streamlit as st
import random

from streamlit_extras.switch_page_button import switch_page
from src.mongodb_cls import MongoDB_cls
from src.thumbnail_decoder import thumbnail_decoder

with open(os.path.join(os.getcwd(), 'style.css')) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

mongodb = MongoDB_cls()

def main():
    st.session_state.load_recipe_info_nav_main = True
    #mongodb = MongoDB_cls()
    try:
        favorite_food_list = mongodb.load_user_favorite_food_list(st.session_state.key)
    except:
        switch_page("streamlit_app")
    favorite_food_list = ast.literal_eval(favorite_food_list)

    st.sidebar.title("오늘의 레시피")
    try:
        st.sidebar.write(f'{st.session_state.key}님, 환영합니다')
    except:
        switch_page("streamlit_app")
        pass
    want_to_contribute = st.sidebar.button("logout")
    if want_to_contribute:
        switch_page("streamlit_app")

    # 로고로 변경하기
    st.title("오늘의 레시피")
    st.header(f':star: {st.session_state.key}님을 위한 레시피 추천')

    col_1, col_2 = st.columns([4,1])
    with col_1:
        st.empty()
    with col_2:
        bookmark_link = st.button(":pushpin: 좋아하는 레시피", use_container_width=True)
        if bookmark_link:
            switch_page("book_mark")

    st.subheader('💡 뭐 먹을 지 고민 된다면 편하게 말해주세요. 추천해드려요')
    st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)

    # 감성분석 추천
    try:
        text = st.session_state.text
        text = st.text_input(' ')
    except:
        text = st.text_input(' ')
    
    text_box_cols_1, text_box_cols_2 = st.columns([5,1])
    with text_box_cols_1:
        st.write('예시) 술 마실 때 먹기 좋은 국물 요리가 필요해')
    with text_box_cols_2:
        button_clicked = st.button("Submit", use_container_width=True)

    try:
        recommend_list = st.session_state.recommend_list
    except:
        recommend_list = []

    # When the button is clicked, display the text entered by the user.
    if button_clicked & (text != ''):
        st.session_state.text = text
        # FastAPI 서버의 URL
        url = "http://115.85.182.72:30006/recommend"
        # 요청 본문
        data = {"text": text}
        # POST 요청을 보냅니다.
        response = requests.post(url, json=data)
        recommend_list = mongodb.load_category_idx_to_recipeid(list(response.json()))
        # To shuffle this list:
        random.shuffle(recommend_list)
        recommend_list = recommend_list[:5]
        if len(recommend_list) == 0:
            st.warning("일치하는 추천메뉴가 없어요. 다른 말로 다시 입력해주세요")
        # else:
        st.session_state.recommend_list = recommend_list


    display_thumbnails(recommend_list, favorite_food_list)
 


    st.subheader('🤖 AI가 추천하는 메뉴')
    st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)

    # ----- 나중에 모델 아웃풋 리스트 들어갈 곳 ----- #
    thumbnail_ids = [6891816, 6843136, 7002443, 6996297, 6885909,
                     6915088, 6897374, 6933760, 6846168, 6881099]
    # --------------------------------------- #
    
    display_thumbnails(thumbnail_ids, favorite_food_list)
          

def display_thumbnails(thumbnail_ids, favorite_food_list):
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

                if st.button(button_text, key=f"box_good_{thumbnail_id}", use_container_width=True):
                    st.session_state[f"toggle_{thumbnail_id}"] = not toggle_state
                    if st.session_state[f"toggle_{thumbnail_id}"]:
                        if thumbnail_id not in favorite_food_list:
                            favorite_food_list.append(thumbnail_id)
                            st.session_state.recipe_id = thumbnail_id
                            mongodb.update_user_favorite_food_list(st.session_state.key, favorite_food_list)
                            switch_page("main_reset")
                    else:
                        if thumbnail_id in favorite_food_list:
                            favorite_food_list.remove(thumbnail_id)
                            mongodb.update_user_favorite_food_list(st.session_state.key, favorite_food_list)
                            switch_page("main_reset")

                box_good_buttons.append(toggle_state)

            with box_col_02:
                box_move_button = st.button('자세히', key=f"box_move_{thumbnail_id}", use_container_width=True)
                box_move_buttons.append(box_move_button)
        if i % 5 == 4:
            st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
            cols = st.columns(5)

    result = [thumbnail_ids[i] for i in range(len(thumbnail_ids)) if box_move_buttons[i]]
    if sum(box_move_buttons) == 1:
        st.session_state.recipe_id = result[0]
        switch_page("load_recipe_info")


if __name__ == "__main__":
    main()