from google.cloud import aiplatform

def deploy_model(event, context):
    project_id = ""
    model_name = event["name"]

    aiplatform.init(project=project_id, location="us-west1")
    model = aiplatform.Model(model_name)
    
    endpoint = aiplatform.Endpoint.create(display_name="sales_forecast_endpoint")
    model.deploy(endpoint=endpoint, machine_type="n1-standard-4")

    print(f"Modelo {model_name} implantado no endpoint {endpoint.resource_name}")

