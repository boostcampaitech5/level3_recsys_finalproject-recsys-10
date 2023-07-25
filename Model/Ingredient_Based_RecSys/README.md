# level3_recsys_finalproject-recsys-10

> level3_recsys_finalproject-recsys-10

Ingredient_Based_Recipe_RecSys 모듈을 임포트하고,

initialize_vector 함수와 get_recipe_by_ingredient_based_recsys 함수를 사용한다.

> initialize_vector: 

1. csv 파일들을 토대로 Recipe의 vector들을 만드는 함수로, 프로그램 실행 시점에 한 번만 실행하여 Ingredient Vector metrix를 만든다.

2. 인자로 넘겨줘야 하는 값은 3개의 경로이다. 3개의 인자를 주는데 순서대로 다음과 같다.


ingresync_recipe_path : 재료, 레시피가 담긴 종합 csv 파일의 경로를 넘겨준다. (recipe_data_final.csv)

cate_recipe_path : 카테고리 레시피 정보가 담긴 csv 파일의 경로를 넘겨준다. (cate_data_final.csv)

save_pickle_path : Ingredient Vector metrix와 부가 정보를 저장할 pickle의 경로를 넘겨준다. (이름 X, 경로만 입력)


3. 이 함수를 사용하면, 지정된 경로에 pickle 파일이 생성된다. 이 pickle 파일의 경로는 get_recipe_by_ingredient_based_recsys 함수의 인자가 된다.


> get_recipe_by_ingredient_based_recsys:

1. Ingredient Vector metrix, 유저 vector의 cosine 유사도를 비교하여 추천을 해준다. -> 약 30초 정도 소요.

2. 인자로 넘겨줘야 하는 값은 2개 이다. 2개의 인자를 주는데 순서대로 다음과 같다.


preference_recipe : 유저가 가지고 있는 재료 목록을 리스트 형식으로 넘겨준다. ex) ['돼지고기', '베이컨', '소금', '마늘', '닭가슴살', '양파', '간장', '설탕', '대파']

save_pickle_path : Ingredient Vector metrix를 담고 있는 pickle 파일의 경로를 넘겨준다.


3. 반환 값은 튜플의 형태이다.
-> (list 형태의 10개의 추천 레시피, 학습에 사용되지 않은 재료들을 나열한 문자열)

-> 학습에 사용되지 않은 재료들을 나열한 문자열은 재료 검색창을 만들었기 때문에 사용하지 않아도 무방. -> 혹시 모를 경우를 대비해 남겨는 둠.