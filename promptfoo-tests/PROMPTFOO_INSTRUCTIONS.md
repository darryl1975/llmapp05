# Project Structure

  promptfoo-tests/
  ├── package.json        # npm scripts to run all or individual suites
  ├── classify.yaml       # 4 tests for POST /api/ai/classify
  ├── sentiment.yaml      # 5 tests for POST /api/ai/sentiment
  ├── summarize.yaml      # 3 tests for POST /api/ai/summarize
  └── intent.yaml         # 5 tests for POST /api/ai/intent
  
  # How to Run

  From promptfoo-tests/:

  # Run ALL endpoint tests (17 total)
  npm run eval
  
  # Run a single endpoint suite
  npm run eval:classify
  npm run eval:sentiment
  npm run eval:summarize
  npm run eval:intent
  
  # View results in browser
  npm run view
  
  Or directly with npx:
  
  npx promptfoo@latest eval -c classify.yaml