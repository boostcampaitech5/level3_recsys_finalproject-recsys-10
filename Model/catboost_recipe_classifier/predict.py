import os
import yaml
import catboost as cb
import pandas as pd
import numpy as np
from pandas import DataFrame
from typing import List

from train import load_data, split_data

# Load the configuration
with open("config.yaml", 'r') as stream:
    config = yaml.safe_load(stream)

TRAIN_DATA_PATH = os.path.join(config['data_dir'], config['train_data_file'])
MODEL_LOAD_PATH = os.path.join(config['model_dir'], config['model_save_file'])
TOP_K = config['top_k']

def load_model(model_path: str) -> cb.CatBoostClassifier:
    """
    Load the CatBoost model from the specified file.

    Parameters:
    model_path (str): The path to the model file.

    Returns:
    loaded_model (CatBoostClassifier): The loaded model.
    """
    loaded_model = cb.CatBoostClassifier()
    loaded_model.load_model(model_path)
    return loaded_model

def predict_proba(model: cb.CatBoostClassifier, X_test: DataFrame) -> DataFrame:
    """
    Predict the probabilities of each class using the model.

    Parameters:
    model (CatBoostClassifier): The trained model.
    X_test (DataFrame): The testing data.

    Returns:
    probabilities (DataFrame): The predicted probabilities for each class.
    """
    probabilities = model.predict_proba(X_test)
    return probabilities

def get_top_k_classes(probabilities: DataFrame, k: int) -> List[List[int]]:
    """
    Get the top k classes for each instance based on the predicted probabilities.

    Parameters:
    probabilities (DataFrame): The predicted probabilities for each class.
    k (int): The number of top classes to return.

    Returns:
    top_k_classes (List[List[int]]): The top k classes for each instance.
    """
    top_k_classes = probabilities.argsort(axis=1)[:, -k:].tolist()
    return top_k_classes

def map_labels(classes: list, top_k_classes: list) -> list:
    """
    Maps the top k class indices to their corresponding labels.

    Parameters:
    classes (list): The class labels in the order they were trained on.
    top_k_classes (list): The top k classes predicted by the model.

    Returns:
    result (list): The top k classes mapped to their original labels.
    """
    # Create a mapping from index to class label
    label_mapping = {idx: label for idx, label in enumerate(classes)}

    # Map the top k classes to their original labels
    result = [label_mapping[label] for label in top_k_classes]

    return result

## main predict code
def predict_main(input_list: list) -> list[int]:
    """
    The predict_main function to tie all the steps together.

    Parameters:
    input_list (list): The user input data for which predictions are to be made.

    Returns:
    top_k_classes (list[int]): The top k classes predicted by the model.
    """
    # Load the trained model
    loaded_model = load_model(MODEL_LOAD_PATH)
    
    # Convert the input list to a numpy array for further processing
    input_list = np.array(input_list)
    
    # If the maximum value in the input list is greater than 1,
    # normalize all values in the list to be within the range [0,1] by dividing by the maximum value
    # This is to ensure the input data is on the same scale as the data the model was trained on
    if np.max(input_list) > 1:
        input_list = input_list / np.max(input_list)

    # Round the values in the input list to 2 decimal places
    input_list = np.round(input_list, decimals=2)

    # Get the predicted probabilities for each class from the model
    probabilities = loaded_model.predict_proba(loaded_model, input_list)

    # Get the top k classes based on the predicted probabilities
    top_k_classes = get_top_k_classes(probabilities, TOP_K)

    # Map the top k classes to their original labels
    top_k_classes = map_labels(loaded_model.classes_, top_k_classes)

    # Return the top k classes
    return top_k_classes


## test code
def _main() -> None:
    """
    The main function to tie all the steps together.
    """
    # Load model
    loaded_model = load_model(MODEL_LOAD_PATH)

    # Load data
    X, y = load_data(TRAIN_DATA_PATH)
    # Split data
    X_train, X_test, y_train, y_test = split_data(X, y)
    
    # Predict probabilities
    probabilities = predict_proba(loaded_model, X_test)

    # Get top k classes
    top_k_classes = get_top_k_classes(probabilities, TOP_K)

    print_k = 10
    # Print the first 10 instances
    for index, i in enumerate(top_k_classes):
        print(index, i)
        if index == print_k:
            break

if __name__ == "__main__":
    _main()
