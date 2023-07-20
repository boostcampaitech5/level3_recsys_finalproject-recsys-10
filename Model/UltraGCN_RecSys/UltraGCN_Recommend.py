from ultragcn_main import recsys_train_by_ultragcn
from ultragcn_main import recsys_get_recipe_by_ultragcn
from ultragcn_main import recsys_add_user_by_ultragcn
import torch
import torch.nn as nn
import argparse



user_num = recsys_add_user_by_ultragcn([6885928, 6843983, 6928654, 6963896, 6881542])
print(user_num)
recsys_train_by_ultragcn('/opt/ml/Recipe_Project/Recipe_code/ultragcn/config/Ultragcn_Recipe_RecSys.ini')
result = recsys_get_recipe_by_ultragcn(user_num)
print(result)
