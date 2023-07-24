# level3_recsys_finalproject-recsys-10

> level3_recsys_finalproject-recsys-10

ultragcn_main 모듈을 임포트하고,

총 4개의 함수를 사용한다.

1. initialize_dataset
2. recsys_add_user_by_ultragcn
3. recsys_train_by_ultragcn
4. recsys_get_recipe_by_ultragcn


> initialize_dataset :

1. csv파일 경로를 주면, 그 csv파일을 통해 UltraGCN 모델 학습에 필요한 txt파일(train_txt, test_txt)과 userid, recipeid의 mapping_table을 초기화해주는 함수이다

2. 제공된 csv파일을 통해 학습 txt 파일(train_txt, test_txt)을 생성하므로 이 함수를 사용하면, csv 파일을 통해 제공된 유저 정보 후에 추가된 유저 정보들은 모두 초기화된다.

-> 프로그램 실행 시점에 한 번만 이 함수를 실행하고나서 유저 선호 데이터를 추가, 수정한다.

3. 인자로 넘겨줘야 하는 값은 5개이다. 5개의 인자를 주는데 순서대로 다음과 같다.


csv_path : csv 파일의 경로이다. 이 csv 파일은 sequence_final.csv 파일의 형식의 형태로 제공되어야한다.

train_file_path : train_txt 파일을 저장할 경로이다. (이름 X, 경로만 입력)

test_file_path : test_txt 파일을 저장할 경로이다. (이름 X, 경로만 입력)

User_LM_path : user의 mapping table이 저장된 pickle을 저장할 경로이다. (이름 X, 경로만 입력)

Recipe_LE_path : Recipe의 LabelEncoder가 저장된 pickle을 저장할 경로이다. (이름 X, 경로만 입력)


4. 실행 후에는 train_txt 파일과 test_txt 파일이 생성된다. 이는 csv 파일을 통해 생성된 txt 파일이다.


> recsys_add_user_by_ultragcn : 

1. 새로운 유저의 선호 목록을 데이터에 추가하거나, 기존 유저의 선호 목록을 업데이트 하는 함수이다. -> 업데이트 정보는 txt 파일에 저장된다.

2. 인자로 넘겨줘야 하는 값은 6개이다. 6개의 인자를 주는데 순서대로 다음과 같다.


new_user_name_number : 유저의 고유 번호를 int 형태로 넘겨준다.

new_user_preference : 유저가 선호하는 레시피 번호를 list 형태로 넘겨준다.

train_file_path : initialize_dataset 함수로 만들어진 train_txt가 저장된 경로이다.

test_file_path : initialize_dataset 함수로 만들어진 text_txt가 저장된 경로이다.

User_LM_path : initialize_dataset 함수로 만들어진 user mapping table pickle이 저장된 경로이다.

Recipe_LE_path : initialize_dataset 함수로 만들어진 recipe mapping table pickle이 저장된 경로이다.


3. 반환 값은 따로 없고, txt 파일들(train_txt, test_txt)이 갱신된다.


> recsys_train_by_ultragcn :

1. config_file의 값을 토대로 학습을 진행하는 함수이다. 

2. 인자로 config_file의 경로를 넘겨주면 된다. 

3. 반환 값은 따로 없으며, UltraGCN 모델이 학습되고, 추천의 결과가 txt 파일로 자동 저장된다.


> recsys_get_recipe_by_ultragcn :

1. 추천 목록을 받고 싶은 유저의 고유 번호를 인자로 받아서 10개의 레시피를 추천해주는 함수이다.

2. 인자로 넘겨줘야 하는 값은 4개이다. 4개의 인자를 주는데 순서대로 다음과 같다.


user_name_number : 추천 결과를 받고 싶은 유저의 고유 번호를 int 형태로 넘겨준다.

result_file_path : 모델 학습 결과 추천의 결과가 담긴 txt 파일의 경로이다.

User_LM_path : initialize_dataset 함수로 만들어진 user mapping table pickle이 저장된 경로이다.

Recipe_LE_path : initialize_dataset 함수로 만들어진 recipe mapping table pickle이 저장된 경로이다.


3. 반환 값은 10개의 추천 레시피로 이루어진 list이다.
=======
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

