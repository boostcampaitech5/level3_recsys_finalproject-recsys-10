"""
    CatBoostClassifier

    Goal:
    To recommend recipes based on a user's past interactions with categories.

    Dataset:
    userdata + recipeid -> userdata + category data [one hot]

    Train Dataset example:
    recipeid,   0,   1,   2,   3, ... ,  55,  56,  57,  58,  59,  60
    6885928,  0.0, 0.0, 0.0, 0.0, ... , 1.0, 0.0, 0.0, 0.0, 0.0, 0.0
    6892249,  0.0, 0.0, 0.0, 0.5, ... , 0.5, 0.0, 0.0, 0.0, 0.0, 0.0
"""

import os
import yaml
import catboost as cb
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from pandas import DataFrame, Series
from numpy import ndarray
from typing import Tuple


# Load the configuration
with open("config.yaml", 'r') as stream:
    config = yaml.safe_load(stream)

# Get the file paths from the configuration
TRAIN_DATA_PATH = os.path.join(config['data_dir'], config['train_data_file'])
MODEL_SAVE_PATH = os.path.join(config['model_dir'], config['model_save_file'])


def load_data(file_path: str) -> Tuple(DataFrame, Series):
    """
    Load the dataset from a csv file.

    Parameters:
    file_path (str): The file path of the dataset.

    Returns:
    X (DataFrame): The input features.
    y (Series): The target variable.
    """
    df_grouped = pd.read_csv(file_path)
    X = df_grouped.drop("recipeid", axis=1)
    y = df_grouped["recipeid"]
    return X, y

def split_data(X: DataFrame, y: Series, test_size: float=0.2, random_state: int=42) -> Tuple(DataFrame, DataFrame, Series, Series):
    """
    Split the dataset into training and testing sets.

    Parameters:
    X (DataFrame): The input features.
    y (Series): The target variable.
    test_size (float): The proportion of the dataset to include in the test split.
    random_state (int): The seed used by the random number generator.

    Returns:
    X_train, X_test, y_train, y_test (DataFrame, DataFrame, Series, Series): The splitted data.
    """
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
    return X_train, X_test, y_train, y_test

def train_model(X_train: DataFrame, y_train: Series, X_test: DataFrame, y_test: Series, early_stop_rounds: int=20) -> cb.CatBoostClassifier:
    """
    Train the CatBoost classifier.

    Parameters:
    X_train, X_test, y_train, y_test (DataFrame, DataFrame, Series, Series): The training and testing data.
    early_stop_rounds (int): The number of rounds to use for early stopping.

    Returns:
    model (CatBoostClassifier): The trained model.
    """
    # Load the CatBoost parameters from the configuration
    catboost_params = config['catboost_params']

    model = cb.CatBoostClassifier(**catboost_params)
    model.fit(X_train, y_train,
              eval_set=(X_test, y_test),
              early_stopping_rounds=early_stop_rounds,
              use_best_model=True)
    return model

def save_model(model: cb.CatBoostClassifier, model_path: str) -> None:
    """
    Save the trained model.

    Parameters:
    model (CatBoostClassifier): The trained model.
    model_path (str): The path to save the model.
    """
    model.save_model(model_path)

def predict(model: cb.CatBoostClassifier, X_test: DataFrame) -> ndarray:
    """
    Predict the target variable using the trained model.

    Parameters:
    model (CatBoostClassifier): The trained model.
    X_test (DataFrame): The testing data.

    Returns:
    y_pred (array): The predicted values.
    """
    y_pred = model.predict(X_test)
    return y_pred

def evaluate_model(y_test: Series, y_pred: ndarray) -> float:
    """
    Evaluate the performance of the model.

    Parameters:
    y_test (Series): The true values.
    y_pred (array): The predicted values.

    Returns:
    accuracy (float): The accuracy score of the model.
    """
    accuracy = accuracy_score(y_test, y_pred)
    return accuracy

def main() -> None:
    """
    The main function to tie all the steps together.
    """
    # Load data
    X, y = load_data(TRAIN_DATA_PATH)

    # Split data
    X_train, X_test, y_train, y_test = split_data(X, y)

    # Train model
    model = train_model(X_train, y_train, X_test, y_test)

    # Save model
    save_model(model, MODEL_SAVE_PATH)

    # Predict
    y_pred = predict(model, X_test)

    # Evaluate
    accuracy = evaluate_model(y_test, y_pred)
    print("Accuracy:", accuracy)

if __name__ == "__main__":
    main()