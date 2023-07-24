import pandas as pd
import os
import ast
import pickle

def get_recipe_dataset(path): # 데이터베이스 위치를 입력받으면 레시피 데이터프레임을 반환하는 함수
    try:
        with open(os.path.join(path,'recipe_data.pkl'), 'rb') as f:
            recipe = pickle.load(f)
    except:
        recipe = pd.read_csv(os.path.join(path,'recipe_data_final.csv'))
        recipe['ingredients'] = recipe['ingredients'].apply(lambda x:ast.literal_eval(x))
        with open(os.path.join(os.path.join(path),'recipe_data.pkl'), 'wb') as f:
            pickle.dump(recipe, f)
    return recipe