# send request
import requests
import ray
from ray import serve

if __name__ == "__main__":

    ray.init(address="auto", namespace="xgbregressor")
    print(serve.list_deployments())

    sample_request_inputs = [
        {"Pregnancies": 6,
         "Glucose": 148,
         "BloodPressure": 72,
         "SkinThickness": 35,
         "Insulin": 0,
         "BMI": 33.6,
         "DiabetesPedigree": 0.625,
         "Age": 50,
         },
        {"Pregnancies": 10,
         "Glucose": 168,
         "BloodPressure": 74,
         "SkinThickness": 0,
         "Insulin": 0,
         "BMI": 38.0,
         "DiabetesPedigree": 0.537,
         "Age": 34,
         },
        {"Pregnancies": 10,
         "Glucose": 39,
         "BloodPressure": 80,
         "SkinThickness": 0,
         "Insulin": 0,
         "BMI": 27.1,
         "DiabetesPedigree": 1.441,
         "Age": 57,
         },
        {"Pregnancies": 1,
         "Glucose": 103,
         "BloodPressure": 30,
         "SkinThickness": 38,
         "Insulin": 83,
         "BMI": 43.3,
         "DiabetesPedigree": 0.183,
         "Age": 33,
         }
    ]
    for sri in sample_request_inputs:
        response = requests.post("http://localhost:8000/regressor/", json=sri)
        print(response.text)