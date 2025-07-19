import pandas as pd
import numpy as np
import pymysql, pickle
from collections import Counter

from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from warnings import filterwarnings

filterwarnings("ignore", category=UserWarning)


def main():
    train = load_data()
    train = remove_duplicated(train)
    train = filtered_top_40_brand_process(train)
    y_train, X_train = normalized_process(train)
    
    X_train1, X_test1, y_train1, y_test1 = train_test_split_process(y_train, X_train)
    ml = build_XGBRegressor_model(X_train1, y_train1)
    
    test(X_train1, ml)


def load_data():

    # Read Password
    pw = pickle.load(open('./Flask/pickle/pw.pkl', 'rb'))
    host_ = pickle.load(open('./Flask/pickle/host.pkl', 'rb')) 
    
    # AWS MySql Connection Info
    db = pymysql.connect(
        host = host_,
        user = "root",
        password = pw,
        db = "usedcar",
        charset='utf8',
    )

    SQL_QUERY = """
        SELECT *
        FROM usedcar;
    """

    train = pd.read_sql(SQL_QUERY, db)
    pickle.dump(train, open("./Flask/pickle/database.pkl", "wb"))
    
    return train


def remove_duplicated(train):
    train = train.drop_duplicates(['ID'])
    
    return train
    

def filtered_top_40_brand_process(train):
    # Top 40 car brands
    brand_list = []
    for brand in Counter(train.Brand).most_common(40):
        brand_list.append(brand[0])
    
    # Check the index of data not included in the top 40 car brands
    idx_list = []
    idx = 0
    for brand in train["Brand"]:
        if brand not in brand_list:
            # print(f"Brands that are not among the 40 most popular brands : {brand}")
            idx_list.append(idx)
        idx += 1
    
    # Only the top 40 car brands are filtered
    train = train.drop(idx_list)
    train.reset_index(drop=True, inplace=True)
    
    # Drop the index
    train = train.drop("index", axis=1)

    actual_car_info = train[["Brand", "Model", "Year", "Mileage", "Price"]]
    pickle.dump(actual_car_info, open("./Flask/pickle/actual_car_info.pkl", "wb"))

    return train


def normalized_process(train):

    # Select models and brands as category variables
    categorical_features = ['Brand', 'Model', 'Bodystyle', 'Exterior Color', 'Interior Color', 'Drivetrain',\
                                'MPG','Fuel Type', 'Transmission','Engine']

    # Dummy category variable
    dummy_cat = pd.get_dummies(train[categorical_features])

    # Select by numeric variable
    numerical_features = ['Year', 'Mileage', 'Price']

    normalize_num = np.log1p(train[numerical_features])

    # Join numeric variable with categoric variable
    X_train_0 = normalize_num.join(dummy_cat)
    
    # Seperate price as y value
    y_train = X_train_0["Price"]
    X_train = X_train_0.drop("Price", axis=1)

    return y_train, X_train



def train_test_split_process(y_train, X_train):
    k_fold = KFold(n_splits=10, shuffle=True, random_state=2024)
    X_train1, X_test1, y_train1, y_test1 = train_test_split(X_train, y_train)

    return X_train1, X_test1, y_train1, y_test1


def build_XGBRegressor_model(X_train1, y_train1):

    ml = XGBRegressor(n_estimators=1000, learning_rate=0.05, verbose=False)
    
    # Train model
    ml = ml.fit(X_train1, y_train1, verbose=False)
    pickle.dump(ml, open("./Flask/pickle/model.pkl", "wb"))
    pickle.dump(X_train1.columns, open("./Flask/pickle/column.pkl", "wb"))

    return ml


def test(X_train1, ml):

    brand = 'honda'
    model = 'accord'
    year = int(2010)
    mileage = int(150000)
    
    target = pd.DataFrame(columns=[X_train1.columns])

    brand_index = 0
    for col in X_train1.columns:
        if col == 'Brand' + "_" + brand:
            break;
        brand_index += 1

    # Check the index location of the selected used car model in the variable column data frame
    model_index = 0
    for col in X_train1.columns:
        if col == 'Model' + "_" + model:
            break;
        model_index += 1

    # Array of zeros
    target_list = np.zeros_like(X_train1.iloc[0])

    # Save the target_list to pickle file
    pickle.dump(target_list, open("./Flask/pickle/target_list.pkl", "wb"))

    # Put the number 1 in the selected brand and model locations in the data frame
    target_list[brand_index] = 1
    target_list[model_index] = 1

    # Put the year and miles in the data frame
    target_list[0] = year
    target_list[1] = mileage

    # Convert all elements in target_list with 0 being False and 1 being True
    transformed_values = [True if x == 1 else False for x in target_list[2:]]
    target_list = [target_list[0], target_list[1]] + transformed_values
    
    # Insert data into target data frame
    for i in range(1):
        target.loc[i] = target_list

    numerical_features = ['Year', 'Mileage']

    # Convert the values ​​in the Year and Mileage columns to float form and apply the log1p function
    normalize_target = target[numerical_features].astype(float).apply(np.log1p)

    # After deleting the Year and Mileage columns, combine them with the normalize_target dataframe to create target_goal.
    target.drop(['Year', 'Mileage'], axis=1, level=0, inplace=True)
    target_goal = normalize_target.join(target)
        

    # Predicted logged price
    price_log = ml.predict(target_goal)

    # Revert the logged price back to its estimated price
    price = np.exp(price_log)
    print(f"Brand : {brand.upper()}")
    print(f"Model : {model.upper()}")
    print(f"Year  : {year}")
    print(f"Estimated Price : ${int(price)}")


if __name__=="__main__":
    main()