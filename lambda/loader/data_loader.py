import json
import boto3
import psycopg2
import psycopg2.extras
import logging
from datetime import datetime
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, db_config: Dict, s3_bucket: str):
        self.s3_client = boto3.client('s3')
        self.bucket = s3_bucket
        self.db_config = db_config
    
    def load_from_s3(self, key: str) -> List[Dict]:
        """Load processed data from S3"""
        response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
        return json.loads(response['Body'].read())
    
    def batch_upsert_repositories(self, cursor, repos: List[Dict]) -> Dict[str, int]:
        """Batch insert repositories, return mapping of owner/name to repo_id"""
        repo_map = {}
        
        for repo in repos:
            cursor.execute("""
                INSERT INTO repositories (repo_name, owner, url, description, language, category, license, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (owner, repo_name) 
                DO UPDATE SET 
                    description = EXCLUDED.description,
                    language = EXCLUDED.language,
                    license = EXCLUDED.license
                RETURNING repo_id
            """, (
                repo['repo_name'], repo['owner'], repo['url'], 
                repo.get('description'), repo.get('language'), 
                repo['category'], repo.get('license'), repo['created_at']
            ))
            repo_id = cursor.fetchone()[0]
            repo_map[f"{repo['owner']}/{repo['repo_name']}"] = repo_id
        
        return repo_map
    
    def batch_upsert_metrics(self, cursor, repos: List[Dict], repo_map: Dict[str, int], snapshot_date: str):
        """Batch insert metrics"""
        metrics_data = []
        
        for repo in repos:
            key = f"{repo['owner']}/{repo['repo_name']}"
            repo_id = repo_map[key]
            
            metrics_data.append((
                repo_id, snapshot_date, repo['stars'], repo['forks'], 
                repo['watchers'], repo['open_issues'], repo['activity_score'],
                repo['fork_ratio'], repo['rank']
            ))
        
        psycopg2.extras.execute_batch(cursor, """
            INSERT INTO metrics (repo_id, snapshot_date, stars, forks, watchers, open_issues, 
                                activity_score, fork_ratio, rank_in_category)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (repo_id, snapshot_date)
            DO UPDATE SET
                stars = EXCLUDED.stars,
                forks = EXCLUDED.forks,
                watchers = EXCLUDED.watchers,
                open_issues = EXCLUDED.open_issues,
                activity_score = EXCLUDED.activity_score,
                fork_ratio = EXCLUDED.fork_ratio,
                rank_in_category = EXCLUDED.rank_in_category
        """, metrics_data)
    
    def update_category_summary(self, cursor, category: str):
        """Update category aggregations"""
        cursor.execute("""
            INSERT INTO categories (category_name, total_repos, avg_stars, avg_activity_score, updated_at)
            SELECT 
                %s,
                COUNT(*),
                AVG(m.stars),
                AVG(m.activity_score),
                CURRENT_TIMESTAMP
            FROM repositories r
            JOIN metrics m ON r.repo_id = m.repo_id
            WHERE r.category = %s
            AND m.snapshot_date = (SELECT MAX(snapshot_date) FROM metrics)
            ON CONFLICT (category_name)
            DO UPDATE SET
                total_repos = EXCLUDED.total_repos,
                avg_stars = EXCLUDED.avg_stars,
                avg_activity_score = EXCLUDED.avg_activity_score,
                updated_at = EXCLUDED.updated_at
        """, (category, category))
    
    def load_to_database(self, repos: List[Dict], snapshot_date: str):
        """Load repositories and metrics to database"""
        conn = psycopg2.connect(**self.db_config, sslmode='require')
        cursor = conn.cursor()
        
        try:
            logger.info(f"Loading {len(repos)} repositories to database")
            
            # Batch upsert repositories
            repo_map = self.batch_upsert_repositories(cursor, repos)
            logger.info(f"Upserted {len(repo_map)} repositories")
            
            # Batch upsert metrics
            self.batch_upsert_metrics(cursor, repos, repo_map, snapshot_date)
            logger.info(f"Upserted metrics for {len(repos)} repositories")
            
            # Update category summaries
            categories = set(repo['category'] for repo in repos)
            for category in categories:
                self.update_category_summary(cursor, category)
            logger.info(f"Updated {len(categories)} category summaries")
            
            conn.commit()
            return len(repos)
        except Exception as e:
            logger.error(f"Database load failed: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

def lambda_handler(event, context):
    """AWS Lambda handler"""
    import os
    
    db_config = {
        'host': os.environ['DB_HOST'],
        'database': os.environ['DB_NAME'],
        'user': os.environ['DB_USER'],
        'password': os.environ['DB_PASSWORD'],
        'port': 5432
    }
    
    bucket = os.environ['S3_BUCKET']
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    loader = DataLoader(db_config, bucket)
    
    results = {}
    for category in ['productivity', 'development']:
        key = f'processed/{date_str}/{category}.json'
        repos = loader.load_from_s3(key)
        count = loader.load_to_database(repos, date_str)
        results[category] = count
    
    return {'statusCode': 200, 'body': json.dumps(results)}

if __name__ == "__main__":
    print("Data loader created. Deploy to Lambda for execution.")
    print("Required environment variables:")
    print("  - DB_HOST, DB_NAME, DB_USER, DB_PASSWORD")
    print("  - S3_BUCKET")
