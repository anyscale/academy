#
# INSTRUCTIONS HOW TO RUN THIS DEPLOYMENT
#
# 1. In a shell window start the ray cluster as a single node
#       ray start --head
# 2. In this window execute this script. This attach to the running ray cluster and start
#    a detached Ray Serve instance, even though this script will exit.
#       python xgboost_fastapi.py
# 3. Send requests to the Ray Serve instance
#       python send_requests.py
# 4. Stop the ray processes, including the Ray Serve instance
#       ray stop

import numpy as np
from numpy import loadtxt
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle

import ray
from fastapi import FastAPI, Request
from ray import serve

app = FastAPI()
ray.init(address="auto", namespace="xgbregressor")
serve.start(detached=True)

# Load the data
dataset = loadtxt('pima-indians-diabetes.data.csv', delimiter=",")
# split data into X and y
X = dataset[:, 0:8]
y = dataset[:, 8]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=7)


def create_and_save_model():
    # Instantiate a model, fit and train
    xgb_model = XGBClassifier()
    xgb_model.fit(X_train, y_train)

    # saving the model
    with open('xgb_model.pkl', 'wb') as f:
        pickle.dump(xgb_model, f)

    return xgb_model


@serve.deployment(num_replicas=2, route_prefix="/regressor")
@serve.ingress(app)
class XGBModel:
    def __init__(self):
        # loading the model
        with open("xgb_model.pkl", "rb") as f:
            self.model = pickle.load(f)
        print("Pickled XGBoost model loaded")

    @app.post("/")
    async def predict(self, starlette_request:Request):
        payload = await starlette_request.json()
        print("Worker: received starlette request with data", payload)

        # input_vector = [
        #     payload["Pregnancies"],
        #     payload["Glucose"],
        #     payload["BloodPressure"],
        #     payload["SkinThickness"],
        #     payload["Insulin"],
        #     payload["BMI"],
        #     payload["DiabetesPedigree"],
        #     payload["Age"],
        # ]
        prediction = self.model.predict([np.array(list(payload.values()))])[0]
        # prediction = self.model.predict([np.array(input_vector)])[0]
        return {"result": prediction}


if __name__ == "__main__":

    model = create_and_save_model()
    y_pred = model.predict(X_test)
    predictions = [round(value) for value in y_pred]
    accuracy = accuracy_score(y_test, predictions)
    print("Accuracy: %.2f%%" % (accuracy * 100.0))

    # Now deploy to Ray Serve
    XGBModel.deploy()


