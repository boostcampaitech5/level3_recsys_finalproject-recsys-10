import pandas as pd
import numpy as np
import os
from collections import Counter
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
import random
import pickle

def remove_whitespace_from_keys(dictionary):
    for key in list(dictionary.keys()):
        updated_key = key.replace(" ", "")
        if updated_key != key:
            dictionary[updated_key] = dictionary.pop(key)
    return dictionary

def count_keys_with_value_above_threshold(dictionary, threshold):
    count = 0
    for value in dictionary.values():
        if value >= threshold:
            count += 1
    return count

def merge_dicts(dict1, dict2):
    merged_dict = dict1.copy()
    for key, value in dict2.items():
        if key in merged_dict:
            merged_dict[key] = np.concatenate((merged_dict[key], np.array(value)))
        else:
            merged_dict[key] = np.array(value)
    return merged_dict


def get_top_similar_recipes(query_vector, recipe_dict, top_k=10):
    similarities = []
    query_vector = np.array(query_vector).reshape(1, -1)

    for recipe_number, dense_vector in recipe_dict.items():
        dense_vector = np.array(dense_vector).reshape(1, -1)
        similarity = cosine_similarity(query_vector, dense_vector)[0, 0]
        similarities.append((recipe_number, similarity))

    similarities.sort(key=lambda x: x[1], reverse=True)
    top_similar_recipes = similarities[:top_k]

    return top_similar_recipes


def initialize_vector(ingresync_recipe_path, cate_recipe_path, pickle_path):
    ingresync_recipe = pd.read_csv(ingresync_recipe_path)
    cate_recipe = pd.read_csv(cate_recipe_path)
    save_pickle_path = os.path.join(pickle_path, 'Ingredient_Recsys_pkl.pkl')


    ingresync_recipe['ingredients'] = ingresync_recipe['ingredients'].apply(eval)
    ingresync_recipe['ingredient_quantity'] = ingresync_recipe['ingredient_quantity'].apply(eval)
    ingresync_recipe['process'] = ingresync_recipe['process'].apply(eval)

    ingredients_origin = set(np.concatenate(ingresync_recipe['ingredients']))
    ingredients_origin.discard('')
    ingredients_origin = list(set(ingredients_origin))

    counter = Counter(val for sublist in ingresync_recipe['ingredients'] for val in sublist)
    ingredients_counts = dict(counter)

    sorted_ingredients_counts = dict(sorted(ingredients_counts.items(), key=lambda x: -x[1]))

    cate_recipe['cat1'] = cate_recipe['cat1'].astype(str)
    cate_recipe['cat2'] = cate_recipe['cat2'].astype(str)
    cate_recipe['cat3'] = cate_recipe['cat3'].astype(str)
    cate_recipe['cat4'] = cate_recipe['cat4'].astype(str)

    # 범주형 열에 대해 One-Hot Encoding 수행

    df_encoded = pd.get_dummies(cate_recipe[['cat1', 'cat2', 'cat3', 'cat4']])

    # recipeid 컬럼과 One-Hot Encoding 결과 병합
    df_merged = pd.concat([cate_recipe['recipeid'], df_encoded], axis=1)

    # 사전 생성
    result_dict = dict(zip(df_merged['recipeid'], df_merged.iloc[:, 1:].values.tolist()))

    ingredient_sparse_vector_collect = {}
    ingredient_dense_vector_collect = {}
    threshold = 5
    ingredients_threshold_len = count_keys_with_value_above_threshold(ingredients_counts, threshold)
    ingredients_origin_len = len(ingredients_origin)
    sorted_ingredients_counts_list = list(sorted_ingredients_counts.keys())[:ingredients_threshold_len]

    pca = PCA(n_components=128)

    for index, row in ingresync_recipe.iterrows():
        ingredient_sparse_vector = [0] * ingredients_threshold_len

        #재료 중복 제거
        set_row = list(set(row['ingredients']))

        #재료 사이 공백 제거 -> 하니까 살짝 오류가 생기네.. 새송이버섯 -> 새송이 버섯 이런것도 있어가지고 함부로 줄일 수가 없다..
        #set_row = [string.replace(" ", "") for string in set_row_c if isinstance(string, str)]

        for r in set_row:
            if(ingredients_counts[r] >= threshold):
                if(r in row['cook']):
                    ingredient_sparse_vector[sorted_ingredients_counts_list.index(r)] = (1 - ingredients_counts[r]/ingredients_origin_len) * 10
                else:
                    ingredient_sparse_vector[sorted_ingredients_counts_list.index(r)] = (1 - ingredients_counts[r]/ingredients_origin_len)

        ingredient_sparse_vector_collect[row['recipeid']] = ingredient_sparse_vector

    pca.fit(np.array(list(ingredient_sparse_vector_collect.values())))

    ingredient_dense_vector_collect = pca.transform(np.array(list(ingredient_sparse_vector_collect.values())))
    ingredient_dense_vector_collect_dict = {key: ingredient_dense_vector_collect[i] for i, key in enumerate(ingredient_sparse_vector_collect)}
    ingredient_dense_vector_collect = merge_dicts(ingredient_dense_vector_collect_dict, result_dict)

    final_dict = {
        'ingredients_threshold_len': ingredients_threshold_len,
        'ingredients_counts': ingredients_counts,
        'threshold': threshold,
        'sorted_ingredients_counts_list': sorted_ingredients_counts_list,
        'ingredients_origin_len': ingredients_origin_len,
        'pca': pca,
        'ingredient_dense_vector_collect': ingredient_dense_vector_collect
    }

    with open(save_pickle_path,'wb') as file:
        pickle.dump(final_dict, file)
    



def get_recipe_by_ingredient_based_recsys(user_ingredient : list, Ingredient_Recsys_pkl_path) -> tuple:

    with open(Ingredient_Recsys_pkl_path, 'rb') as file:
        loaded_data = pickle.load(file)

    ingredients_threshold_len = loaded_data['ingredients_threshold_len']
    ingredients_counts = loaded_data['ingredients_counts'] 
    threshold = loaded_data['threshold']
    sorted_ingredients_counts_list = loaded_data['sorted_ingredients_counts_list']
    ingredients_origin_len = loaded_data['ingredients_origin_len']
    pca = loaded_data['pca']
    ingredient_dense_vector_collect = loaded_data['ingredient_dense_vector_collect']

    user_ingredient_sparse_vector = [0] * ingredients_threshold_len
    invalid_ingredients = []

    #재료사이 공백 제거
    user_ingredient = [string.replace(" ", "") for string in user_ingredient if isinstance(string, str)]

    for u in user_ingredient:
        if(u in ingredients_counts.keys()):
            if(ingredients_counts[u] >= threshold):
                user_ingredient_sparse_vector[sorted_ingredients_counts_list.index(u)] = (1 - ingredients_counts[u]/ingredients_origin_len)
        else:
            invalid_ingredients.append(u)


    query_vector_beta = pca.transform(np.array(list(user_ingredient_sparse_vector)).reshape(1, -1))
    
    new_shape = (1, list(ingredient_dense_vector_collect.values())[0].shape[0])
    query_vector = np.zeros(new_shape)
    query_vector[:, :query_vector_beta.shape[1]] = query_vector_beta

    top_similar_recipes = get_top_similar_recipes(query_vector, ingredient_dense_vector_collect, top_k=20)
    top_list = [x[0] for x in top_similar_recipes]

    random_10 = random.sample(top_list, k=10)
    output = ', '.join(invalid_ingredients)

    return (random_10, output)