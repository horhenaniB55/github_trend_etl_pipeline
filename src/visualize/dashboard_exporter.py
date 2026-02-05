import json
import boto3
import psycopg2
from datetime import datetime
import os

class DashboardExporter:
    def __init__(self, db_config, s3_bucket):
        self.db_config = db_config
        self.s3_client = boto3.client('s3')
        self.bucket = s3_bucket
    
    def export_dashboard_data(self):
        """Export data for dashboard visualization"""
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()
        
        # Get latest snapshot date
        cursor.execute('SELECT MAX(snapshot_date) FROM metrics')
        latest_date = cursor.fetchone()[0]
        
        # Top repos by category
        cursor.execute('''
            SELECT r.category, r.repo_name, r.owner, r.url, 
                   m.stars, m.forks, m.activity_score, m.rank_in_category
            FROM repositories r
            JOIN metrics m ON r.repo_id = m.repo_id
            WHERE m.snapshot_date = %s
            ORDER BY r.category, m.rank_in_category
            LIMIT 20
        ''', (latest_date,))
        
        top_repos = []
        for row in cursor.fetchall():
            top_repos.append({
                'category': row[0],
                'repo_name': row[1],
                'owner': row[2],
                'url': row[3],
                'stars': row[4],
                'forks': row[5],
                'activity_score': float(row[6]),
                'rank': row[7]
            })
        
        # Category summary
        cursor.execute('''
            SELECT category_name, total_repos, 
                   ROUND(avg_stars::numeric, 0) as avg_stars,
                   ROUND(avg_activity_score::numeric, 0) as avg_activity
            FROM categories
            ORDER BY category_name
        ''')
        
        categories = []
        for row in cursor.fetchall():
            categories.append({
                'name': row[0],
                'total_repos': row[1],
                'avg_stars': int(row[2]),
                'avg_activity': int(row[3])
            })
        
        cursor.close()
        conn.close()
        
        dashboard_data = {
            'generated_at': datetime.now().isoformat(),
            'snapshot_date': str(latest_date),
            'categories': categories,
            'top_repos': top_repos
        }
        
        return dashboard_data
    
    def save_to_s3(self, data):
        """Save dashboard data to S3"""
        key = 'exports/dashboard/latest.json'
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json.dumps(data, indent=2),
            ContentType='application/json',
            CacheControl='no-cache'
        )
        return f's3://{self.bucket}/{key}'

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
    
    exporter = DashboardExporter(db_config, 'github-trending-etl-bucket')
    data = exporter.export_dashboard_data()
    s3_path = exporter.save_to_s3(data)
    
    print(f"✓ Dashboard data exported to {s3_path}")
    print(f"  Categories: {len(data['categories'])}")
    print(f"  Top repos: {len(data['top_repos'])}")
