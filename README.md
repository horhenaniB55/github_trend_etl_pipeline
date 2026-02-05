# GitHub Trending ETL Pipeline

## Project Status: Phase 2 - Extract Layer ✅

### Completed
- ✅ Project structure created
- ✅ GitHub API extractor implemented and tested
- ✅ Successfully extracting repository data
- ✅ Data saved locally in JSON format

### Current Data
- Extracted 3 productivity repositories
- Data includes: stars, forks, watchers, topics, language, license
- Saved to: `data/raw/productivity_2026-02-05.json`

## Next Steps

### 1. Enhance Extractor
- [ ] Add better query filters (use topic: prefix)
- [ ] Extract both productivity AND development categories
- [ ] Add rate limiting handling
- [ ] Add pagination for >100 results

### 2. Create S3 Bucket
- [ ] Create S3 bucket: `github-trending-etl-bucket`
- [ ] Set up folder structure (raw/, processed/, exports/)
- [ ] Test upload from Lambda

### 3. Transform Layer (Glue Job)
- [ ] Create data cleaning script
- [ ] Calculate metrics (star velocity, growth rate)
- [ ] Implement trend analysis

### 4. Load Layer (RDS + Lambda)
- [ ] Set up RDS PostgreSQL instance
- [ ] Create database schema
- [ ] Implement data loader Lambda

### 5. Orchestration (Step Functions)
- [ ] Design state machine
- [ ] Set up EventBridge trigger
- [ ] Test end-to-end pipeline

## Quick Start

```bash
# Activate environment
source .venv/bin/activate

# Run extractor locally
python src/extract/github_extractor.py

# Check output
cat data/raw/productivity_2026-02-05.json
```

## AWS Resources Needed
- S3 bucket
- RDS PostgreSQL (db.t3.micro)
- Lambda functions (2)
- Glue Python Shell job
- Step Functions state machine
- EventBridge rule
