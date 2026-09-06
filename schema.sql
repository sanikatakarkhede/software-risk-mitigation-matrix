-- Software Risk Mitigation Matrix Database Schema
-- SQLite3

PRAGMA foreign_keys = ON;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'Risk Manager', -- 'Admin', 'Risk Manager', 'Developer', 'Auditor'
    department TEXT DEFAULT 'Engineering',
    avatar_color TEXT DEFAULT '#6366f1',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Categories Table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    icon TEXT NOT NULL DEFAULT 'fa-folder',
    color TEXT NOT NULL DEFAULT '#6366f1',
    description TEXT
);

-- Projects Table
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    project_type TEXT DEFAULT 'Web Application',
    description TEXT,
    tech_stack TEXT,
    team_size INTEGER DEFAULT 5,
    stage TEXT DEFAULT 'Development', -- 'Planning', 'Development', 'Testing', 'Deployment', 'Maintenance'
    deployment_type TEXT DEFAULT 'Cloud', -- 'Cloud', 'On-Premise', 'Hybrid'
    concerns TEXT, -- JSON array / comma-separated list of selected concern areas
    is_demo INTEGER DEFAULT 0,
    created_by TEXT DEFAULT 'Admin',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Risks Table
CREATE TABLE IF NOT EXISTS risks (
    id TEXT PRIMARY KEY, -- e.g. 'RISK-001'
    project_id INTEGER,
    name TEXT NOT NULL,
    description TEXT,
    category_id INTEGER NOT NULL,
    probability INTEGER NOT NULL CHECK(probability BETWEEN 1 AND 5),
    impact INTEGER NOT NULL CHECK(impact BETWEEN 1 AND 5),
    risk_score INTEGER NOT NULL CHECK(risk_score BETWEEN 1 AND 25),
    risk_level TEXT NOT NULL, -- 'Low', 'Medium', 'High', 'Critical'
    initial_probability INTEGER NOT NULL DEFAULT 1,
    initial_impact INTEGER NOT NULL DEFAULT 1,
    initial_score INTEGER NOT NULL DEFAULT 1,
    owner TEXT NOT NULL,
    department TEXT NOT NULL,
    date_identified DATE NOT NULL,
    mitigation_strategy TEXT,
    mitigation_owner TEXT,
    target_date DATE,
    status TEXT NOT NULL DEFAULT 'Assessed', -- 'Identified', 'Assessed', 'Mitigation Planned', 'In Progress', 'Under Review', 'Reduced', 'Closed'
    is_demo INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
);

-- Mitigation Plans Table
CREATE TABLE IF NOT EXISTS mitigation_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    risk_id TEXT NOT NULL,
    strategy_name TEXT NOT NULL,
    action_steps TEXT,
    responsible_person TEXT NOT NULL,
    start_date DATE NOT NULL,
    target_date DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'In Progress', -- 'Planned', 'In Progress', 'Completed', 'On Hold'
    progress_pct INTEGER NOT NULL DEFAULT 0 CHECK(progress_pct BETWEEN 0 AND 100),
    residual_probability INTEGER CHECK(residual_probability BETWEEN 1 AND 5),
    residual_impact INTEGER CHECK(residual_impact BETWEEN 1 AND 5),
    residual_score INTEGER CHECK(residual_score BETWEEN 1 AND 25),
    notes TEXT,
    is_demo INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (risk_id) REFERENCES risks(id) ON DELETE CASCADE
);

-- Risk History Timeline Table
CREATE TABLE IF NOT EXISTS risk_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    risk_id TEXT NOT NULL,
    recorded_date DATE NOT NULL,
    probability INTEGER NOT NULL CHECK(probability BETWEEN 1 AND 5),
    impact INTEGER NOT NULL CHECK(impact BETWEEN 1 AND 5),
    risk_score INTEGER NOT NULL CHECK(risk_score BETWEEN 1 AND 25),
    risk_level TEXT NOT NULL,
    previous_score INTEGER,
    notes TEXT,
    recorded_by TEXT DEFAULT 'System',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (risk_id) REFERENCES risks(id) ON DELETE CASCADE
);

-- Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'info', -- 'critical', 'warning', 'info', 'success'
    is_read BOOLEAN NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Application Settings / Configuration Table
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT
);

-- Indexes for optimal performance
CREATE INDEX IF NOT EXISTS idx_risks_status ON risks(status);
CREATE INDEX IF NOT EXISTS idx_risks_level ON risks(risk_level);
CREATE INDEX IF NOT EXISTS idx_risks_category ON risks(category_id);
CREATE INDEX IF NOT EXISTS idx_risks_project ON risks(project_id);
CREATE INDEX IF NOT EXISTS idx_mitigation_risk ON mitigation_plans(risk_id);
CREATE INDEX IF NOT EXISTS idx_history_risk ON risk_history(risk_id);
