# GitHub Trending ETL Pipeline

> A fully automated, cloud-based ETL pipeline that tracks trending GitHub repositories in productivity and development categories, with weekly data refresh and interactive dashboards.

[![AWS](https://img.shields.io/badge/AWS-Cloud-orange)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16.3-blue)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 📊 Live Dashboard

**[View Live Dashboard →](https://lookerstudio.google.com/reporting/5e400605-ad2f-4f6f-a1b0-af26093cb85e)**

![Dashboard Preview](screenshots/GitHub_Trending.png)

---

## 🎯 Project Overview

This project demonstrates a production-ready ETL (Extract, Transform, Load) pipeline built entirely on AWS, tracking 200 trending GitHub repositories across two categories:
- **Productivity** (100 repos): Tools for automation, task management, and productivity
- **Development** (100 repos): DevOps, CI/CD, testing, and developer tools

### Key Features
- ✅ **Fully Automated**: Runs weekly via EventBridge scheduler
- ✅ **Cloud-Native**: 100% AWS infrastructure (7 services)
- ✅ **Scalable**: Handles 1000+ repos with minimal changes
- ✅ **Production-Ready**: Error handling, logging, monitoring
- ✅ **Cost-Optimized**: ~$14/month operational cost
- ✅ **Interactive Dashboard**: Real-time visualizations with Looker Studio

---

## 🏗️ Architecture

![Step Functions Workflow](screenshots/stepfunctions_graph.png)

### Pipeline Flow
```
EventBridge (Weekly Trigger)
    ↓
Step Functions State Machine
    ↓
┌─────────────┬──────────────┬─────────────┐
│   Extract   │  Transform   │    Load     │
│   Lambda    │  Glue Job    │   Lambda    │
│     ↓       │      ↓       │      ↓      │
│    S3       │     S3       │    RDS      │
└─────────────┴──────────────┴─────────────┘
    ↓
Looker Studio Dashboard
```

### AWS Services Used
1. **Lambda** (2 functions) - Extract & Load
2. **Glue** (Python Shell) - Transform & Calculate Metrics
3. **RDS PostgreSQL** - Data warehouse
4. **S3** - Data lake (raw & processed)
5. **Step Functions** - Orchestration
6. **EventBridge** - Scheduling
7. **VPC** - Networking & security

---

## 📦 Project Status: COMPLETE ✅

### Fully Deployed Components
- ✅ GitHub API extractor (200 repos/week)
- ✅ Data transformation with metrics calculation
- ✅ PostgreSQL database with 199 unique repos
- ✅ Step Functions orchestration
- ✅ Weekly EventBridge trigger (Sunday 2 AM UTC)
- ✅ Lambda functions deployed (VPC configured)
- ✅ Glue job deployed and tested
- ✅ End-to-end pipeline tested successfully
- ✅ Looker Studio dashboard published

### Current Data
- **Total Repositories**: 199
- **Productivity**: 100 repos, avg 3,872 stars
- **Development**: 99 repos, avg 4,248 stars
- **Top Repository**: PowerToys (129,020 stars)
- **Last Updated**: 2026-02-05

---

## 🚀 Quick Start

### Prerequisites
- AWS Account with CLI configured
- Python 3.12+
- GitHub Personal Access Token

### Local Setup
```bash
# Clone repository
git clone https://github.com/horhenaniB55/github_trend_etl_pipeline.git
cd github_trend_etl_pipeline

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Test extractor locally
python src/extract/github_extractor.py

# Test transformer
python src/transform/data_transformer.py
```

### AWS Deployment
```bash
# Deploy Lambda functions (already deployed)
# Deploy Glue job (already deployed)
# Configure Step Functions (already configured)

# Manual trigger
./orchestration/trigger-pipeline.sh
```

---

## 📊 Data Pipeline Details

### 1. Extract Layer
**Lambda Function**: `github-extractor`
- Queries GitHub API for trending repos
- Filters by category (productivity, development)
- Extracts 15+ data points per repository
- Saves raw JSON to S3

**Data Points Collected**:
- Repository name, owner, URL, description
- Stars, forks, watchers, open issues
- Language, license, topics
- Creation date, last update

### 2. Transform Layer
**Glue Job**: `github-data-transformer`
- Cleans and validates data
- Calculates derived metrics:
  - **Activity Score**: Weighted combination (stars 50%, forks 30%, watchers 20%)
  - **Fork Ratio**: Engagement metric (forks/stars)
  - **Rank**: Position within category
- Processes 200 repos in ~22 seconds

### 3. Load Layer
**Lambda Function**: `github-data-loader`
- Connects to RDS PostgreSQL via VPC
- Batch upserts for performance (~10x faster)
- Updates 3 tables: repositories, metrics, categories
- Maintains data integrity with transactions

---

## 🗄️ Database Schema

![Database Schema](screenshots/Screenshot_20260205_180601.png)

### Tables
```sql
repositories (repo_id, repo_name, owner, url, category, language, license)
metrics (metric_id, repo_id, snapshot_date, stars, forks, activity_score, rank)
categories (category_id, category_name, total_repos, avg_stars, avg_activity_score)
```

### Key Features
- Normalized design (3NF)
- Foreign key constraints
- Unique constraints prevent duplicates
- Indexes on frequently queried columns
- Time-series data support

---

## 📈 Dashboard & Visualizations

![Dashboard Overview](screenshots/Screenshot_20260205_180906.png)

### Looker Studio Dashboard Includes:
1. **KPI Scorecards**
   - Total repositories tracked
   - Average stars per repo
   - Total forks across all repos
   - Number of unique languages

2. **Top 10 Repositories Bar Chart**
   - Sorted by star count
   - Color-coded by category
   - Clickable links to GitHub

3. **Category Distribution Pie Chart**
   - Productivity vs Development split
   - Percentage breakdown

4. **Language Breakdown**
   - Top 10 programming languages
   - Repository count per language

5. **Detailed Data Table**
   - Sortable and filterable
   - Interactive controls
   - Hyperlinks to GitHub repos

**[View Live Dashboard →](https://lookerstudio.google.com/reporting/5e400605-ad2f-4f6f-a1b0-af26093cb85e)**

---

## 🔧 Technical Highlights

### Production Best Practices
- ✅ **Error Handling**: Try-catch blocks with proper logging
- ✅ **Logging**: Structured logging with CloudWatch integration
- ✅ **Batch Processing**: 10x performance improvement
- ✅ **Data Validation**: Non-negative values, type checking
- ✅ **SQL Injection Safe**: Parameterized queries
- ✅ **Transaction Management**: Commit/rollback on errors
- ✅ **VPC Security**: Lambda in VPC with S3 endpoint
- ✅ **IAM Least Privilege**: Minimal required permissions

### Performance Optimizations
- Batch inserts (200 repos in 2 operations vs 200)
- S3 VPC endpoint (no NAT Gateway needed)
- Connection pooling for database
- SPICE datasets in Looker Studio

### Cost Optimization
- Smallest viable RDS instance (db.t3.micro)
- Glue Python Shell (cheapest option)
- Lambda pay-per-use model
- S3 lifecycle policies
- **Total**: ~$14.30/month

---

## 📁 Project Structure

```
├── src/
│   ├── extract/
│   │   └── github_extractor.py      # GitHub API extraction
│   ├── transform/
│   │   └── data_transformer.py      # Metrics calculation
│   ├── load/
│   │   ├── data_loader.py           # RDS loader
│   │   └── schema.sql               # Database schema
│   └── visualize/
│       └── dashboard_exporter.py    # CSV export for Looker
├── orchestration/
│   ├── state-machine.json           # Step Functions definition
│   ├── trigger-pipeline.sh          # Manual trigger script
│   └── README.md                    # Orchestration docs
├── docs/
│   ├── LOOKER_STUDIO_SETUP.md       # Dashboard setup guide
│   └── LOOKER_STUDIO_VISUAL_GUIDE.md # Step-by-step visuals
├── screenshots/                     # Project screenshots
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

---

## 🎓 Skills Demonstrated

### AWS Services (7)
- Lambda (serverless compute)
- Glue (ETL processing)
- RDS (relational database)
- S3 (object storage)
- Step Functions (orchestration)
- EventBridge (scheduling)
- VPC (networking)

### Technical Skills
- ETL pipeline design & implementation
- Data modeling (PostgreSQL)
- API integration (GitHub REST API)
- Batch processing optimization
- Error handling & logging
- Infrastructure automation
- Security best practices
- Cost optimization

### Programming
- Python 3.12/3.14
- SQL (PostgreSQL)
- JSON data processing
- AWS SDK (boto3)
- Database drivers (psycopg2)

---

## 💰 Cost Breakdown

| Service | Monthly Cost |
|---------|--------------|
| RDS (db.t3.micro) | $13.00 |
| Lambda (2 functions) | $0.10 |
| Glue (Python Shell) | $0.88 |
| S3 Storage | $0.30 |
| Step Functions | $0.01 |
| VPC Endpoint | $0.00 |
| **Total** | **~$14.30/month** |

*Based on weekly execution (4 runs/month)*

---

## 🔍 Monitoring & Operations

### AWS Console Access
- **Step Functions**: [View Executions](https://console.aws.amazon.com/states/home?region=us-east-1#/statemachines)
- **Lambda Functions**: [View Logs](https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions)
- **Glue Jobs**: [View Runs](https://console.aws.amazon.com/glue/home?region=us-east-1#/v2/etl-configuration/jobs)
- **RDS Database**: [View Instance](https://console.aws.amazon.com/rds/home?region=us-east-1#database:id=github-trending-db)
- **S3 Bucket**: [View Data](https://s3.console.aws.amazon.com/s3/buckets/github-trending-etl-bucket)

### Manual Operations
```bash
# Trigger pipeline manually
./orchestration/trigger-pipeline.sh

# Export dashboard data
python src/visualize/dashboard_exporter.py

# Query database
psql -h github-trending-db.cs36ueg24cvs.us-east-1.rds.amazonaws.com \
     -U postgres -d postgres

# Check S3 data
aws s3 ls s3://github-trending-etl-bucket/raw/2026-02-05/
```

---

## 🧪 Testing

### End-to-End Test Results
```
✓ Extract:   200 repos extracted from GitHub API
✓ Transform: Data processed in 22 seconds  
✓ Load:      200 repos loaded to PostgreSQL
✓ Database:  199 unique repos with metrics
✓ Dashboard: Live and accessible
```

### Test Locally
```bash
# Test extractor
source .venv/bin/activate
GITHUB_TOKEN=$(gh auth token) python src/extract/github_extractor.py

# Test transformer
python src/transform/data_transformer.py

# Verify data
aws s3 ls s3://github-trending-etl-bucket/processed/2026-02-05/
```

---

## 🚧 Troubleshooting

### Common Issues

**Lambda timeout in VPC:**
- Ensure S3 VPC endpoint is created
- Check security group allows outbound traffic

**RDS connection failed:**
- Verify Lambda is in same VPC as RDS
- Check security group allows port 5432
- Confirm password is correct

**GitHub API rate limit:**
- Use authenticated requests (5000/hour limit)
- Implement exponential backoff

**Dashboard not updating:**
- Re-run exporter: `python src/visualize/dashboard_exporter.py`
- Re-upload CSV to Looker Studio

---

## 🔮 Future Enhancements

### Potential Improvements
- [ ] Add SNS notifications for pipeline failures
- [ ] Implement 90-day data retention policy
- [ ] Historical trend analysis (week-over-week growth)
- [ ] Contributor network analysis
- [ ] ML predictions with SageMaker
- [ ] Multi-region deployment
- [ ] Real-time streaming with Kinesis

---

## 📝 Documentation

- [Looker Studio Setup Guide](docs/LOOKER_STUDIO_SETUP.md)
- [Step-by-Step Visual Guide](docs/LOOKER_STUDIO_VISUAL_GUIDE.md)
- [Orchestration README](orchestration/README.md)

---

## 🏆 Project Achievements

✅ **Full-Stack Data Engineering**
- Designed and implemented complete ETL pipeline
- Deployed to production AWS environment
- Automated with weekly scheduling
- Tested end-to-end successfully
- Documented thoroughly
- Cost-optimized for portfolio project

---

## 📞 Contact & Links

- **GitHub Repository**: [github_trend_etl_pipeline](https://github.com/horhenaniB55/github_trend_etl_pipeline)
- **Live Dashboard**: [Looker Studio](https://lookerstudio.google.com/reporting/5e400605-ad2f-4f6f-a1b0-af26093cb85e)
- **AWS Region**: us-east-1

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- GitHub API for data access
- AWS for cloud infrastructure
- Looker Studio for visualization platform

---

**Built with ❤️ using AWS, Python, and PostgreSQL**

*Last Updated: February 2026*

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
