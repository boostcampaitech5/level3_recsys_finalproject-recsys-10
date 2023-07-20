import os
import random
import numpy as np
import pandas as pd
import re
import pickle
import yaml
import torch
import evaluate

from torch.utils.data import Dataset
from transformers import AutoModelForSequenceClassification
from transformers import DataCollatorWithPadding
from transformers import TrainingArguments, Trainer
from sklearn.model_selection import train_test_split
from KobertTokenizer.tokenization_kobert import KoBertTokenizer

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)

DEVICE = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

# DEVICE
BASE_DIR = os.getcwd()
DATA_DIR = os.path.join(BASE_DIR, '../data')
OUTPUT_DIR = os.path.join(BASE_DIR, '../output')

# catedata load
with open('data/category_dict.yaml', 'r', encoding='utf-8') as file:
    categories = yaml.safe_load(file)
cat1 = {int(key): value for key, value in categories['cat1'].items()}
cat2 = {int(key): value for key, value in categories['cat2'].items()}
cat3 = {int(key): value for key, value in categories['cat3'].items()}
cat4 = {int(key): value for key, value in categories['cat4'].items()}


for cat_name, cat_len in zip(['cat4','cat2','cat1','cat3'],[17, 14, 14, 16]):
    model_name = 'monologg/kobert' 
    tokenizer = KoBertTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=cat_len).to(DEVICE)

    data = pd.read_csv(os.path.join(DATA_DIR, 'cate_data.csv'))
    data = data[['name',cat_name]]
    data = data.dropna(subset=['name'])
    data['name'] = data['name'].apply(lambda x: re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣\s]', '', x))

    # 데이터셋의 'cat' 열의 고유한 값들을 확인합니다
    unique_cat_values = data[cat_name].unique()
    # 새로운 값을 할당할 딕셔너리를 생성합니다
    cat_mapping = {value: index for index, value in enumerate(unique_cat_values)}
    # 딕셔너리를 피클로 저장
    with open(cat_name+'dictionary.pkl', 'wb') as f:
        pickle.dump(cat_mapping, f)

    # 데이터셋의 'cat' 열을 새로운 값으로 매핑하여 업데이트합니다
    data[cat_name] = data[cat_name].map(cat_mapping)

    # 'cat' 값을 기준으로 데이터를 그룹화
    grouped_dataset = data.groupby(cat_name)

    # 그룹별로 테스트 데이터셋 분리
    train_datasets = []
    test_datasets = []
    for group_name, group_data in grouped_dataset:
        train_data, test_data = train_test_split(group_data, test_size=0.3, random_state=SEED)
        train_datasets.append(train_data)
        test_datasets.append(test_data)

    # 테스트 데이터셋 병합
    dataset_train = pd.concat(train_datasets)
    dataset_valid = pd.concat(test_datasets)


    class BERTDataset(Dataset):
        def __init__(self, data, tokenizer):
            input_texts = data['name']
            targets = data[cat_name]
            self.inputs = []; self.labels = []
            for text, label in zip(input_texts, targets):
                tokenized_input = tokenizer(text, padding='max_length', truncation=True, return_tensors='pt')
                self.inputs.append(tokenized_input)
                self.labels.append(torch.tensor(label))
        
        def __getitem__(self, idx):
            return {
                'input_ids': self.inputs[idx]['input_ids'].squeeze(0),  
                'attention_mask': self.inputs[idx]['attention_mask'].squeeze(0),
                'labels': self.labels[idx].squeeze(0)
            }
        
        def __len__(self):
            return len(self.labels)
        
    data_train = BERTDataset(dataset_train, tokenizer)
    data_valid = BERTDataset(dataset_valid, tokenizer)

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    f1 = evaluate.load('f1')
    def compute_metrics(eval_pred):
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        return f1.compute(predictions=predictions, references=labels, average='macro')

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        overwrite_output_dir=True,
        do_train=True,
        do_eval=True,
        do_predict=True,
        logging_strategy='steps',
        evaluation_strategy='steps',
        save_strategy='steps',
        logging_steps=100,
        eval_steps=100,
        save_steps=100,
        save_total_limit=2,
        learning_rate= 2e-05,
        adam_beta1 = 0.9,
        adam_beta2 = 0.999,
        adam_epsilon=1e-08,
        weight_decay=0.01,
        lr_scheduler_type='linear',
        per_device_train_batch_size=32,
        per_device_eval_batch_size=32,
        num_train_epochs=2,
        load_best_model_at_end=True,
        metric_for_best_model='eval_f1',
        greater_is_better=True,
        seed=SEED
    )


    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=data_train,
        eval_dataset=data_valid,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )
    trainer.train()

    # 학습이 완료된 후 모델 저장
    trainer.model.save_pretrained(cat_name+"_model_directory")

    # torch.save(model, cat_name+'_model.pt')  # 전체 모델 저장
    # torch.save(model.state_dict(), cat_name+'_model_state_dict.pt')