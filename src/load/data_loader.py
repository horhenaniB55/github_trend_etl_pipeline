import json
import boto3
import psycopg2
from datetime import datetime
from typing import List, Dict

class DataLoader:
    def __init__(self, db_config: Dict, s3_bucket: str):
        self.s3_client = boto3.client('s3')
        self.bucket = s3_bucket
        self.db_config = db_config
    
    def load_from_s3(self, key: str) -> List[Dict]:
        """Load processed data from S3"""
        response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
        return json.loads(response['Body'].read())
    
    def upsert_repository(self, cursor, repo: Dict) -> int:
        """Insert or update repository, return repo_id"""
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
        return cursor.fetchone()[0]
    
    def upsert_metrics(self, cursor, repo_id: int, repo: Dict, snapshot_date: str):
        """Insert or update metrics"""
        cursor.execute("""
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
        """, (
            repo_id, snapshot_date, repo['stars'], repo['forks'], 
            repo['watchers'], repo['open_issues'], repo['activity_score'],
            repo['fork_ratio'], repo['rank']
        ))
    
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
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()
        
        try:
            for repo in repos:
                repo_id = self.upsert_repository(cursor, repo)
                self.upsert_metrics(cursor, repo_id, repo, snapshot_date)
            
            # Update category summaries
            categories = set(repo['category'] for repo in repos)
            for category in categories:
                self.update_category_summary(cursor, category)
            
            conn.commit()
            return len(repos)
        except Exception as e:
            conn.rollback()
            raise e
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
