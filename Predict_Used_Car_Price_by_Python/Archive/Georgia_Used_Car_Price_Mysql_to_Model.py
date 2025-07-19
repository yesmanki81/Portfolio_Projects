
# coding: utf-8

import MySQLdb, pickle
import pandas as pd
from sqlalchemy import create_engine
from collections import Counter
import numpy as np
import pandas as pd

# read local car_info popular
pw = pickle.load(open('./Flask//models/pw.plk','rb'))

db = MySQLdb.connect(
    "ec2-3-133-82-223.us-east-2.compute.amazonaws.com",
    "root",
    pw,
    "car",
    charset='utf8',
)

SQL_QUERY = """
    SELECT *
    FROM car;
"""

train = pd.read_sql(SQL_QUERY, db)

pickle.dump(train, open("./Flask//models/database.plk","wb"))

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


categorical_features = ['brand', 'model']

dummy_cat = pd.get_dummies(train[categorical_features])

numerical_features = ['year', 'miles','price']

normalize_num = np.log1p(train[numerical_features])

# pre_train = pd.merge(normalize_num, dummy_cat)
X_train_0 = normalize_num.join(dummy_cat)
y_train = X_train_0["price"]
X_train = X_train_0.drop("price", axis=1)

from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold

k_fold = KFold(n_splits=10, shuffle=True, random_state=2020)
X_train1, X_test1, y_train1, y_test1 = train_test_split(X_train, y_train)

ml = XGBRegressor(n_estimators=1000, learning_rate=0.05, verbose=False)

ml = ml.fit(X_train1, y_train1)
y_pred = ml.predict(X_test1)

pickle.dump(ml, open("./Flask/models/model.plk","wb"))

actual_car_info = train[["brand", "model","year","miles","price"]]
pickle.dump(actual_car_info, open("./Flask/models/actual_car_info.plk","wb"))

target = pd.DataFrame(columns = [X_train1.columns])

pickle.dump(X_train1.columns, open("./Flask/models/column.plk","wb"))
