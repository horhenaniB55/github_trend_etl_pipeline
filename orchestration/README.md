# Orchestration Layer

## Overview
AWS Step Functions orchestrates the ETL pipeline with three stages:
1. **Extract** - Lambda function fetches GitHub data
2. **Transform** - Glue job processes and calculates metrics
3. **Load** - Lambda function loads to RDS

## Components

### Step Functions State Machine
- **Name**: `github-trending-etl-pipeline`
- **ARN**: `arn:aws:states:us-east-1:338394181752:stateMachine:github-trending-etl-pipeline`
- **Definition**: `state-machine.json`

### EventBridge Schedule
- **Rule**: `github-etl-weekly-trigger`
- **Schedule**: Every Sunday at 2 AM UTC (`cron(0 2 ? * SUN *)`)
- **Status**: ENABLED

### IAM Roles
- **Step Functions Role**: `github-etl-stepfunctions-role`
  - Permissions: Invoke Lambda, Start Glue jobs, CloudWatch Logs
- **EventBridge Role**: `github-etl-eventbridge-role`
  - Permissions: Start Step Functions execution

## Manual Execution

```bash
# Trigger pipeline manually
./orchestration/trigger-pipeline.sh

# Check execution status
aws stepfunctions describe-execution \
  --execution-arn <execution-arn>

# List recent executions
aws stepfunctions list-executions \
  --state-machine-arn arn:aws:states:us-east-1:338394181752:stateMachine:github-trending-etl-pipeline \
  --max-results 5
```

## Monitoring

View executions in AWS Console:
https://console.aws.amazon.com/states/home?region=us-east-1#/statemachines/view/arn:aws:states:us-east-1:338394181752:stateMachine:github-trending-etl-pipeline

## Error Handling

The state machine includes error handling for each stage:
- **ExtractFailed** - GitHub API errors
- **TransformFailed** - Data processing errors
- **LoadFailed** - Database connection/insert errors

Failed executions can be retried from the AWS Console.

## Next Steps

1. Deploy Lambda functions (extract & load)
2. Create Glue job (transform)
3. Test end-to-end execution
4. Monitor first scheduled run
