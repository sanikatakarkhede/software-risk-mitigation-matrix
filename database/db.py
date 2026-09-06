import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database.db')
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')

def get_db_connection():
    """Returns a SQLite connection with row_factory set to sqlite3.Row and foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db_schema():
    """Initializes the database tables from schema.sql."""
    conn = get_db_connection()
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

def query_db(query, args=(), one=False):
    """Executes a parameterized query and returns dicts or a single dict."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    conn.close()
    if one:
        return dict(rv[0]) if rv else None
    return [dict(row) for row in rv]

def execute_db(query, args=()):
    """Executes an INSERT/UPDATE/DELETE query and commits changes."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    last_id = cur.lastrowid
    rowcount = cur.rowcount
    cur.close()
    conn.close()
    return last_id, rowcount

def calculate_risk_level(score):
    """
    Standard Matrix Risk Banding:
    1 - 4: Low (Green)
    5 - 9: Medium (Yellow/Amber)
    10 - 16: High (Orange)
    17 - 25: Critical (Red)
    """
    score = int(score) if score is not None else 1
    if score >= 17:
        return 'Critical'
    elif score >= 10:
        return 'High'
    elif score >= 5:
        return 'Medium'
    else:
        return 'Low'

def calculate_risk_reduction(initial_score, current_score):
    """
    Unified Individual Risk Reduction Formula:
    ((Initial Score - Current Score) / Initial Score) * 100
    """
    init = float(initial_score) if initial_score else 1.0
    curr = float(current_score) if current_score is not None else 0.0
    if init <= 0:
        return 0.0
    reduction = ((init - curr) / init) * 100.0
    return max(0.0, round(reduction, 1))

def get_suggested_mitigation(category_name, threat_description=""):
    """
    Returns a practical software engineering mitigation strategy and action steps
    based on the domain area and risk context.
    """
    cat_lower = (category_name or '').lower()
    
    suggestions = {
        'security': {
            'strategy': 'Review access permissions and enable multi-factor authentication',
            'action_steps': '1. Enforce strict role-based access control (RBAC) and least privilege.\n2. Enable mandatory multi-factor authentication (MFA/FIDO2).\n3. Schedule quarterly external penetration tests and automated dependency vulnerability scans.'
        },
        'performance': {
            'strategy': 'Add performance testing and monitor response times',
            'action_steps': '1. Establish automated k6/Locust load testing in staging pipeline.\n2. Optimize high-latency database queries and add missing indexes.\n3. Configure APM distributed tracing and p95/p99 latency alerting.'
        },
        'requirements': {
            'strategy': 'Introduce requirement review and change approval',
            'action_steps': '1. Define clear acceptance criteria and Definition of Done for each user story.\n2. Enforce 2-week freeze window prior to major release milestones.\n3. Require product owner and engineering lead sign-off for scope changes.'
        },
        'schedule': {
            'strategy': 'Add milestone tracking and review schedule dependencies',
            'action_steps': '1. Implement critical path mapping and weekly milestone review meetings.\n2. Decouple blocking backend dependencies using feature flagging.\n3. Add 15% buffer time before customer delivery milestones.'
        },
        'budget': {
            'strategy': 'Monitor project costs and establish budget alerts',
            'action_steps': '1. Set up cloud budget alerts at 75% and 90% thresholds.\n2. Implement nightly idle server instance auto-shutdown policies.\n3. Review third-party SaaS subscription usage quarterly.'
        },
        'team': {
            'strategy': 'Conduct technical cross-training and document critical workflows',
            'action_steps': '1. Mandate Architecture Decision Records (ADRs) for design changes.\n2. Schedule 4 hours weekly of pair-programming on core services.\n3. Maintain updated runbooks for deployment and incident response.'
        },
        'technology': {
            'strategy': 'Enforce branch test coverage gating and automated static analysis',
            'action_steps': '1. Gating rule: 80% automated unit and integration test coverage on PRs.\n2. Integrate SonarQube / ESLint static analysis in CI/CD pipeline.\n3. Schedule dedicated 20% refactoring sprints for technical debt.'
        },
        'third-party': {
            'strategy': 'Implement API circuit breakers, exponential backoff, and fallback queues',
            'action_steps': '1. Wrap external vendor API calls in circuit breaker and timeout wrappers.\n2. Add asynchronous retry queues with exponential backoff and jitter.\n3. Integrate secondary fallback vendor SDKs where available.'
        },
        'data': {
            'strategy': 'Enable continuous point-in-time recovery and snapshot replication',
            'action_steps': '1. Enable automated daily database backups with point-in-time recovery (PITR).\n2. Replicate encrypted snapshots to secondary multi-region cloud storage.\n3. Run monthly automated backup restore verification drills.'
        },
        'infrastructure': {
            'strategy': 'Deploy high-availability multi-zone clusters with health-check failover',
            'action_steps': '1. Provision redundant nodes across at least 2 availability zones.\n2. Configure automated health checks and auto-restart container policies.\n3. Implement automated DNS traffic routing and multi-region failover.'
        },
        'compliance': {
            'strategy': 'Align controls with ISO 27001 / SOC 2 requirements and automate audit trails',
            'action_steps': '1. Map software controls to compliance framework requirements.\n2. Enable immutable audit logging for all administrative actions.\n3. Conduct pre-audit readiness reviews semi-annually.'
        }
    }

    # Match category keyword
    for key, val in suggestions.items():
        if key in cat_lower:
            return val

    # Default fallback
    return {
        'strategy': 'Establish structured monitoring, peer review, and mitigation SLAs',
        'action_steps': '1. Define specific measurable mitigation milestones with assigned owners.\n2. Review risk posture weekly in sprint planning and governance meetings.\n3. Validate risk reduction through operational testing and reassessment.'
    }

def get_portfolio_metrics():
    """
    Calculates unified portfolio-level risk governance metrics directly from database records.
    Formula:
    Overall Risk Reduction % = ((Total Initial Score - Total Current Score) / Total Initial Score) * 100
    """
    stats = query_db("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN risk_level = 'Critical' THEN 1 ELSE 0 END) as critical_count,
            SUM(CASE WHEN risk_level = 'High' THEN 1 ELSE 0 END) as high_count,
            SUM(CASE WHEN risk_level = 'Medium' THEN 1 ELSE 0 END) as medium_count,
            SUM(CASE WHEN risk_level = 'Low' THEN 1 ELSE 0 END) as low_count,
            SUM(CASE WHEN status IN ('Identified', 'Open') THEN 1 ELSE 0 END) as open_count,
            SUM(CASE WHEN status IN ('Assessed', 'Mitigation Planned', 'In Progress', 'Under Review') THEN 1 ELSE 0 END) as in_progress_count,
            SUM(CASE WHEN status IN ('Reduced', 'Mitigated') THEN 1 ELSE 0 END) as mitigated_count,
            SUM(CASE WHEN status = 'Closed' THEN 1 ELSE 0 END) as closed_count,
            SUM(CASE WHEN is_demo = 1 THEN 1 ELSE 0 END) as demo_count,
            SUM(CASE WHEN is_demo = 0 THEN 1 ELSE 0 END) as user_count,
            COALESCE(SUM(initial_score), 0) as total_initial_score,
            COALESCE(SUM(risk_score), 0) as total_current_score,
            ROUND(AVG(risk_score), 1) as avg_score,
            ROUND(AVG(initial_score), 1) as avg_initial_score
        FROM risks
    """, one=True) or {}

    total_init = float(stats.get('total_initial_score') or 0)
    total_curr = float(stats.get('total_current_score') or 0)
    
    if total_init > 0:
        overall_reduction_pct = max(0.0, round(((total_init - total_curr) / total_init) * 100.0, 1))
    else:
        overall_reduction_pct = 0.0

    points_mitigated = max(0, int(total_init - total_curr))
    critical_count = stats.get('critical_count') or 0
    high_count = stats.get('high_count') or 0
    attention_count = critical_count + high_count

    return {
        'total': stats.get('total') or 0,
        'demo_count': stats.get('demo_count') or 0,
        'user_count': stats.get('user_count') or 0,
        'critical_count': critical_count,
        'high_count': high_count,
        'medium_count': stats.get('medium_count') or 0,
        'low_count': stats.get('low_count') or 0,
        'open_count': stats.get('open_count') or 0,
        'in_progress_count': stats.get('in_progress_count') or 0,
        'mitigated_count': stats.get('mitigated_count') or 0,
        'closed_count': stats.get('closed_count') or 0,
        'total_initial_score': int(total_init),
        'total_current_score': int(total_curr),
        'avg_score': stats.get('avg_score') or 0.0,
        'avg_initial_score': stats.get('avg_initial_score') or 0.0,
        'overall_reduction_pct': overall_reduction_pct,
        'points_mitigated': points_mitigated,
        'attention_count': attention_count
    }


