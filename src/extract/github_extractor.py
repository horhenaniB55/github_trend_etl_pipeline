import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List
import boto3

class GitHubExtractor:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        self.base_url = "https://api.github.com"
    
    def search_repositories(self, query: str, min_stars: int = 50) -> List[Dict]:
        """Search GitHub repositories with filters"""
        since_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        search_query = f"({query}) stars:>={min_stars} pushed:>={since_date}"
        
        url = f"{self.base_url}/search/repositories"
        params = {
            "q": search_query,
            "sort": "stars",
            "order": "desc",
            "per_page": 100
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json().get("items", [])
    
    def get_repo_details(self, owner: str, repo: str) -> Dict:
        """Get detailed repository information"""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def extract_category(self, category: str, query: str) -> List[Dict]:
        """Extract repositories for a specific category"""
        repos = self.search_repositories(query)
        
        extracted_data = []
        for repo in repos:
            data = {
                "repo_name": repo["name"],
                "owner": repo["owner"]["login"],
                "url": repo["html_url"],
                "description": repo.get("description", ""),
                "stars": repo["stargazers_count"],
                "forks": repo["forks_count"],
                "watchers": repo["watchers_count"],
                "open_issues": repo["open_issues_count"],
                "language": repo.get("language", ""),
                "created_at": repo["created_at"],
                "updated_at": repo["updated_at"],
                "topics": repo.get("topics", []),
                "license": repo.get("license", {}).get("name", "") if repo.get("license") else "",
                "category": category,
                "snapshot_date": datetime.now().isoformat()
            }
            extracted_data.append(data)
        
        return extracted_data

def lambda_handler(event, context):
    """AWS Lambda handler function"""
    token = os.environ.get("GITHUB_TOKEN")
    s3_bucket = os.environ.get("S3_BUCKET")
    
    extractor = GitHubExtractor(token)
    
    categories = {
        "productivity": "topic:productivity OR topic:automation OR topic:task-management OR topic:notes",
        "development": "topic:devops OR topic:ci-cd OR topic:testing OR topic:api OR topic:developer-tools"
    }
    
    s3_client = boto3.client("s3")
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    results = {}
    for category, query in categories.items():
        data = extractor.extract_category(category, query)
        
        # Save to S3
        key = f"raw/{date_str}/{category}.json"
        s3_client.put_object(
            Bucket=s3_bucket,
            Key=key,
            Body=json.dumps(data, indent=2),
            ContentType="application/json"
        )
        
        results[category] = {
            "count": len(data),
            "s3_key": key
        }
    
    return {
        "statusCode": 200,
        "body": json.dumps(results)
    }

if __name__ == "__main__":
    # Local testing
    import sys
    token = os.getenv("GITHUB_TOKEN") or (sys.argv[1] if len(sys.argv) > 1 else None)
    if not token:
        print("Usage: python github_extractor.py <token> or set GITHUB_TOKEN env var")
        sys.exit(1)
    
    extractor = GitHubExtractor(token)
    
    categories = {
        "productivity": "productivity",
        "development": "devops"
    }
    
    os.makedirs("data/raw", exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    for category, query in categories.items():
        print(f"\nExtracting {category} repos...")
        data = extractor.extract_category(category, query)
        
        filepath = f"data/raw/{category}_{date_str}.json"
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ {len(data)} repos saved to {filepath}")
        if data:
            print(f"  Sample: {data[0]['repo_name']} ({data[0]['stars']} stars)")
