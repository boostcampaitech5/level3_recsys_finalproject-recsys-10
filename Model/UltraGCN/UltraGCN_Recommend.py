from ultragcn_main import recsys_train_by_ultragcn
from ultragcn_main import recsys_get_recipe_by_ultragcn
from ultragcn_main import recsys_add_user_by_ultragcn
from ultragcn_main import initialize_dataset
import torch
import torch.nn as nn
import argparse

#13186 - 3322323
#13187 - 332334
user_num = 3322323

initialize_dataset('/opt/ml/Recipe_Project/Recipe_datasets/sequence_final.csv')
recsys_add_user_by_ultragcn(user_num, [6880130, 6914310, 6926601, 6932904, 2361260, 6908721, 6886836, 6881986, 6954309, 6903367, 6920011, 1223, 243434345, 345346476546])
recsys_train_by_ultragcn('/opt/ml/Recipe_Project/Recipe_code/ultragcn/config/Ultragcn_Recipe_RecSys.ini')

result = recsys_get_recipe_by_ultragcn(user_num)
print(result)

#[6880130, 6914310, 6926601, 4549274, 6931617, 6874146, 6926753, 6902692, 6932904, 2361260, 6908721, 6886836, 6881986, 6954309, 6903367, 6920011, 6852429, 6952013, 6888918, 6830426, 6852956, 6887392, 3187681, 6895976, 6931945, 6856432, 6854896, 6929653, 6849655, 6845180]