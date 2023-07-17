import streamlit as st
from src.mongodb_cls import MongoDB_cls

def register(username, password, thumbnail_ids, check_list) -> bool:
    mongodb = MongoDB_cls()
    collection = mongodb.get_collection('recipe_app_db', 'user_login_db')

    # user registration verification
    existing_user = collection.find_one({"username": username})
    if username.strip() == "" or password.strip() == "":
        st.error("Username 또는 Password를 입력하세요.")
        return False
    if existing_user:
        st.error("이미 존재하는 사용자입니다.")
        return False
    if sum(check_list) < 5:
        st.error(f"선호 메뉴를 5가지 이상 선택해주세요 [{sum(check_list)}개 선택]")
        return False
    
    result = [thumbnail_ids[i] for i in range(len(thumbnail_ids)) if check_list[i]]

    # create a new user
    user = {
        "username": username,
        "password": password,
        "favorite_food": str(result)
    }
    collection.insert_one(user)
    st.success("회원가입이 완료되었습니다.")
    return True