# GitHub Trending ETL Pipeline

## Project Status: Phase 5 Complete ✅

### Completed
- ✅ Project structure created
- ✅ GitHub API extractor implemented and tested
- ✅ Extracting both productivity AND development categories
- ✅ 200 repositories extracted (100 per category)
- ✅ S3 bucket created: `github-trending-etl-bucket`
- ✅ Data uploaded to S3 successfully
- ✅ Transform layer: metrics calculation + ranking
- ✅ RDS PostgreSQL instance created and configured
- ✅ 199 repositories loaded to database
- ✅ Step Functions orchestration deployed
- ✅ EventBridge weekly trigger configured

### Current Data
- **Productivity**: 100 repos (e.g., PowerToys - 129K stars)
- **Development**: 100 repos (e.g., free-for-dev - 117K stars)
- **S3 Location**: `s3://github-trending-etl-bucket/raw/2026-02-05/`

## Next Steps

### 1. ~~Enhance Extractor~~ ✅
- ✅ Extract both productivity AND development categories
- ✅ Successfully extracting 100 repos per category
- [ ] Add rate limiting handling
- [ ] Add pagination for >100 results

### 2. ~~Create S3 Bucket~~ ✅
- ✅ Create S3 bucket: `github-trending-etl-bucket`
- ✅ Set up folder structure (raw/, processed/, exports/)
- ✅ Test upload - working!

### 3. Transform Layer (Glue Job)
- ✅ Create data cleaning script
- ✅ Calculate metrics (star velocity, growth rate)
- ✅ Implement trend analysis

### 4. Load Layer (RDS + Lambda)
- ✅ Set up RDS PostgreSQL instance
- ✅ Create database schema
- ✅ Implement data loader Lambda

### 5. Orchestration (Step Functions)
- ✅ Design state machine
- ✅ Set up EventBridge trigger
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
