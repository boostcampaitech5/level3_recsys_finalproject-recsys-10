import os
import torch
import yaml
# import time


from transformers import AutoModelForSequenceClassification
from KobertTokenizer.tokenization_kobert import BertTokenizer

def recbert_run(input_chunk: str) -> tuple:
    with open(os.path.join(os.getcwd(), 'data/category_dict.yaml'), 'r') as f:
        category_data = yaml.safe_load(f)
    cat1, cat2, cat3, cat4 = category_data['cat1'], category_data['cat2'], category_data['cat3'], category_data['cat4']

    DEVICE = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    BASE_DIR = os.getcwd()
    tokenizer_path = os.path.join(BASE_DIR, 'KobertTokenizer')
    cat1_model_path = os.path.join(BASE_DIR, 'model/cat1_model_directory')
    cat2_model_path = os.path.join(BASE_DIR, 'model/cat2_model_directory')
    cat3_model_path = os.path.join(BASE_DIR, 'model/cat3_model_directory')
    cat4_model_path = os.path.join(BASE_DIR, 'model/cat4_model_directory')

    tokenizer = BertTokenizer.from_pretrained(tokenizer_path, model_max_length=512, is_fast=False, local_files_only=True)

    # nlp 모델 로드 시간 측정
    # start_time = time.time()

    models = []
    model_paths = [cat1_model_path, cat2_model_path, cat3_model_path, cat4_model_path]
    num_labels = [len(cat1), len(cat2), len(cat3), len(cat4)]
    for model_path, num_label in zip(model_paths, num_labels):
        model = AutoModelForSequenceClassification.from_pretrained(model_path, num_labels=num_label, local_files_only=True).to(DEVICE)
        models.append(model)


    # print(f"nlp model load: {round(time.time() - start_time, 2)}s")


    output = []
    inputs = tokenizer(input_chunk, padding='max_length', truncation=True, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        for model in models:
            logits = model(**inputs).logits
            pred = torch.argmax(torch.nn.Softmax(dim=1)(logits), dim=1).cpu().item()
            output.append(pred)
    # print(f"입력 값: {input_chunk}")
    # print(f"[방법: {list(cat1.values())[output[0]]}, 상황: {list(cat2.values())[output[1]]}, 재료: {list(cat3.values())[output[2]]}, 종류: {list(cat4.values())[output[3]]}]")
    return tuple(output)


if __name__ == "__main__":
    print(recbert_run("술과 함께 먹기 좋은 음식"))
    # output
    # nlp model load: 6.45s
    # 입력 값: 술과 함께 먹기 좋은 음식
    # [방법: 튀김, 상황: 술안주, 재료: 기타, 종류: 기타]
    # (4, 6, 9, 10)