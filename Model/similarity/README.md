# level3_recsys_finalproject-recsys-10

> level3_recsys_finalproject-recsys-10

## path의 경우 **recipe_data_final.csv**가 있는 디렉토리가 됨 (ex. '/opt/ml/final_project/Recipe_datasets').
## 최초 실행시 **path**에 csv가 pickle로 변환되어 **recipe_data.pkl**로 저장되며, 피클 저장 이후에는 함수호출할 때 피클을 불러오게 됨.

1. BM25.py
    ㄴ bm25_recipe(path,user_ingre):
        * input
            * **path**: 레시피 데이터프레임(recipe_data_final.csv) 경로 -> string
            * **user_ingre**: 유저에게 입력받은 재료 리스트 -> list
        * output
            * 상위 10개 레시피 아이디 리스트 -> list

2. jaccard.py
    ㄴ jaccard_similar_recipe(path,user_ingre):
        * input
            * **path**: 레시피 데이터프레임(recipe_data_final.csv) 경로 -> string
            * **user_ingre**: 유저에게 입력받은 재료 리스트 -> list
        * output
            * 상위 10개 레시피 아이디 리스트 -> list

