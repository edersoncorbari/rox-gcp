import os
import logging
import pickle
import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

MODEL_NAME = "sales_forecast_model"

DATASET_PATH = "data/sales_dataset.csv"
if not os.path.exists(DATASET_PATH):
    logging.error(f"Arquivo {DATASET_PATH} não encontrado!")
    exit(1)

df = pd.read_csv(DATASET_PATH)

if df.isnull().sum().any():
    logging.warning("O dataset contém valores nulos. Eles serão removidos...")
    df = df.dropna()

X, y = df[["sales", "price", "promotion"]], df["demand"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

model = LinearRegression()
model.fit(X_train, y_train)

predicted_value = model.predict([X_test[0]])[0]
logging.info(f"Teste de Inferência - Input: {X_test[0]}")
logging.info(f"Teste de Inferência - Predict: {predicted_value}")

model_path = f"data/{MODEL_NAME}.pkl"
with open(model_path, "wb") as f:
    pickle.dump({"model": model, "scaler": scaler}, f)

logging.info(f"Modelo salvo localmente em: {model_path}")
