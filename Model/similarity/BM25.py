from recipe_dataset import get_recipe_dataset
import pickle
import os

def bm25_recipe(path,user_ingre):

    df = get_recipe_dataset(path)
    bm25_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),'bm25matrix')
    with open(bm25_path, 'rb') as bm25result_file:
        bm25 = pickle.load(bm25result_file)
    
    return bm25.get_top_n(user_ingre, df['recipeid'], n=10)

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
    n_similar_recipe = bm25_recipe(path,user_ingre) # 자카드 유사도가 높은 상위 10개 레시피아이디 추천
    print(n_similar_recipe)