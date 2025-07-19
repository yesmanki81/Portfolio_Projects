# coding: utf-8
import pymysql, pickle
import pandas as pd
from sqlalchemy import create_engine
from collections import Counter
import numpy as np
import pandas as pd

from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold



def main():

    train = load_data()
    train = filtered_top_50_brand_process(train)
    y_train, X_train = normalized_process(train)
    X_train1, X_test1, y_train1, y_test1 = train_test_split_process(y_train, X_train)
    X_train1, ml = build_XGBRegressor_model(X_train1, X_test1, y_train1)
    test(X_train1, ml)



def load_data():

    # Read Password
    pw = pickle.load(open('./Flask/models/pw.plk', 'rb'))

    # AWS MySql Connection Info
    db = pymysql.connect(
        host = "cars.c3d1kxjihbmh.us-east-1.rds.amazonaws.com",
        user = "root",
        password = pw,
        db = "cars",
        charset='utf8',
    )

    SQL_QUERY = """
        SELECT *
        FROM used_car;
    """

    train = pd.read_sql(SQL_QUERY, db)
    pickle.dump(train, open("./Flask/models/database.plk", "wb"))

    return train

def filtered_top_50_brand_process(train):
    brand_list = []
    for brand in Counter(train.brand).most_common(50):
        brand_list.append(brand[0])

    idx_list = []
    idx = 0
    for i in train["brand"]:
        if i not in brand_list:
            idx_list.append(idx)
        idx += 1

    train = train.drop(idx_list)
    train.reset_index(drop=True, inplace=True)
    train = train.drop("index", axis=1)

    actual_car_info = train[["brand", "model", "year", "miles", "price"]]
    pickle.dump(actual_car_info, open("./Flask/models/actual_car_info.plk", "wb"))

    return train


def normalized_process(train):

    categorical_features = ['brand', 'model', 'deal']

    dummy_cat = pd.get_dummies(train[categorical_features])

    numerical_features = ['year', 'miles', 'price']

    normalize_num = np.log1p(train[numerical_features])

    X_train_0 = normalize_num.join(dummy_cat)
    y_train = X_train_0["price"]
    X_train = X_train_0.drop("price", axis=1)

    return y_train, X_train

def train_test_split_process(y_train, X_train):
    k_fold = KFold(n_splits=10, shuffle=True, random_state=2022)
    X_train1, X_test1, y_train1, y_test1 = train_test_split(X_train, y_train)

    return X_train1, X_test1, y_train1, y_test1


def build_XGBRegressor_model(X_train1, X_test1, y_train1):

    ml = XGBRegressor(n_estimators=1000, learning_rate=0.05, verbose=False)

    ml = ml.fit(X_train1, y_train1)
    pickle.dump(ml, open("./Flask/models/model.plk", "wb"))

    y_pred = ml.predict(X_test1)
    target = pd.DataFrame(columns=[X_train1.columns])
    pickle.dump(X_train1.columns, open("./Flask/models/column.plk", "wb"))

    return X_train1, ml

def test(X_train1, ml):

    brand = 'FORD'
    model = 'F-150'
    year = 2019
    miles = 40000

    target = pd.DataFrame(columns=[X_train1.columns])

    brand_index = 0
    for col in X_train1.columns:
        if col == 'brand' + "_" + brand:
            break;
        brand_index += 1

    # Check the index location of the selected used car model in the variable column data frame
    model_index = 0
    for col in X_train1.columns:
        if col == 'model' + "_" + model:
            break;
        model_index += 1

    # Array of zeros
    target_list = np.zeros_like(X_train1.loc[0])

    # Save the target_list to pickle file
    pickle.dump(target_list, open("./Flask/models/target_list.plk", "wb"))


    # Put the number 1 in the selected brand and model locations in the data frame
    target_list[brand_index] = 1
    target_list[model_index] = 1

    # Put the year and miles in the data frame
    target_list[0] = year
    target_list[1] = miles

    # Insert data into target data frame
    for i in range(1):
        target.loc[i] = target_list


    # Nomalizing numerical features
    numerical_features = ['year', 'miles']
    normalize_target = np.log1p(target[numerical_features])
    target.drop(['year', 'miles'], axis=1, inplace=True)
    target_goal = normalize_target.join(target)

    # Predicted logged price
    price_log = ml.predict(target_goal)

    # Revert the logged price back to its original price
    price = np.exp(price_log)
    print("Price:", int(price))

if __name__=="__main__":
    main()























