from Ingredient_Based_Recipe_RecSys import get_recipe_by_ingredient_based_recsys
from Ingredient_Based_Recipe_RecSys import initialize_vector

ingresync_recipe_path = '/opt/ml/Recipe_Project/Recipe_datasets/recipe_data_final.csv'
cate_recipe_path = '/opt/ml/Recipe_Project/Recipe_datasets/cate_data_final.csv'
save_pickle_path = '/opt/ml/Recipe_Project/Recipe_code/Ingredient_Recsys_pkl.pkl'


# csv 파일들을 토대로 Recipe의 vector들을 만드는 함수. -> 프로그램 실행 시점에 한 번만 실행시켜두면 됨 -> 약 3분 소요
initialize_vector(ingresync_recipe_path, cate_recipe_path, save_pickle_path) 


#만들어진 vector들을 대상으로 유저 vector와 cosine 유사도를 비교 -> 약 30초 정도 소요.
preference_recipe = ['돼지고기', '베이컨', '소금', '마늘', '닭가슴살', '양파', '간장', '설탕', '대파']
Rec_recipe = get_recipe_by_ingredient_based_recsys(preference_recipe, save_pickle_path)

print(Rec_recipe)



