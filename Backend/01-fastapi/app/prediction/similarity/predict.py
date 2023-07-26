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
        with open(os.path.join(path,'recipe_data.pkl'), 'wb') as f:
            pickle.dump(recipe, f)
    return recipe

def bm25_recipe(path,user_ingre):

    df = get_recipe_dataset(path)
    bm25_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),'bm25matrix')
    with open(bm25_path, 'rb') as bm25result_file:
        bm25 = pickle.load(bm25result_file)

    rid_list = list(df["recipeid"])
    
    return bm25.get_top_n(user_ingre, rid_list, n=10)


def jaccard_similarity(x, y):

    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))

    return intersection_cardinality / float(union_cardinality)

def jaccard_similar_recipe(path,user_ingre):

    df = get_recipe_dataset(path)
    recommend = df['ingredients'].apply(lambda x: jaccard_similarity(x,user_ingre)).sort_values(ascending=False)
    
    return df.iloc[recommend.index]['recipeid'].tolist()[:10] # 자카드 유사도가 높은 상위 10개 레시피아이디 추천









