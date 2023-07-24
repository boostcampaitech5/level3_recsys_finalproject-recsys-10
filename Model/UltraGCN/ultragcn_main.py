import torch
import torch.nn as nn
import torch.nn.functional as F
import pickle
import numpy as np
import pandas as pd
import torch.utils.data as data
import scipy.sparse as sp
import os
import gc
import configparser
import time
import argparse
from torch.utils.tensorboard import SummaryWriter

from sklearn.preprocessing import LabelEncoder
import joblib
import shutil
import pickle
import copy

number = 1

def data_param_prepare(config_file):

    config = configparser.ConfigParser()
    config.read(config_file)

    params = {}

    embedding_dim = config.getint('Model', 'embedding_dim')
    params['embedding_dim'] = embedding_dim
    ii_neighbor_num = config.getint('Model', 'ii_neighbor_num')
    params['ii_neighbor_num'] = ii_neighbor_num
    model_save_path = config['Model']['model_save_path']
    params['model_save_path'] = model_save_path
    max_epoch = config.getint('Model', 'max_epoch')
    params['max_epoch'] = max_epoch

    params['enable_tensorboard'] = config.getboolean('Model', 'enable_tensorboard')
    
    initial_weight = config.getfloat('Model', 'initial_weight')
    params['initial_weight'] = initial_weight

    dataset = config['Training']['dataset']
    params['dataset'] = dataset
    train_file_path = config['Training']['train_file_path']
    gpu = config['Training']['gpu']
    params['gpu'] = gpu
    #device는 환경에 따라 바꿔줘
    #device = torch.device('cuda:'+ params['gpu'] if torch.cuda.is_available() else "cpu")
    device = 'cpu'
    params['device'] = device
    lr = config.getfloat('Training', 'learning_rate')
    params['lr'] = lr
    batch_size = config.getint('Training', 'batch_size')
    params['batch_size'] = batch_size
    early_stop_epoch = config.getint('Training', 'early_stop_epoch')
    params['early_stop_epoch'] = early_stop_epoch
    w1 = config.getfloat('Training', 'w1')
    w2 = config.getfloat('Training', 'w2')
    w3 = config.getfloat('Training', 'w3')
    w4 = config.getfloat('Training', 'w4')
    params['w1'] = w1
    params['w2'] = w2
    params['w3'] = w3
    params['w4'] = w4
    negative_num = config.getint('Training', 'negative_num')
    negative_weight = config.getfloat('Training', 'negative_weight')
    params['negative_num'] = negative_num
    params['negative_weight'] = negative_weight

    gamma = config.getfloat('Training', 'gamma')
    params['gamma'] = gamma
    lambda_ = config.getfloat('Training', 'lambda')
    params['lambda'] = lambda_
    sampling_sift_pos = config.getboolean('Training', 'sampling_sift_pos')
    params['sampling_sift_pos'] = sampling_sift_pos
    
    test_batch_size = config.getint('Testing', 'test_batch_size')
    params['test_batch_size'] = test_batch_size
    topk = config.getint('Testing', 'topk') 
    params['topk'] = topk

    test_file_path = config['Testing']['test_file_path']

    # dataset processing
    train_data, test_data, train_mat, user_num, item_num, constraint_mat = load_data(train_file_path, test_file_path)
    train_loader = data.DataLoader(train_data, batch_size=batch_size, shuffle = True, num_workers=5)
    test_loader = data.DataLoader(list(range(user_num)), batch_size=test_batch_size, shuffle=False, num_workers=5)

    params['user_num'] = user_num
    params['item_num'] = item_num

    # mask matrix for testing to accelarate testing speed
    mask = torch.zeros(user_num, item_num)
    interacted_items = [[] for _ in range(user_num)]
    for (u, i) in train_data:
        mask[u][i] = -np.inf
        interacted_items[u].append(i)

    # test user-item interaction, which is ground truth
    test_ground_truth_list = [[] for _ in range(user_num)]
    for (u, i) in test_data:
        test_ground_truth_list[u].append(i)

    # Compute \Omega to extend UltraGCN to the item-item co-occurrence graph
    ii_cons_mat_path = './' + dataset + '_ii_constraint_mat'
    ii_neigh_mat_path = './' + dataset + '_ii_neighbor_mat'
    
    if os.path.exists(ii_cons_mat_path):
        ii_constraint_mat = pload(ii_cons_mat_path)
        ii_neighbor_mat = pload(ii_neigh_mat_path)
    else:
        ii_neighbor_mat, ii_constraint_mat = get_ii_constraint_mat(train_mat, ii_neighbor_num)
        pstore(ii_neighbor_mat, ii_neigh_mat_path)
        pstore(ii_constraint_mat, ii_cons_mat_path)

    return params, constraint_mat, ii_constraint_mat, ii_neighbor_mat, train_loader, test_loader, mask, test_ground_truth_list, interacted_items


def get_ii_constraint_mat(train_mat, num_neighbors, ii_diagonal_zero = False):
    print('Computing \\Omega for the item-item graph... ')
    A = train_mat.T.dot(train_mat)	# I * I
    n_items = A.shape[0]
    res_mat = torch.zeros((n_items, num_neighbors))
    res_sim_mat = torch.zeros((n_items, num_neighbors))
    if ii_diagonal_zero:
        A[range(n_items), range(n_items)] = 0
    items_D = np.sum(A, axis = 0).reshape(-1)
    users_D = np.sum(A, axis = 1).reshape(-1)

    beta_uD = (np.sqrt(users_D + 1) / users_D).reshape(-1, 1)
    beta_iD = (1 / np.sqrt(items_D + 1)).reshape(1, -1)
    all_ii_constraint_mat = torch.from_numpy(beta_uD.dot(beta_iD))
    for i in range(n_items):
        row = all_ii_constraint_mat[i] * torch.from_numpy(A.getrow(i).toarray()[0])
        row_sims, row_idxs = torch.topk(row, num_neighbors)
        res_mat[i] = row_idxs
        res_sim_mat[i] = row_sims
        if i % 15000 == 0:
            print('i-i constraint matrix {} ok'.format(i))

    print('Computation \\Omega OK!')
    return res_mat.long(), res_sim_mat.float()

    
def load_data(train_file, test_file):
    trainUniqueUsers, trainItem, trainUser = [], [], []
    testUniqueUsers, testItem, testUser = [], [], []
    n_user, m_item = 0, 0
    trainDataSize, testDataSize = 0, 0
    with open(train_file, 'r') as f:
        for l in f.readlines():
            if len(l) > 0:
                l = l.strip('\n').split(' ')
                items = [int(i) for i in l[1:]]
                uid = int(l[0])
                trainUniqueUsers.append(uid)
                trainUser.extend([uid] * len(items))
                trainItem.extend(items)
                m_item = max(m_item, max(items))
                n_user = max(n_user, uid)
                trainDataSize += len(items)
    trainUniqueUsers = np.array(trainUniqueUsers)
    trainUser = np.array(trainUser)
    trainItem = np.array(trainItem)

    with open(test_file) as f:
        for l in f.readlines():
            if len(l) > 0:
                l = l.strip('\n').split(' ')
                try:
                    items = [int(i) for i in l[1:]]
                except:
                    items = []
                uid = int(l[0])
                testUniqueUsers.append(uid)
                testUser.extend([uid] * len(items))
                testItem.extend(items)
                try:
                    m_item = max(m_item, max(items))
                except:
                    m_item = m_item
                n_user = max(n_user, uid)
                testDataSize += len(items)

    train_data = []
    test_data = []

    n_user += 1
    m_item += 1

    for i in range(len(trainUser)):
        train_data.append([trainUser[i], trainItem[i]])
    for i in range(len(testUser)):
        test_data.append([testUser[i], testItem[i]])
    train_mat = sp.dok_matrix((n_user, m_item), dtype=np.float32)

    for x in train_data:
        train_mat[x[0], x[1]] = 1.0

    # construct degree matrix for graphmf

    items_D = np.sum(train_mat, axis = 0).reshape(-1)
    users_D = np.sum(train_mat, axis = 1).reshape(-1)

    print(users_D)

    beta_uD = (np.sqrt(users_D + 1) / users_D).reshape(-1, 1)
    beta_iD = (1 / np.sqrt(items_D + 1)).reshape(1, -1)

    constraint_mat = {"beta_uD": torch.from_numpy(beta_uD).reshape(-1),
                      "beta_iD": torch.from_numpy(beta_iD).reshape(-1)}

    return train_data, test_data, train_mat, n_user, m_item, constraint_mat


def pload(path):
	with open(path, 'rb') as f:
		res = pickle.load(f)
	print('load path = {} object'.format(path))
	return res

def pstore(x, path):
	with open(path, 'wb') as f:
		pickle.dump(x, f)
	print('store object in path = {} ok'.format(path))


def Sampling(pos_train_data, item_num, neg_ratio, interacted_items, sampling_sift_pos):
	neg_candidates = np.arange(item_num)

	if sampling_sift_pos:
		neg_items = []
		for u in pos_train_data[0]:
			probs = np.ones(item_num)
			probs[interacted_items[u]] = 0
			probs /= np.sum(probs)

			u_neg_items = np.random.choice(neg_candidates, size = neg_ratio, p = probs, replace = True).reshape(1, -1)
	
			neg_items.append(u_neg_items)

		neg_items = np.concatenate(neg_items, axis = 0) 
	else:
		neg_items = np.random.choice(neg_candidates, (len(pos_train_data[0]), neg_ratio), replace = True)
	
	neg_items = torch.from_numpy(neg_items)
	
	return pos_train_data[0], pos_train_data[1], neg_items	# users, pos_items, neg_items


class UltraGCN(nn.Module):
    def __init__(self, params, constraint_mat, ii_constraint_mat, ii_neighbor_mat):
        super(UltraGCN, self).__init__()
        self.user_num = params['user_num']
        self.item_num = params['item_num']
        self.embedding_dim = params['embedding_dim']
        self.w1 = params['w1']
        self.w2 = params['w2']
        self.w3 = params['w3']
        self.w4 = params['w4']

        self.negative_weight = params['negative_weight']
        self.gamma = params['gamma']
        self.lambda_ = params['lambda']

        self.user_embeds = nn.Embedding(self.user_num, self.embedding_dim)
        self.item_embeds = nn.Embedding(self.item_num, self.embedding_dim)

        self.constraint_mat = constraint_mat
        self.ii_constraint_mat = ii_constraint_mat
        self.ii_neighbor_mat = ii_neighbor_mat

        self.initial_weight = params['initial_weight']
        self.initial_weights()

    def initial_weights(self):
        nn.init.normal_(self.user_embeds.weight, std=self.initial_weight)
        nn.init.normal_(self.item_embeds.weight, std=self.initial_weight)

    def get_omegas(self, users, pos_items, neg_items):
        device = self.get_device()
        if self.w2 > 0:
            pos_weight = torch.mul(self.constraint_mat['beta_uD'][users], self.constraint_mat['beta_iD'][pos_items]).to(device)
            pow_weight = self.w1 + self.w2 * pos_weight
        else:
            pos_weight = self.w1 * torch.ones(len(pos_items)).to(device)
        
        # users = (users * self.item_num).unsqueeze(0)
        if self.w4 > 0:
            neg_weight = torch.mul(torch.repeat_interleave(self.constraint_mat['beta_uD'][users], neg_items.size(1)), self.constraint_mat['beta_iD'][neg_items.flatten()]).to(device)
            neg_weight = self.w3 + self.w4 * neg_weight
        else:
            neg_weight = self.w3 * torch.ones(neg_items.size(0) * neg_items.size(1)).to(device)


        weight = torch.cat((pow_weight, neg_weight))
        return weight

    def cal_loss_L(self, users, pos_items, neg_items, omega_weight):
        device = self.get_device()
        user_embeds = self.user_embeds(users)
        pos_embeds = self.item_embeds(pos_items)
        neg_embeds = self.item_embeds(neg_items)
      
        pos_scores = (user_embeds * pos_embeds).sum(dim=-1) # batch_size
        user_embeds = user_embeds.unsqueeze(1)
        neg_scores = (user_embeds * neg_embeds).sum(dim=-1) # batch_size * negative_num

        neg_labels = torch.zeros(neg_scores.size()).to(device)
        neg_loss = F.binary_cross_entropy_with_logits(neg_scores, neg_labels, weight = omega_weight[len(pos_scores):].view(neg_scores.size()), reduction='none').mean(dim = -1)
        
        pos_labels = torch.ones(pos_scores.size()).to(device)
        pos_loss = F.binary_cross_entropy_with_logits(pos_scores, pos_labels, weight = omega_weight[:len(pos_scores)], reduction='none')

        loss = pos_loss + neg_loss * self.negative_weight
      
        return loss.sum()

    def cal_loss_I(self, users, pos_items):
        device = self.get_device()
        neighbor_embeds = self.item_embeds(self.ii_neighbor_mat[pos_items].to(device))    # len(pos_items) * num_neighbors * dim
        sim_scores = self.ii_constraint_mat[pos_items].to(device)     # len(pos_items) * num_neighbors
        user_embeds = self.user_embeds(users).unsqueeze(1)
        
        loss = -sim_scores * (user_embeds * neighbor_embeds).sum(dim=-1).sigmoid().log()
      
        # loss = loss.sum(-1)
        return loss.sum()

    def norm_loss(self):
        loss = 0.0
        for parameter in self.parameters():
            loss += torch.sum(parameter ** 2)
        return loss / 2

    def forward(self, users, pos_items, neg_items):
        omega_weight = self.get_omegas(users, pos_items, neg_items)
        
        loss = self.cal_loss_L(users, pos_items, neg_items, omega_weight)
        loss += self.gamma * self.norm_loss()
        loss += self.lambda_ * self.cal_loss_I(users, pos_items)
        return loss

    def test_foward(self, users):
        items = torch.arange(self.item_num).to(users.device)
        user_embeds = self.user_embeds(users)
        item_embeds = self.item_embeds(items)
         
        return user_embeds.mm(item_embeds.t())

    def get_device(self):
        return self.user_embeds.weight.device
    
########################### TRAINING #####################################

def train(model, optimizer, train_loader, test_loader, mask, test_ground_truth_list, interacted_items, params): 
    device = params['device']
    best_epoch, best_recall, best_ndcg = 0, 0, 0
    early_stop_count = 0
    early_stop = False

    batches = len(train_loader.dataset) // params['batch_size']
    if len(train_loader.dataset) % params['batch_size'] != 0:
        batches += 1
    print('Total training batches = {}'.format(batches))
    
    #if params['enable_tensorboard']:
        #writer = SummaryWriter()

    for epoch in range(params['max_epoch']):
        model.train() 
        start_time = time.time()

        for batch, x in enumerate(train_loader): # x: tensor:[users, pos_items]
            users, pos_items, neg_items = Sampling(x, params['item_num'], params['negative_num'], interacted_items, params['sampling_sift_pos'])
            users = users.to(device)
            pos_items = pos_items.to(device)
            neg_items = neg_items.to(device)

            model.zero_grad()
            loss = model(users, pos_items, neg_items).to(device)
            #if params['enable_tensorboard']:
                #writer.add_scalar("Loss/train_batch", loss, batches * epoch + batch)
            loss.backward()
            optimizer.step()
        
        train_time = time.strftime("%H: %M: %S", time.gmtime(time.time() - start_time))
        #if params['enable_tensorboard']:
            #writer.add_scalar("Loss/train_epoch", loss, epoch)

        need_test = True
        #if epoch < 50 and epoch % 5 != 0:
            #need_test = False
            
        if need_test:
            start_time = time.time()
            F1_score, Precision, Recall, NDCG = test(model, test_loader, test_ground_truth_list, mask, params['topk'], params['user_num'], epoch)
            #if params['enable_tensorboard']:
                #writer.add_scalar('Results/recall@20', Recall, epoch)
                #writer.add_scalar('Results/ndcg@20', NDCG, epoch)
            test_time = time.strftime("%H: %M: %S", time.gmtime(time.time() - start_time))
            
            print('The time for epoch {} is: train time = {}, test time = {}'.format(epoch, train_time, test_time))
            print("Loss = {:.5f}, F1-score: {:5f} \t Precision: {:.5f}\t Recall: {:.5f}\tNDCG: {:.5f}".format(loss.item(), F1_score, Precision, Recall, NDCG))

            if Recall > best_recall:
                best_recall, best_ndcg, best_epoch = Recall, NDCG, epoch
                early_stop_count = 0
                torch.save(model.state_dict(), params['model_save_path'])

            else:
                early_stop_count += 1
                if early_stop_count == params['early_stop_epoch']:
                    early_stop = True
        
        if early_stop:
            print('##########################################')
            print('Early stop is triggered at {} epochs.'.format(epoch))
            print('Results:')
            print('best epoch = {}, best recall = {}, best ndcg = {}'.format(best_epoch, best_recall, best_ndcg))
            print('The best model is saved at {}'.format(params['model_save_path']))
            break

    #writer.flush()

    print('Training end!')


########################### TESTING #####################################

def hit(gt_item, pred_items):
	if gt_item in pred_items:
		return 1
	return 0


def ndcg(gt_item, pred_items):
	if gt_item in pred_items:
		index = pred_items.index(gt_item)
		return np.reciprocal(np.log2(index+2))
	return 0


def RecallPrecision_ATk(test_data, r, k):
	"""
    test_data should be a list? cause users may have different amount of pos items. shape (test_batch, k)
    pred_data : shape (test_batch, k) NOTE: pred_data should be pre-sorted
    k : top-k
    """
	right_pred = r[:, :k].sum(1)
	precis_n = k
	
	recall_n = np.array([len(test_data[i]) for i in range(len(test_data))])
	recall_n = np.where(recall_n != 0, recall_n, 1)
	recall = np.sum(right_pred / recall_n)
	precis = np.sum(right_pred) / precis_n
	return {'recall': recall, 'precision': precis}


def MRRatK_r(r, k):
	"""
    Mean Reciprocal Rank
    """
	pred_data = r[:, :k]
	scores = np.log2(1. / np.arange(1, k + 1))
	pred_data = pred_data / scores
	pred_data = pred_data.sum(1)
	return np.sum(pred_data)


def NDCGatK_r(test_data, r, k):
	"""
    Normalized Discounted Cumulative Gain
    rel_i = 1 or 0, so 2^{rel_i} - 1 = 1 or 0
    """
	assert len(r) == len(test_data)
	pred_data = r[:, :k]

	test_matrix = np.zeros((len(pred_data), k))
	for i, items in enumerate(test_data):
		length = k if k <= len(items) else len(items)
		test_matrix[i, :length] = 1
	max_r = test_matrix
	idcg = np.sum(max_r * 1. / np.log2(np.arange(2, k + 2)), axis=1)
	dcg = pred_data * (1. / np.log2(np.arange(2, k + 2)))
	dcg = np.sum(dcg, axis=1)
	idcg[idcg == 0.] = 1.
	ndcg = dcg / idcg
	ndcg[np.isnan(ndcg)] = 0.
	return np.sum(ndcg)


def test_one_batch(X, k):
    sorted_items = X[0].numpy()
    groundTrue = X[1]
    r = getLabel(groundTrue, sorted_items)
    ret = RecallPrecision_ATk(groundTrue, r, k)
    return ret['precision'], ret['recall'], NDCGatK_r(groundTrue,r,k)

def getLabel(test_data, pred_data):
    r = []
    for i in range(len(test_data)):
        groundTrue = test_data[i]
        predictTopK = pred_data[i]
        pred = list(map(lambda x: x in groundTrue, predictTopK))
        pred = np.array(pred).astype("float")
        r.append(pred)
    return np.array(r).astype('float')


def test(model, test_loader, test_ground_truth_list, mask, topk, n_user, epoch):
    users_list = []
    rating_list = []
    groundTrue_list = []
    global number

    with torch.no_grad():
        model.eval()
        for idx, batch_users in enumerate(test_loader):
            
            batch_users = batch_users.to(model.get_device())
            rating = model.test_foward(batch_users) 
            rating = rating.cpu()
            rating += mask[batch_users]
            
            _, rating_K = torch.topk(rating, k=topk)
            rating_list.append(rating_K)

            groundTrue_list.append([test_ground_truth_list[u] for u in batch_users])

    f = open(f'RecSys_Result_UltraGCN.txt','w') 
    for s in rating_list:
        for t in s:
            f.write(str(number) + ' ')
            f.write(' '.join(map(str, t.tolist())))
            f.write('\n')
            number += 1
    f.close()
    number = 1

    X = zip(rating_list, groundTrue_list)
    Recall, Precision, NDCG = 0, 0, 0

    for i, x in enumerate(X):
        precision, recall, ndcg = test_one_batch(x, topk)
        Recall += recall
        Precision += precision
        NDCG += ndcg
        
    Precision /= n_user
    Recall /= n_user
    NDCG /= n_user
    F1_score = 2 * (Precision * Recall) / (Precision + Recall)

    return F1_score, Precision, Recall, NDCG



#csv파일 경로를 주면, 그 csv파일을 통해 UltraGCN 모델 학습에 필요한 txt파일과 userid, recipeid의 mapping_table을 초기화.
#csv 파일은 sequence_final.csv 형식이어야 함.
def initialize_dataset(csv_path):

    #환경에 따라 수정해야할 경로.
    ultragcn_recipe_train_data_path = '/opt/ml/Recipe_Project/Recipe_code/ultragcn/data/Ultragcn_Recipe_Data/ultragcn_recipe_train_data.txt'
    ultragcn_recipe_test_data_path = '/opt/ml/Recipe_Project/Recipe_code/ultragcn/data/Ultragcn_Recipe_Data/ultragcn_recipe_test_data.txt'

    sequence_data = pd.read_csv(csv_path)

    condition = ((sequence_data['star']==4) | (sequence_data['star']==5)) # or 말고 | 사용해야 먹힌다.
    sequence_data = sequence_data[condition]

    rid_counts = dict(sequence_data['rid'].value_counts())

    threshold = 10
    sequence_data = sequence_data[sequence_data['rid'].map(lambda x: rid_counts[x]) <= threshold]
    sequence_data.reset_index()

    #userid mapping
    userid_LE = LabelEncoder()
    userid_LE.fit(sequence_data['uid'])
    sequence_data['uid'] = userid_LE.transform(sequence_data['uid'])
    user_label_mapping = {label: i for i, label in enumerate(list(sequence_data['uid'].unique()))}

    with open('/opt/ml/Recipe_Project/Recipe_code/ultragcn/Userid_label_encoder.pickle', 'wb') as file:
        pickle.dump(user_label_mapping, file)

    #recipeid mapping
    recipeid_LE = LabelEncoder()
    recipeid_LE.fit(sequence_data['rid'])
    sequence_data['rid'] = recipeid_LE.transform(sequence_data['rid'])
    sequence_data

    Recipeid_LE_path = '/opt/ml/Recipe_Project/Recipe_code/ultragcn/Recipeid_label_encoder.pkl'
    joblib.dump(recipeid_LE, Recipeid_LE_path)
    
    #train, test txt파일 생성
    f = open(ultragcn_recipe_train_data_path, 'w')
    tf = open(ultragcn_recipe_test_data_path, 'w')
    for i,v in sequence_data.groupby('uid')['rid']:
        f.write(str(i))
        f.write(' ')
        if(len(v.values)<10):
            f.write(' '.join(str(e) for e in v.values))
        else:
            f.write(' '.join(str(e) for e in v.values[:int((len(v.values)/10)*9)]))
        f.write('\n')
        if(len(v.values)>=10):
            tf.write(str(i))
            tf.write(' ')
            tf.write(' '.join(str(e) for e in v.values[(int(len(v.values)/10)*9):]))
            tf.write('\n')
    f.close()
    tf.close()



#새로운 유저의 선호 목록을 데이터에 추가하고 유저의 고유 번호 반환
def recsys_add_user_by_ultragcn(new_user_name_number : int, new_user_preference : list):

    # 폴더 위치에 따라 수정 필요
    train_file_path = '/opt/ml/Recipe_Project/Recipe_code/ultragcn/data/Ultragcn_Recipe_Data/ultragcn_recipe_train_data.txt'
    test_file_path = '/opt/ml/Recipe_Project/Recipe_code/ultragcn/data/Ultragcn_Recipe_Data/ultragcn_recipe_test_data.txt'
    User_LM_path = '/opt/ml/Recipe_Project/Recipe_code/ultragcn/Userid_label_encoder.pickle'
    Recipe_LE_path = '/opt/ml/Recipe_Project/Recipe_code/ultragcn/Recipeid_label_encoder.pkl'

    exist_flag = True

    with open(User_LM_path, 'rb') as file:
        user_label_mapping = pickle.load(file)
    recipe_LE = joblib.load(Recipe_LE_path)

    user_label_mapping_key = list(user_label_mapping.keys())
    user_label_mapping_value = list(user_label_mapping.values())

    if(not new_user_name_number in user_label_mapping_value):
        exist_flag = False
        last_key = max(user_label_mapping_key)
        new_key = last_key + 1

        user_label_mapping[new_key] = new_user_name_number

        with open(User_LM_path, 'wb') as file:
            pickle.dump(user_label_mapping, file)

    new_user_preference_temp =copy.deepcopy(new_user_preference)
    new_user_preference = []

    for up in new_user_preference_temp:
        try:
            t = recipe_LE.transform([up])
            new_user_preference.append(int(t[0]))
        except ValueError as e:
            continue
    
    all_train_user_preference = ' '.join(str(e) for e in new_user_preference)
    train_user_preference = ' '.join(str(e) for e in new_user_preference[:int((len(new_user_preference)/10)*9)])
    test_user_preference = ' '.join(str(e) for e in new_user_preference[(int(len(new_user_preference)/10)*9):])


    if(not exist_flag): #기존에 존재하지 않는 새로운 유저일 경우 -> 그 유저와 선호 리스트 추가

        #print('새로운 유저 추가')

        if(len(new_user_preference)<10):

            with open(train_file_path, 'a') as file:
                file.write(f"{new_key} {all_train_user_preference}\n")

        else:

            with open(train_file_path, 'a') as file:
                file.write(f"{new_key} {train_user_preference}\n")

            with open(test_file_path, 'a') as file:
                file.write(f"{new_key} {test_user_preference}\n")
            

    else: #기존에 존재하는 유저일 경우 -> 그 유저의 선호 리스트를 갱신

        #print('유저가 이미 존재')

        if(len(new_user_preference)<10):
            
            with open(train_file_path, 'r') as file:
                
                temp_file_path = '/opt/ml/Recipe_Project/Recipe_code/ultragcn/train_temp.txt'

                with open(temp_file_path, 'w') as temp_file:
                    for line in file:
                        parts = line.strip().split(' ')
                        key = int(parts[0])
                        
                        if user_label_mapping[key] == new_user_name_number:
                            line = f"{key} {all_train_user_preference}\n"
                            
                        temp_file.write(line)

                shutil.move(temp_file_path, train_file_path)
            
            with open(test_file_path, 'r') as file:
                
                temp_file_path = '/opt/ml/Recipe_Project/Recipe_code/ultragcn/test_temp.txt'

                with open(temp_file_path, 'w') as temp_file:
                    for line in file:
                        parts = line.strip().split(' ')
                        key = int(parts[0])
                        
                        if user_label_mapping[key] == new_user_name_number:
                            line = ''
                            
                        temp_file.write(line)

                shutil.move(temp_file_path, test_file_path)

        else:

            with open(train_file_path, 'r') as file:
                temp_file_path = '/opt/ml/Recipe_Project/Recipe_code/ultragcn/train_temp.txt'

                with open(temp_file_path, 'w') as temp_file:
                    for line in file:
                        parts = line.strip().split(' ')
                        key = int(parts[0])
                        
                        if user_label_mapping[key] == new_user_name_number:
                            line = f"{key} {train_user_preference}\n"
                            
                        temp_file.write(line)

                shutil.move(temp_file_path, train_file_path)


            with open(test_file_path, 'r') as file:

                temp_file_path = '/opt/ml/Recipe_Project/Recipe_code/ultragcn/test_temp.txt'

                first_elements = [int(line.split()[0]) for line in file]

                file.seek(0)
        
                #유저가 이미 존재하므로 무조건 값이 있음.
                user_key = next(key for key, value in user_label_mapping.items() if value == new_user_name_number)

                if(user_key in first_elements):
                    
                    with open(temp_file_path, 'w') as temp_file:
                        for line in file:
                            parts = line.strip().split(' ')
                            key = int(parts[0])

                            if user_label_mapping[key] == new_user_name_number:
                                line = f"{key} {test_user_preference}\n"

                            temp_file.write(line)

                else:
                    
                    t_flag = True 
                    with open(temp_file_path, 'w') as temp_file:
                        for line in file:
            
                            parts = line.strip().split(' ')
                            key = int(parts[0])
                            
                            if (t_flag & (key >= user_key)):
                                temp_file.write(f"{user_key} {test_user_preference}\n")
                                t_flag = False
                            
                            temp_file.write(line)
                    
                        if(t_flag):
                             temp_file.write(f"{user_key} {test_user_preference}\n")

                shutil.move(temp_file_path, test_file_path)


# 모델 학습 시키는 코드
def recsys_train_by_ultragcn(config_file):

    params, constraint_mat, ii_constraint_mat, ii_neighbor_mat, train_loader, test_loader, mask, test_ground_truth_list, interacted_items = data_param_prepare(config_file)
    
    ultragcn = UltraGCN(params, constraint_mat, ii_constraint_mat, ii_neighbor_mat)
    ultragcn = ultragcn.to(params['device'])
    optimizer = torch.optim.Adam(ultragcn.parameters(), lr=params['lr'])

    train(ultragcn, optimizer, train_loader, test_loader, mask, test_ground_truth_list, interacted_items, params)


#유저 고유 번호를 받고 그 유저의 추천 목록 반환
def recsys_get_recipe_by_ultragcn(user_name_number : int) -> list:

    #환경에 따라 수정 필요.
    file_path = '/opt/ml/Recipe_Project/Recipe_code/ultragcn/RecSys_Result_UltraGCN.txt'
    User_LM_path = '/opt/ml/Recipe_Project/Recipe_code/ultragcn/Userid_label_encoder.pickle'
    Recipe_LE_path = '/opt/ml/Recipe_Project/Recipe_code/ultragcn/Recipeid_label_encoder.pkl'

    with open(User_LM_path, 'rb') as file:
        user_label_mapping = pickle.load(file)
    recipe_LE = joblib.load(Recipe_LE_path)
    
    user_name_number = next(key for key, value in user_label_mapping.items() if value == user_name_number)

    values = []

    with open(file_path, 'r') as file:
        for line in file:
            parts = line.split()
            if int(parts[0]) == user_name_number:
                values = [int(value) for value in parts[1:]]
                break

    return recipe_LE.inverse_transform(values)

# 단일 실행 시 단순 학습.
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_file', type=str, help='config file path')
    args = parser.parse_args()

    print('###################### UltraGCN ######################')

    print('Loading Configuration...')
    params, constraint_mat, ii_constraint_mat, ii_neighbor_mat, train_loader, test_loader, mask, test_ground_truth_list, interacted_items = data_param_prepare(args.config_file)
    
    print('Load Configuration OK, show them below')
    print('Configuration:')
    print(params)

    ultragcn = UltraGCN(params, constraint_mat, ii_constraint_mat, ii_neighbor_mat)
    ultragcn = ultragcn.to(params['device'])
    optimizer = torch.optim.Adam(ultragcn.parameters(), lr=params['lr'])

    #주석은 API 테스트
    #user_num = recsys_add_user_by_ultragcn([2234,5453,12232,8753,22342])
    #print(user_num)
    train(ultragcn, optimizer, train_loader, test_loader, mask, test_ground_truth_list, interacted_items, params)
    #result = recsys_get_recipe_by_ultragcn(user_num)
    #print(result)
    

    print('END')