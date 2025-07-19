from flask import Flask,render_template, request, jsonify
import pickle
import numpy as np
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


app = Flask(__name__)
app.config.update(
    TEMPLATES_AUTO_RELOAD = True,
)
# model
# model = model.fit(X_train1, y_train1)
def init():
    with open("./pickle/model.pkl","rb") as f:
        global ml
        ml = pickle.load(f)

# Train 데이터의 컬럼이름들 (dummy 컬럼 + 숫자 컬럼 이름)
# columns = pd.DataFrame(columns = [X_train1.columns])
def columns():
    with open("./pickle/column.pkl","rb") as c:
        global columns
        columns = pickle.load(c)

# target_list = np.zeros_like(X_train.loc[0])
def target_list():
    with open("./pickle/target_list.pkl","rb") as t:
        global target_list
        target_list = pickle.load(t)

def actual_car_info():
    with open("./pickle/actual_car_info.pkl","rb") as a:
        global actual_car_info
        actual_car_info = pickle.load(a)

def database():
    with open("./pickle/database.pkl","rb") as d:
        global database
        database = pickle.load(d)

init()
columns()
target_list()
actual_car_info()
database()

brand_group = list(set(database["Brand"]))
model_group = list(set(database["Model"]))

@app.route("/")
def index():
    return render_template("index.html")

# API
@app.route("/predict/" , methods=["POST"])
def predict():
    global target_list, actual_car_info, database, columns, ml
    target = pd.DataFrame(columns = columns)

    brand = request.values.get("brand")
    model = request.values.get("model")
    year = request.values.get("year")
    mileage = request.values.get("mileage")

    brand = str(brand).lower()
    model = str(model).lower()
    year = int(year)
    mileage = int(mileage)
    
    cdx = 0
    for col in columns:
        if col == 'Brand'+"_"+brand:
            break;
        cdx += 1

    sdx = 0
    for col in columns:
        if col == 'Model'+"_"+model:
            break;
        sdx += 1

    target_list[cdx] = 1
    target_list[sdx] = 1
    target_list[0] = year
    target_list[1] = mileage

    # Convert all elements in target_list with 0 being False and 1 being True
    transformed_values = [True if x == 1 else False for x in target_list[2:]]
    target_list = [target_list[0], target_list[1]] + transformed_values
    
    # Insert data into target data frame
    for i in range(1):
        target.loc[i] = target_list

    numerical_features = ['Year', 'Mileage']

    target[numerical_features] = np.log1p(target[numerical_features])
    price_log = ml.predict(target)
    price = np.exp(price_log)
    price = int(price)

    same_model = actual_car_info[actual_car_info["Model"]==model]
    print(same_model)
    year_price = same_model[["Year", "Price"]]
    year_price_list = year_price.groupby("Year").agg({'Price':np.mean}).astype('int')
    year_price_list = year_price_list.reset_index()
    year_price_list["Year"] = year_price_list["Year"].apply(lambda x: str(x) )
    year_price_list["Price"] = year_price_list["Price"].apply(lambda x: str(x) )
    year_list = year_price_list["Year"]
    price_list = year_price_list["Price"]
    same_brand = actual_car_info[actual_car_info["Brand"]==brand]
    same_brand = list(set(same_brand["Model"]))
    same_brand.sort()


    result = {"status": 200, "price":price, "year_list": list(year_list), "price_list":list(price_list), "same_brand":same_brand}
    print(result)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)