# deployment script at llm-frontend-python/k8s/deployment.yaml. The
  
  ## file includes:
  ┌────────────┬───────────────────────────────────────────────┐
  │  Resource  │                     Name                      │
  ├────────────┼───────────────────────────────────────────────┤
  │ Namespace  │ llm-frontend                                  │
  ├────────────┼───────────────────────────────────────────────┤
  │ Deployment │ llm-frontend-app                              │
  ├────────────┼───────────────────────────────────────────────┤
  │ Container  │ llm-frontend-container                        │
  ├────────────┼───────────────────────────────────────────────┤
  │ Service    │ llm-frontend-service (ClusterIP on port 5000) │
  ├────────────┼───────────────────────────────────────────────┤
  │ ConfigMap  │ llm-frontend-config                           │
  └────────────┴───────────────────────────────────────────────┘
  
  ## Key configurations:
  - Container port: 5000 (matching the Flask app)
  - Image: darryl1975/llm-frontend-python:latest
  - Backend URL configured via ConfigMap to connect to the llm-multiroute service  
  - Health probes pointing to the root endpoint /
  - Resource limits: 256Mi memory, 250m CPU
  
  ## To deploy:
  kubectl apply -f llm-frontend-python/k8s/deployment.yaml 