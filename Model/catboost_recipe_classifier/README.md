# CatBoost_recipe_classifier

> 유저의 레시피 상호작용 데이터의 레시피 카테고리 기반으로 레시피 K개 추천 

## - Directory

```
.
|-- README.md
|-- config.yaml
|-- notebook
|   |-- catboost_test_prototype.ipynb
|   `-- eda.ipynb
|-- predict.py
|-- requirements.txt
`-- train.py
```

## - Run

> \- train  
> `> python train.py`
>
> \- test  
> `> python predict.py`
>
> \- use predict [for serving]  
> ```python
> from predict import predict_main
>
> ...
> predict_main(input_list: list)
> ...
>
> ```
>

## - requirements
```
catboost
pandas
scikit-learn
numpy
PyYAML
```


## Evaluation Results

| Top K | Output Unique | Origin Unique | Correct Predictions | Incorrect Predictions | Accuracy | % Change in Accuracy |
|-------|---------------|---------------|--------------------|----------------------|----------|---------------------|
| 5     | 2096          | 2361          | 4687               | 13869                | 25.26%   | -                   |
| 10    | 2280          | 2361          | 6318               | 12238                | 34.05%   | +8.79%              |
| 15    | 2326          | 2361          | 7389               | 11167                | 39.82%   | +5.77%              |
| 20    | 2346          | 2361          | 8229               | 10327                | 44.35%   | +4.53%              |
| 25    | 2351          | 2361          | 8896               | 9660                 | 47.94%   | +3.59%              |
| 30    | 2356          | 2361          | 9441               | 9115                 | 50.88%   | +2.94%              |
| 35    | 2358          | 2361          | 9862               | 8694                 | 53.15%   | +2.27%              |
| 40    | 2360          | 2361          | 10245              | 8311                 | 55.21%   | +2.06%              |
| 45    | 2360          | 2361          | 10588              | 7968                 | 57.06%   | +1.85%              |
| 50    | 2361          | 2361          | 10919              | 7637                 | 58.84%   | +1.78%              |
| 100   | 2361          | 2361          | 12988              | 5568                 | 69.99%   | -                   |
| 200   | 2361          | 2361          | 14805              | 3751                 | 79.79%   | -                   |

