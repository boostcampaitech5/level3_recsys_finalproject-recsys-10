import os
import streamlit as st

from streamlit_extras.switch_page_button import switch_page
from src.mongodb_cls import MongoDB_cls
from src.thumbnail_decoder import thumbnail_decoder

with open(os.path.join(os.getcwd(), 'style.css')) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    mongodb = MongoDB_cls()
    st.sidebar.title("오늘의 레시피")
    try:
        st.sidebar.write(f'{st.session_state.key}님, 환영합니다')
    except:
        switch_page("streamlit_app")
        pass
    want_to_contribute = st.sidebar.button("logout")
    if want_to_contribute:
        switch_page("streamlit_app")

    st.header(f'{st.session_state.key}님을 위한 레시피 추천')
    st.markdown("---")

    # 내중에 모델 아웃풋 리스트 들어갈 곳
    thumbnail_ids = [6912734, 6843136, 7002443, 6996297, 6885909,
                     6915088, 6897374, 6933760, 6846168, 6881099]

    cols = st.columns(5)
    box_good_buttons = []
    box_move_buttons = []
    result = [False]

    for i, thumbnail_id in enumerate(thumbnail_ids):
        col = cols[i%5]
        with col:
            thumbnail = thumbnail_decoder(mongodb.load_thumbnail(thumbnail_id))
            st.image(thumbnail, use_column_width=True)
            title = mongodb.load_title(thumbnail_id)
            if len(title) > 19:
                title = title[:19] + ".."  # 텍스트 길이 제한
            st.text(title)
            box_col_01, box_col_02 = st.columns(2)
            with box_col_01:
                box_good_button = st.button('좋아요', key=f"box_good_{thumbnail_id}", use_container_width=True)
                box_good_buttons.append(box_good_button)
            with box_col_02:
                box_move_button = st.button('자세히', key=f"box_move_{thumbnail_id}", use_container_width=True)
                box_move_buttons.append(box_move_button)
        if i%5 == 4:
            st.markdown('---')
            cols = st.columns(5)
    
    result = [thumbnail_ids[i] for i in range(len(thumbnail_ids)) if box_move_buttons[i]]
    if sum(box_move_buttons) == 1:
        st.session_state.recipe_id = result[0]
        switch_page("load_recipe_info")


if __name__ == "__main__":
    main()