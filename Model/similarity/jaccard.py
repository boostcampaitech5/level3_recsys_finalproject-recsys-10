from recipe_dataset import get_recipe_dataset


def jaccard_similarity(x, y):

    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))

    return intersection_cardinality / float(union_cardinality)

def jaccard_similar_recipe(path,user_ingre):

    df = get_recipe_dataset(path)
    recommend = df['ingredients'].apply(lambda x: jaccard_similarity(x,user_ingre)).sort_values(ascending=False)
    
    return df.iloc[recommend.index]['recipeid'].tolist()[:10] # 자카드 유사도가 높은 상위 10개 레시피아이디 추천

if __name__=="__main__":
    """
    input:

    1. 레시피 데이터프레임의 '경로'
    2. 유저가 가진 재료 '리스트'
    
    output:

    1. 유저가 가진 재료와 가장 유사한 재료들로 이루어져 있는 10개 recipeid '리스트'
    """
    path = '/opt/ml/final_project/Recipe_datasets' # 데이터프레임의 경로 입력
    user_ingre = ['마늘', '소금', '돼지고기', '닭가슴살', '양파', '간장', '설탕', '베이컨', '대파', '파스타'] # 유저가 갖고 있는 재료 입력
    n_similar_recipe = jaccard_similar_recipe(path,user_ingre) # 자카드 유사도가 높은 상위 10개 레시피아이디 추천
    print(n_similar_recipe)