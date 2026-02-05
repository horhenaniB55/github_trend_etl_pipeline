import json
import boto3
import psycopg2
import csv
from datetime import datetime
import os

class LookerStudioExporter:
    def __init__(self, db_config, s3_bucket):
        self.db_config = db_config
        self.s3_client = boto3.client('s3')
        self.bucket = s3_bucket
    
    def export_to_csv(self):
        """Export data to CSV for Looker Studio"""
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()
        
        # Get latest snapshot
        cursor.execute('SELECT MAX(snapshot_date) FROM metrics')
        latest_date = cursor.fetchone()[0]
        
        # Export main dataset
        cursor.execute('''
            SELECT 
                r.repo_name,
                r.owner,
                r.url,
                r.category,
                r.language,
                r.license,
                m.stars,
                m.forks,
                m.watchers,
                m.open_issues,
                m.activity_score,
                m.fork_ratio,
                m.rank_in_category,
                m.snapshot_date
            FROM repositories r
            JOIN metrics m ON r.repo_id = m.repo_id
            WHERE m.snapshot_date = %s
            ORDER BY m.stars DESC
        ''', (latest_date,))
        
        rows = cursor.fetchall()
        columns = ['repo_name', 'owner', 'url', 'category', 'language', 'license',
                   'stars', 'forks', 'watchers', 'open_issues', 'activity_score',
                   'fork_ratio', 'rank', 'snapshot_date']
        
        # Save to CSV
        csv_file = '/tmp/github_trending.csv'
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)
        
        # Upload to S3
        key = 'exports/looker-studio/github_trending.csv'
        self.s3_client.upload_file(
            csv_file,
            self.bucket,
            key,
            ExtraArgs={'ContentType': 'text/csv'}
        )
        
        cursor.close()
        conn.close()
        
        return f's3://{self.bucket}/{key}', len(rows)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    db_config = {
        'host': os.getenv('DB_HOST'),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': 'require'
    }
    
    exporter = LookerStudioExporter(db_config, 'github-trending-etl-bucket')
    s3_path, count = exporter.export_to_csv()
    
    print(f"✓ Exported {count} repos to {s3_path}")
    print(f"✓ CSV ready for Looker Studio import")
