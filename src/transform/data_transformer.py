import json
import boto3
import logging
from datetime import datetime
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataTransformer:
    def __init__(self, s3_bucket: str):
        self.s3_client = boto3.client('s3')
        self.bucket = s3_bucket
    
    def load_from_s3(self, key: str) -> List[Dict]:
        """Load JSON data from S3"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            return json.loads(response['Body'].read())
        except Exception as e:
            logger.error(f"Failed to load from S3 {key}: {e}")
            raise
    
    def calculate_metrics(self, repos: List[Dict]) -> List[Dict]:
        """Calculate derived metrics for repositories"""
        for repo in repos:
            # Validate data
            stars = max(0, repo.get('stars', 0))
            forks = max(0, repo.get('forks', 0))
            watchers = max(0, repo.get('watchers', 0))
            
            repo['activity_score'] = round(
                (stars * 0.5) + (forks * 0.3) + (watchers * 0.2), 2
            )
            
            # Engagement ratio
            if stars > 0:
                repo['fork_ratio'] = round(forks / stars, 3)
            else:
                repo['fork_ratio'] = 0
        
        return repos
    
    def rank_by_category(self, repos: List[Dict]) -> List[Dict]:
        """Add ranking within category"""
        sorted_repos = sorted(repos, key=lambda x: x.get('stars', 0), reverse=True)
        for idx, repo in enumerate(sorted_repos, 1):
            repo['rank'] = idx
        return sorted_repos
    
    def save_to_s3(self, data: List[Dict], key: str):
        """Save processed data to S3"""
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json.dumps(data, indent=2),
            ContentType='application/json'
        )

def glue_handler(event=None, context=None):
    """AWS Glue job handler"""
    bucket = 'github-trending-etl-bucket'
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    transformer = DataTransformer(bucket)
    
    categories = ['productivity', 'development']
    results = {}
    
    for category in categories:
        # Load raw data
        raw_key = f'raw/{date_str}/{category}.json'
        repos = transformer.load_from_s3(raw_key)
        
        # Transform
        repos = transformer.calculate_metrics(repos)
        repos = transformer.rank_by_category(repos)
        
        # Save processed data
        processed_key = f'processed/{date_str}/{category}.json'
        transformer.save_to_s3(repos, processed_key)
        
        results[category] = {
            'count': len(repos),
            'processed_key': processed_key
        }
    
    return {'statusCode': 200, 'body': json.dumps(results)}

if __name__ == "__main__":
    # Local testing
    import sys
    
    bucket = 'github-trending-etl-bucket'
    date_str = '2026-02-05'
    
    transformer = DataTransformer(bucket)
    
    for category in ['productivity', 'development']:
        print(f"\nProcessing {category}...")
        
        # Load from S3
        raw_key = f'raw/{date_str}/{category}.json'
        repos = transformer.load_from_s3(raw_key)
        print(f"Loaded {len(repos)} repos")
        
        # Transform
        repos = transformer.calculate_metrics(repos)
        repos = transformer.rank_by_category(repos)
        
        # Save to S3
        processed_key = f'processed/{date_str}/{category}.json'
        transformer.save_to_s3(repos, processed_key)
        print(f"✓ Saved to s3://{bucket}/{processed_key}")
        
        # Show sample
        print(f"  Top repo: {repos[0]['repo_name']} (rank {repos[0]['rank']}, score {repos[0]['activity_score']})")
