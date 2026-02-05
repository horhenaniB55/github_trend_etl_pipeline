-- GitHub Trending ETL Database Schema

-- Repositories table
CREATE TABLE IF NOT EXISTS repositories (
    repo_id SERIAL PRIMARY KEY,
    repo_name VARCHAR(255) NOT NULL,
    owner VARCHAR(255) NOT NULL,
    url TEXT,
    description TEXT,
    language VARCHAR(100),
    category VARCHAR(50),
    license VARCHAR(100),
    created_at TIMESTAMP,
    UNIQUE(owner, repo_name)
);

-- Metrics table (time-series data)
CREATE TABLE IF NOT EXISTS metrics (
    metric_id SERIAL PRIMARY KEY,
    repo_id INTEGER REFERENCES repositories(repo_id) ON DELETE CASCADE,
    snapshot_date DATE NOT NULL,
    stars INTEGER,
    forks INTEGER,
    watchers INTEGER,
    open_issues INTEGER,
    activity_score DECIMAL(10,2),
    fork_ratio DECIMAL(5,3),
    rank_in_category INTEGER,
    UNIQUE(repo_id, snapshot_date)
);

-- Categories summary table
CREATE TABLE IF NOT EXISTS categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(50) UNIQUE NOT NULL,
    total_repos INTEGER,
    avg_stars DECIMAL(10,2),
    avg_activity_score DECIMAL(10,2),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_metrics_date ON metrics(snapshot_date);
CREATE INDEX IF NOT EXISTS idx_metrics_repo ON metrics(repo_id);
CREATE INDEX IF NOT EXISTS idx_repos_category ON repositories(category);
CREATE INDEX IF NOT EXISTS idx_repos_owner_name ON repositories(owner, repo_name);
