from google.cloud import aiplatform

project_id = ""
region = "us-west1"

def deploy_model(event, context) -> None:
    
    model_name = event["name"]

    aiplatform.init(project=project_id, location=region)
    model = aiplatform.Model(model_name)
    
    endpoint = aiplatform.Endpoint.create(display_name="sales_forecast_endpoint")
    model.deploy(endpoint=endpoint, machine_type="n1-standard-4")

    print(f"Modelo {model_name} implantado no endpoint {endpoint.resource_name}")
