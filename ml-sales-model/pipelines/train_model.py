import os
import pickle
import argparse
import pandas as pd
from google.cloud import storage, aiplatform
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

parser = argparse.ArgumentParser()
parser.add_argument("--model-dir", type=str, required=True)
args = parser.parse_args()

project_id = ""
region = ""
bucket_name = "mlops-models15"

file_name = "sales_dataset.csv"

storage_client = storage.Client(project=project_id)
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(file_name)
blob.download_to_filename(file_name)

df = pd.read_csv(file_name)
X, y = df[["sales", "price", "promotion"]], df["demand"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)

model_path = os.path.join(args.model_dir, "sales_forecast_model.pkl")
with open(model_path, "wb") as f:
    pickle.dump(model, f)

blob = bucket.blob(f"models/sales_forecast_model.pkl")
blob.upload_from_filename(model_path)
print(f"Modelo salvo em: gs://{bucket_name}/models/sales_forecast_model.pkl")

aiplatform.init(project=project_id, location=region)
model = aiplatform.Model.upload(
    display_name="sales_forecast_model",
    artifact_uri=f"gs://{bucket_name}/models/sales_forecast_model.pkl",
    serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-0"
)
print(f"Modelo registrado no Vertex AI: {model.resource_name}")
