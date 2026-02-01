# GitHub Actions Workflows 

  ## 1. llm-multiroute-ci.yml — Python Pipeline
  - Triggers: push/PR on llm-multiroute/** changes
  - Jobs: Lint (Ruff) → Unit Tests (pytest) → Docker Build
  - Pipeline: 3-stage sequential — lint must pass before tests, tests  before Docker build
  1. llm-frontend-python-ci.yml — Python Pipeline
  - Triggers: push/PR on llm-frontend-python/** changes
  - Jobs: Lint (Ruff) → Docker Build
  - Pipeline: 2-stage sequential — no tests exist, so lint then build  

  ## 2. promptfoo-tests-ci.yml — Node.js Pipeline
  - Triggers: push/PR on promptfoo-tests/** OR llm-multiroute/**
  changes
  - Jobs: Single job that starts the backend via docker compose, waits for health, runs all 4 PromptFoo evaluations, then tears down
  - Pipeline: Integration test pipeline using Node.js 20 (different runtime from the Python projects) 
  - Required secrets: OLLAMA_API_KEY, OLLAMA_BASE_URL
  
  ## 3. deepeval-tests-ci.yml — Python Pipeline (with Docker integration)
  - Triggers: push/PR on deepeval-tests/** OR llm-multiroute/** changes
  - Jobs: Single job that installs Python deps, starts the backend via docker compose, waits for health, runs all 4 DeepEval test suites, then tears down
  - Pipeline: LLM evaluation pipeline using Python 3.12 + DeepEval
  judge model
  - Required secrets: OLLAMA_API_KEY, OLLAMA_BASE_URL, OPENAI_API_KEY
  Required GitHub Repository Secrets
  You'll need to add these secrets in your repo settings (Settings >
  Secrets and variables > Actions):
  Secret: OLLAMA_API_KEY
  Used By: promptfoo, deepeval
  Purpose: Authenticate with Ollama cloud API
  ────────────────────────────────────────
  Secret: OLLAMA_BASE_URL
  Used By: promptfoo, deepeval
  Purpose: Ollama cloud endpoint URL
  ────────────────────────────────────────
  Secret: OPENAI_API_KEY
  Used By: deepeval only
  Purpose: DeepEval's judge LLM for evaluation metrics

## Updated pipeline stages

  llm-multiroute: Lint → Unit Tests → Build Image → Trivy Scan → Push  
  llm-frontend-python: Lint → Build Image → Trivy Scan → Push          
                                                                       
  What the Trivy step does                                             
                                                                       
  1. Build for scanning — The image is built with load: true into the  
  local Docker daemon (no push yet), tagged as <image>:scan            
  2. Trivy scan — aquasecurity/trivy-action scans the local image for  
  vulnerabilities                                                      
    - Reports in table format for readable CI output                   
    - exit-code: '1' — fails the workflow if vulnerabilities are found 
    - severity: 'CRITICAL,HIGH' — only blocks on CRITICAL and HIGH     
  severity issues (MEDIUM/LOW won't fail the build)                    
  3. Push — Only runs if the Trivy scan passes and it's not a pull     
  request. Uses the build cache so the push is fast since the image    
  layers already exist. 


    .trivyignore created at the repo root with CVE-2026-0861 suppressed —
   the glibc integer overflow in memalign that has no upstream fix     
  available yet.                                                       
                                                                       
  Both workflows updated to pass trivyignores: .trivyignore to the     
  Trivy action, so the scanner skips that CVE.                         
                                                                       
  The pipeline will now pass since the 6 OpenSSL findings were already 
  resolved by the apt-get upgrade in the Dockerfiles, and the 2        
  remaining glibc findings are suppressed. Once Debian publishes a     
  glibc patch, you can remove CVE-2026-0861 from .trivyignore and the  
  upgrade step will pick up the fix automatically.  