  llm-multiroute/Dockerfile
  - Python 3.12 slim base image
  - Installs FastAPI/uvicorn dependencies
  - Exposes port 8080
  - Runs uvicorn on 0.0.0.0:8080
  llm-frontend-python/Dockerfile
  - Python 3.12 slim base image
  - Installs Flask/requests dependencies
  - Exposes port 5000
  - Runs python app.py
  docker-compose.yml (project root)
  - Defines a shared llm-network (bridge driver) so both containers can communicate
  - llm-multiroute service: passes through all Ollama config via environment
   variables (reads from your host .env or shell)
  - llm-frontend-python service: sets BACKEND_URL=http://llm-multiroute:8080
   so the frontend proxy reaches the backend using Docker's internal DNS, and FLASK_DEBUG=false for production
  - depends_on ensures the backend starts before the frontend 
  
  How to run
  # Set your API key (or put it in a .env file at the project root)
  export OLLAMA_API_KEY=your_key_here 
  
  # Build and start both services 
  docker compose up --build

  The frontend will be available at http://localhost:5000 and the backend  API at http://localhost:8082.  