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

### Metrics
> 1. For each prediction in the "top k list":  
>       - If the target is in the "top k list", increment "Correct Predictions" by 1.  
>       - If the target is not in the "top k list", increment "Incorrect Predictions" by 1.
>
> 2. Accuracy Formula:
> $$\text{Accuracy} = \frac{\text{Correct Predictions}}{\text{Correct Predictions + Incorrect Predictions}} \times 100$$


### Columns Explanation:
> - **Top K:** The number of top predictions considered in the evaluation.
> - **Output Unique:** The number of unique outputs produced by the model.
> - **Origin Unique:** The number of classes in the model.
> - **Correct Predictions:** The number of predictions that match the ground truth (correct predictions).
> - **Incorrect Predictions:** The number of predictions that do not match the ground truth (incorrect predictions).
> - **Accuracy:** The percentage of correct predictions over the total number of predictions for each "Top K" scenario.
> - **% Change in Accuracy:** The percentage change in accuracy compared to the previous "Top K" scenario, indicating the model's performance improvement with more predictions considered.


### \- Top 1 ~ 5
| Top K | Output Unique | Origin Unique | Correct Predictions | Incorrect Predictions | Accuracy | % Change in Accuracy |
|-------|---------------|---------------|--------------------|----------------------|----------|---------------------|
| 1     | 1336          | 2361          | 1919               | 16637                | 10.34%   | -                   |
| 2     | 1693          | 2361          | 2922               | 15634                | 15.75%   | +5.41%              |
| 3     | 1885          | 2361          | 3662               | 14894                | 19.73%   | +3.98%              |
| 4     | 2000          | 2361          | 4207               | 14349                | 22.67%   | +2.94%              |
| 5     | 2096          | 2361          | 4687               | 13869                | 25.26%   | +2.59%              |

### \- Top 1 ~ 200
| Top K | Output Unique | Origin Unique | Correct Predictions | Incorrect Predictions | Accuracy | % Change in Accuracy |
|-------|---------------|---------------|--------------------|----------------------|----------|---------------------|
| 1     | 1336          | 2361          | 1919               | 16637                | 10.34%   | -                   |
| 5     | 2096          | 2361          | 4687               | 13869                | 25.26%   | +14.92%             |
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

