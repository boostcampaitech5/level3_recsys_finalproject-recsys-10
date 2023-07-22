import pandas as pd
import os
import ast

def get_recipe_dataset(path): # 데이터베이스 위치를 입력받으면 레시피 데이터프레임을 반환하는 함수
    similarity
    recipe_df = pd.read_csv(os.path.join(path),encoding='utf-8')
    recipe_df['ingredients'] = recipe_df['ingredients'].apply(lambda x:ast.literal_eval(x))
    return recipe_df