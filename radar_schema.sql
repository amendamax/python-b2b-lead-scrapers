-- Schema for Radar Network Indexing System

CREATE TABLE IF NOT EXISTS urls_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  site_id TEXT NOT NULL,         -- 'pillscam', 'broker', 'dating', 'jobscam', 'appscam'
  url TEXT UNIQUE NOT NULL,
  is_indexed INTEGER DEFAULT 0,
  indexed_at TEXT,
  last_error TEXT
);

CREATE INDEX IF NOT EXISTS idx_site_pending ON urls_queue (site_id, is_indexed, id);
CREATE INDEX IF NOT EXISTS idx_site_url ON urls_queue (site_id, url);

CREATE TABLE IF NOT EXISTS indexing_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  site_id TEXT NOT NULL,
  status TEXT NOT NULL,          -- 'SUCCESS', 'QUOTA_EXCEEDED', 'ERROR'
  urls_count INTEGER NOT NULL,
  details TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_logs_site_time ON indexing_logs (site_id, created_at);
