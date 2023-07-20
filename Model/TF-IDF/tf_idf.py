'''
    수정하기
        24번째줄 recipe_data_final.csv 위치
        26번째줄 recipe_tfidf.pkl 위치
        29번째줄 tfidf_vectorizer.pkl 위치
'''

import pandas as pd
import numpy as np
import pickle
import ast

# from mongodb_cls import MongoDB_cls
from sklearn.metrics.pairwise import cosine_similarity

def join_text(t):
    return ' '.join(t)

# 여러개 레시피 넣고싶다.
def recommend_recipes_ingre(my_id, num_recom = 10):
    # 레시피 데이터 가져오기
    recipe = pd.read_csv('./DATA/recipe_data_final.csv')
    
    with open('recipe_tfidf.pkl', 'rb') as f:
        recipe_tfidf_pickle = pickle.load(f)

    with open('tfidf_vectorizer.pkl', 'rb') as f:
        tfidf_vectorizer_pickle = pickle.load(f)
    
    # 입력된 레시피 ID에 해당하는 레시피 정보 추출
    selected_recipes = recipe[recipe['recipeid'].isin(my_id)]
    
    # ‘ingredients’ 열의 값을 리스트로 변환
    selected_recipes['ingredients'] = selected_recipes['ingredients'].apply(ast.literal_eval)
    # ‘ingredient_quantity’ 열의 값을 리스트로 변환
    selected_recipes['ingredient_quantity'] = selected_recipes['ingredient_quantity'].apply(ast.literal_eval)
    # ‘process’ 열의 값을 리스트로 변환
    selected_recipes['process'] = selected_recipes['process'].apply(ast.literal_eval)
    
    # 입력된 레시피 tfidf
    selected_recipe_tfidf = tfidf_vectorizer_pickle.transform(selected_recipes['ingredients'].apply(join_text))
    
    # 입력된 레시피id들과 전체 레시피 유사도 구하기
    similarity_scores = cosine_similarity(selected_recipe_tfidf, recipe_tfidf_pickle)
    
    # 각 레시피의 유사도 평균
    similarity_scores = np.mean(similarity_scores,axis=0)

    # # 유사도 기준 내림차순으로 레시피 정렬
    related_recipe_indices = similarity_scores.argsort()[::-1][:num_recom]
    related_recipe_indices = list(set(related_recipe_indices) - set(my_id))
    related_recipes = recipe.iloc[related_recipe_indices]
    return related_recipes['recipeid'].to_list()

if __name__=="__main__":
    # my_id = 'test'
    # mogodb = MongoDB_cls()
    # # 좋아요 누른 상위 5개 레시피
    # my_recipeids = eval(mogodb.load_user_favorite_food_list(my_id))[-5:]
    my_recipeids = [221097]

    recom = recommend_recipes_ingre(my_recipeids, num_recom = 10)
    print(recom)
