# Kubernetes deployment script at                          
  llm-multiroute/k8s/deployment.yaml with the following resources:     
  Resource: Namespace                                                  
  Name: llm-multiroute-backend                                         
  Description: Isolated namespace for the application                  
  ────────────────────────────────────────                             
  Resource: Deployment                                                 
  Name: llm-multiroute-app                                             
  Description: Deploys the container with health probes                
  ────────────────────────────────────────                             
  Resource: Container                                                  
  Name: llm-multiroute-container                                       
  Description: Runs on port 8080                                       
  ────────────────────────────────────────                             
  Resource: Service                                                    
  Name: llm-multiroute-service                                         
  Description: ClusterIP service exposing port 8080                    
  ────────────────────────────────────────                             
  Resource: ConfigMap                                                  
  Name: llm-multiroute-config                                          
  Description: Stores Ollama configuration                             
  ────────────────────────────────────────                             
  Resource: Secret                                                     
  Name: llm-multiroute-secret                                          
  Description: Stores the API key (needs base64 value)                 
  To deploy:                                                           
  # First, encode your API key                                         
  echo -n 'your-api-key' | base64                                      
                                                                       
  # Update the secret in deployment.yaml with the encoded value, then  
  apply                                                                
  kubectl apply -f llm-multiroute/k8s/deployment.yaml  