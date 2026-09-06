import os
import sys
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.security import generate_password_hash
from database.db import get_db_connection, init_db_schema, calculate_risk_level

def seed_database():
    """Seeds the SQLite database with rich realistic software project data."""
    conn = get_db_connection()
    cur = conn.cursor()
    # Drop existing tables to ensure clean schema sync
    tables = ['notifications', 'risk_history', 'mitigation_plans', 'risks', 'projects', 'categories', 'users', 'settings']
    for t in tables:
        cur.execute(f"DROP TABLE IF EXISTS {t}")
    conn.commit()
    conn.close()

    init_db_schema()
    conn = get_db_connection()
    cur = conn.cursor()

    # 1. Insert Users (Indian Demo Profiles)
    users_data = [
        (1, 'admin', 'rahul.patil@matrixpro.io', generate_password_hash('admin123'), 'Rahul Patil', 'Admin', 'Executive Suite', '#6366f1'),
        (2, 'risk_manager', 'priya.sharma@matrixpro.io', generate_password_hash('manager123'), 'Priya Sharma', 'Risk Manager', 'Risk & Governance', '#8b5cf6'),
        (3, 'dev_lead', 'amit.kulkarni@matrixpro.io', generate_password_hash('dev123'), 'Amit Kulkarni', 'Developer', 'Engineering Core', '#06b6d4'),
        (4, 'auditor', 'sneha.deshmukh@matrixpro.io', generate_password_hash('audit123'), 'Sneha Deshmukh', 'Auditor', 'QA & Compliance', '#ec4899')
    ]
    cur.executemany("""
        INSERT INTO users (id, username, email, password_hash, full_name, role, department, avatar_color)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, users_data)

    # 2. Insert Categories
    categories_data = [
        (1, 'Infrastructure & Availability', 'fa-server', '#6366f1', 'Server uptime, clustering, disaster recovery and hardware limits'),
        (2, 'Security & Compliance', 'fa-shield-halved', '#ef4444', 'Data protection, vulnerability management, zero trust and GDPR'),
        (3, 'Financial & Budget', 'fa-wallet', '#10b981', 'Cost forecasting, license spikes and resource allocation'),
        (4, 'Schedule & Delivery', 'fa-timeline', '#f59e0b', 'Sprint milestones, release blockers and critical path dependencies'),
        (5, 'Requirements & Scope', 'fa-arrows-split-up-and-left', '#8b5cf6', 'Feature creep, stakeholder misalignment and specifications churn'),
        (6, 'Human Capital & Skills', 'fa-users-gear', '#3b82f6', 'Staff retention, key person dependencies and domain ramp-up'),
        (7, 'Code Quality & Reliability', 'fa-bug-slash', '#ec4899', 'Technical debt, automated test coverage and zero regression goals'),
        (8, 'Third-Party & Vendor APIs', 'fa-cloud-arrow-down', '#06b6d4', 'SaaS integrations, rate limits, deprecations and SLA breaches'),
        (9, 'Data Governance & Storage', 'fa-database', '#14b8a6', 'Data corruption, replication failure, sync lag and retention'),
        (10, 'Product Adoption & UX', 'fa-chart-line-up', '#f97316', 'Onboarding drop-off, UX friction and user satisfaction metrics')
    ]
    cur.executemany("""
        INSERT INTO categories (id, name, icon, color, description)
        VALUES (?, ?, ?, ?, ?)
    """, categories_data)

    # 2.1 Insert Sample Software Project (Marked as is_demo = 1)
    projects_data = [
        (
            1, 'UPI & Cloud Banking Mobile App Gateway', 'Web & Mobile Application',
            'Next-generation retail banking mobile client and resilient cloud microservices API gateway.',
            'React Native, TypeScript, Node.js, PostgreSQL, AWS',
            8, 'Development', 'Cloud',
            '["Security", "Performance", "Budget", "Schedule", "Compliance", "Data", "Infrastructure"]',
            1, 'Rahul Patil'
        )
    ]
    cur.executemany("""
        INSERT INTO projects (id, name, project_type, description, tech_stack, team_size, stage, deployment_type, concerns, is_demo, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, projects_data)

    # 3. Insert Risks (Marked as is_demo = 1)
    # Format: (id, proj_id, name, description, cat_id, prob, impact, init_prob, init_imp, owner, dept, date_id, strat, mit_owner, target_date, status, is_demo)
    risks_raw = [
        (
            'RISK-001', 1, 'Server Downtime & Cloud Outage',
            'Unplanned production downtime caused by regional cloud data center failure or hypervisor disruption.',
            1, 2, 3, 3, 5, # curr prob 2, imp 3 (score 6, Med) from init prob 3, imp 5 (score 15, High)
            'Amit Kulkarni', 'Infrastructure', '2026-06-01',
            'Deploy active-active multi-region Kubernetes clusters with automated Route53 failover.',
            'Amit Kulkarni', '2026-09-15', 'In Progress', 1
        ),
        (
            'RISK-002', 1, 'Data Security Breach & Exfiltration',
            'Unauthorized access to tenant database records via credential stuffing or zero-day SQL injection.',
            2, 2, 5, 4, 5, # curr prob 2, imp 5 (score 10, High) from init prob 4, imp 5 (score 20, Critical)
            'Priya Sharma', 'Security', '2026-05-10',
            'Implement mandatory WebAuthn hardware keys, SOC-2 compliant encryption at rest (AES-256), and daily automated penetration scans.',
            'Priya Sharma', '2026-09-30', 'In Progress', 1
        ),
        (
            'RISK-003', 1, 'Budget Overrun on Cloud Compute',
            'Unmonitored auto-scaling clusters and unindexed vector search queries exceeding quarterly OpEx budget by >35%.',
            3, 2, 3, 4, 3, # curr prob 2, imp 3 (score 6, Med) from init prob 4, imp 3 (score 12, High)
            'Rahul Patil', 'Finance & IT', '2026-06-15',
            'Introduce granular AWS Budgets alerts, Kubecost pod allocation quotas, and nightly reserved instance pooling.',
            'Rahul Patil', '2026-08-30', 'Reduced', 1
        ),
        (
            'RISK-004', 1, 'Critical Path Schedule Delay',
            'Core backend microservices refactoring delaying Q3 mobile client beta rollout by 4 weeks.',
            4, 2, 4, 5, 4, # curr prob 2, imp 4 (score 8, Med) from init prob 5, imp 4 (score 20, Critical)
            'Sneha Deshmukh', 'Product Management', '2026-05-20',
            'Adopt feature flagging (LaunchDarkly) for trunk-based deployments and reallocate two senior developers from lower priority backlog.',
            'Sneha Deshmukh', '2026-09-01', 'In Progress', 1
        ),
        (
            'RISK-005', 1, 'Volatile Requirement Changes',
            'Stakeholder feedback causing scope churn and frequent mid-sprint acceptance criteria modifications.',
            5, 3, 4, 4, 4, # curr prob 3, imp 4 (score 12, High) from init prob 4, imp 4 (score 16, High)
            'Rahul Patil', 'Product', '2026-06-25',
            'Establish strict 2-week freeze windows before milestone releases and require executive sign-off for scope additions >8 story points.',
            'Rahul Patil', '2026-10-15', 'Assessed', 1
        ),
        (
            'RISK-006', 1, 'Senior Staff Shortage & Turnover',
            'Key person dependency on lead distributed systems engineer during crucial database sharding phase.',
            6, 1, 4, 3, 4, # curr prob 1, imp 4 (score 4, Low) from init prob 3, imp 4 (score 12, High)
            'Priya Sharma', 'Human Resources', '2026-04-12',
            'Conduct cross-training workshops, mandate architecture decision records (ADRs), and hire 2 contractor specialists.',
            'Priya Sharma', '2026-08-15', 'Closed', 1
        ),
        (
            'RISK-007', 1, 'Critical Software Bugs in Release',
            'High severity regressions slipping into production due to incomplete integration test coverage in checkout flow.',
            7, 1, 4, 4, 4, # curr prob 1, imp 4 (score 4, Low) from init prob 4, imp 4 (score 16, High)
            'Sneha Deshmukh', 'Quality Assurance', '2026-05-02',
            'Enforce 85% branch coverage gating on CI/CD pipelines and integrate automated Playwright end-to-end regression suites.',
            'Sneha Deshmukh', '2026-08-20', 'Reduced', 1
        ),
        (
            'RISK-008', 1, 'Third Party Payment API Outage',
            'Payment processor gateway latency spikes and throttling causing checkout abandonment during peak campaign.',
            8, 2, 3, 5, 3, # curr prob 2, imp 3 (score 6, Med) from init prob 5, imp 3 (score 15, High)
            'Amit Kulkarni', 'Engineering', '2026-06-18',
            'Implement dynamic multi-gateway failover (Stripe + Adyen) with asynchronous webhook queueing and exponential backoff retry.',
            'Amit Kulkarni', '2026-09-10', 'In Progress', 1
        ),
        (
            'RISK-009', 1, 'Catastrophic Data Loss in Cache/DB',
            'Loss of uncommitted user transaction state in Redis cluster during master replica desynchronization.',
            9, 1, 5, 4, 5, # curr prob 1, imp 5 (score 5, Med) from init prob 4, imp 5 (score 20, Critical)
            'Vikram Deshmukh', 'Data Engineering', '2026-04-30',
            'Enable continuous WAL point-in-time recovery (PITR) with automated hourly encrypted snapshots replicated to secondary cloud bucket.',
            'Vikram Deshmukh', '2026-08-01', 'Reduced', 1
        ),
        (
            'RISK-010', 1, 'Poor User Adoption & UX Friction',
            'Enterprise users struggling with complex navigation resulting in low daily active usage.',
            10, 2, 3, 3, 4, # curr prob 2, imp 3 (score 6, Med) from init prob 3, imp 4 (score 12, High)
            'Sneha Deshmukh', 'Product Design', '2026-07-01',
            'Deploy in-app interactive walkthroughs, simplify setup wizard down to 3 steps, and conduct weekly usability lab sessions.',
            'Sneha Deshmukh', '2026-10-01', 'In Progress', 1
        ),
        (
            'RISK-011', 1, 'Cloud Infrastructure Cost Spikes',
            'Uncapped serverless invocation rates during viral traffic bursts triggering unexpectedly high billing.',
            3, 1, 3, 3, 3, # curr prob 1, imp 3 (score 3, Low) from init prob 3, imp 3 (score 9, Med)
            'Amit Kulkarni', 'Infrastructure', '2026-07-15',
            'Configure API gateway rate limits, warm concurrency caps, and intelligent request throttling policies.',
            'Amit Kulkarni', '2026-08-28', 'Reduced', 1
        ),
        (
            'RISK-012', 1, 'Legacy Codebase Technical Debt',
            'Monolithic core modules hindering micro-frontend migration and slowing sprint velocity.',
            7, 2, 4, 4, 4, # curr prob 2, imp 4 (score 8, Med) from init prob 4, imp 4 (score 16, High)
            'Amit Kulkarni', 'Engineering', '2026-06-10',
            'Implement strangler fig pattern to gradually isolate modules into clean TypeScript packages with contract tests.',
            'Amit Kulkarni', '2026-11-30', 'Identified', 1
        )
    ]

    for r in risks_raw:
        r_id, proj_id, name, desc, cat_id, prob, imp, init_p, init_i, owner, dept, date_id, strat, mit_own, tgt_date, status, is_dm = r
        score = prob * imp
        level = calculate_risk_level(score)
        init_score = init_p * init_i
        cur.execute("""
            INSERT INTO risks (
                id, project_id, name, description, category_id, probability, impact, risk_score, risk_level,
                initial_probability, initial_impact, initial_score, owner, department, date_identified,
                mitigation_strategy, mitigation_owner, target_date, status, is_demo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (r_id, proj_id, name, desc, cat_id, prob, imp, score, level, init_p, init_i, init_score, owner, dept, date_id, strat, mit_own, tgt_date, status, is_dm))

    # 4. Insert Mitigation Plans (Marked as is_demo = 1)
    mitigations_data = [
        (
            'RISK-001', 'Multi-Region Kubernetes & Failover Mesh',
            '1. Deploy secondary EKS cluster in EU-West.\n2. Configure cross-region Aurora database replication.\n3. Run monthly simulated traffic drain drills.',
            'Amit Kulkarni', '2026-06-15', '2026-09-15', 'In Progress', 75,
            2, 3, 6, 'Secondary cluster provisioned; DNS failover automation in final staging validation.', 1
        ),
        (
            'RISK-002', 'Zero-Trust Access & Hardware Token Enforcement',
            '1. Mandate FIDO2/WebAuthn for all internal dashboards.\n2. Integrate Wiz.io cloud posture scanner.\n3. Conduct 3rd party black-box audit.',
            'Priya Sharma', '2026-05-15', '2026-09-30', 'In Progress', 65,
            2, 5, 10, 'FIDO2 rollout complete across 85% staff. Pen test scheduled for next week.', 1
        ),
        (
            'RISK-003', 'Automated FinOps Quotas & Idle Pod Pruner',
            '1. Set hard AWS budget thresholds at 80% with Slack alerting.\n2. Deploy KEDA autoscaling based on active connections.\n3. Convert 60% on-demand instances to 1-year savings plans.',
            'Rahul Patil', '2026-06-20', '2026-08-30', 'Completed', 100,
            2, 3, 6, 'Completed. Monthly cloud burn rate decreased by ₹1,40,000 (28% savings).', 1
        ),
        (
            'RISK-004', 'Trunk-Based Feature Flagging & Backlog Rebalancing',
            '1. Integrate LaunchDarkly flags to decouple deploy from release.\n2. Shift 2 backend engineers to core pipeline sprint.\n3. Eliminate merge freezes.',
            'Sneha Deshmukh', '2026-06-01', '2026-09-01', 'In Progress', 80,
            2, 4, 8, 'Feature flags live. Velocity increased by 32% over the last 2 sprints.', 1
        ),
        (
            'RISK-005', 'Formal Scope Lock & Impact Assessment Gate',
            '1. Implement mandatory change request impact calculator.\n2. Enforce 14-day pre-release code freeze.\n3. Stakeholder sign-off SLA.',
            'Rahul Patil', '2026-07-01', '2026-10-15', 'In Progress', 40,
            3, 4, 12, 'Policy draft approved by leadership. Tooling workflow under integration.', 1
        ),
        (
            'RISK-006', 'Knowledge Base & Mentorship Program',
            '1. Require ADRs for all RFCs.\n2. Pair programming 4 hours/week.\n3. Onboard 2 senior contract engineers.',
            'Priya Sharma', '2026-04-20', '2026-08-15', 'Completed', 100,
            1, 4, 4, 'Successfully cross-trained 4 engineers on distributed consensus layer.', 1
        ),
        (
            'RISK-007', 'Automated Playwright CI/CD Regression Gating',
            '1. Write 140 end-to-end user journey tests.\n2. Require PR status checks with 100% test pass rate.\n3. Add visual regression snapshot diffing.',
            'Sneha Deshmukh', '2026-05-10', '2026-08-20', 'Completed', 100,
            1, 4, 4, 'Test suite executes in under 6 minutes in parallel matrix. Zero major regressions in last 3 releases.', 1
        ),
        (
            'RISK-008', 'Dynamic Multi-Gateway Payment Orchestration',
            '1. Build smart routing microservice between Stripe and Adyen.\n2. Add local fallback caching for failed checkout attempts.\n3. Setup real-time webhook retries.',
            'Amit Kulkarni', '2026-06-25', '2026-09-10', 'In Progress', 70,
            2, 3, 6, 'Adyen fallback adapter in testing; Stripe fallback automated.', 1
        ),
        (
            'RISK-009', 'Point-In-Time Continuous Cloud Recovery',
            '1. Enable AWS Aurora continuous backup with 1-second granularity.\n2. Implement daily automated backup restore verification.\n3. Cross-region immutable S3 bucket lock.',
            'Vikram Deshmukh', '2026-05-05', '2026-08-01', 'Completed', 100,
            1, 5, 5, 'Restore drills verified with 4-minute RTO and 0-minute RPO.', 1
        ),
        (
            'RISK-010', 'Guided Interactive Onboarding & User Feedback Loop',
            '1. Embed step-by-step interactive product tour.\n2. Introduce contextual tooltips and search shortcuts.\n3. Implement in-app NPS and micro-surveys.',
            'Sneha Deshmukh', '2026-07-05', '2026-10-01', 'In Progress', 55,
            2, 3, 6, 'Tour implemented on 4 key screens; early user feedback up by 24%.', 1
        ),
        (
            'RISK-011', 'Rate Limiting & Concurrency Ceiling Enforcement',
            '1. Configure Cloudflare edge rate limiting rules.\n2. Cap Lambda reserved concurrency.\n3. Implement token bucket algorithm for API consumers.',
            'Amit Kulkarni', '2026-07-20', '2026-08-28', 'Completed', 100,
            1, 3, 3, 'Rate limiting actively blocking scrapers and rogue bots without impacting legitimate traffic.', 1
        ),
        (
            'RISK-012', 'Domain-Driven Strangler Pattern Refactoring',
            '1. Carve out authentication and billing into standalone microservices.\n2. Wrap legacy SQL calls in clean repository abstractions.\n3. Establish gRPC service contracts.',
            'Amit Kulkarni', '2026-06-15', '2026-11-30', 'In Progress', 35,
            2, 4, 8, 'Auth microservice extracted; billing pipeline extraction underway.', 1
        )
    ]

    cur.executemany("""
        INSERT INTO mitigation_plans (
            risk_id, strategy_name, action_steps, responsible_person, start_date, target_date,
            status, progress_pct, residual_probability, residual_impact, residual_score, notes, is_demo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, mitigations_data)

    # 5. Insert Risk History (Demonstrating continuous risk reduction over time milestones)
    # Format: (risk_id, date, prob, imp, new_score, level, prev_score, notes, recorded_by)
    history_records = [
        # RISK-001: 15 -> 12 -> 6
        ('RISK-001', '2026-06-01', 3, 5, 15, 'High', 15, 'Initial assessment: single availability zone vulnerability.', 'Amit Kulkarni'),
        ('RISK-001', '2026-07-01', 3, 4, 12, 'High', 15, 'Multi-AZ database setup completed. Secondary cluster deployment begun.', 'Amit Kulkarni'),
        ('RISK-001', '2026-08-01', 2, 3, 6, 'Medium', 12, 'Kubernetes cluster deployed in secondary region; failover tested in staging.', 'Amit Kulkarni'),

        # RISK-002: 20 -> 15 -> 10
        ('RISK-002', '2026-05-10', 4, 5, 20, 'Critical', 20, 'Initial assessment: audit highlighted legacy session tokens.', 'Priya Sharma'),
        ('RISK-002', '2026-06-15', 3, 5, 15, 'High', 20, 'Zero trust architecture approved and 2FA enforced for all staff.', 'Priya Sharma'),
        ('RISK-002', '2026-07-25', 2, 5, 10, 'High', 15, 'WebAuthn hardware tokens rolled out. Critical vulnerabilities patched.', 'Priya Sharma'),

        # RISK-003: 12 -> 9 -> 6
        ('RISK-003', '2026-06-15', 4, 3, 12, 'High', 12, 'Initial assessment: compute costs trending 40% above forecast.', 'Rahul Patil'),
        ('RISK-003', '2026-07-15', 3, 3, 9, 'Medium', 12, 'Kubecost alerting implemented; 12 unattached volumes deleted.', 'Rahul Patil'),
        ('RISK-003', '2026-08-15', 2, 3, 6, 'Medium', 9, 'Reserved instance coverage applied. Spending stabilized at target.', 'Rahul Patil'),

        # RISK-004: 20 -> 12 -> 8
        ('RISK-004', '2026-05-20', 5, 4, 20, 'Critical', 20, 'Initial assessment: major architectural blockers causing sprint slippage.', 'Sneha Deshmukh'),
        ('RISK-004', '2026-06-30', 3, 4, 12, 'High', 20, 'Trunk-based branch strategy implemented; 2 developers reassigned.', 'Sneha Deshmukh'),
        ('RISK-004', '2026-08-10', 2, 4, 8, 'Medium', 12, 'Feature flagging reduced merge conflicts; sprint velocity restored.', 'Sneha Deshmukh'),

        # RISK-006: 12 -> 8 -> 4
        ('RISK-006', '2026-04-12', 3, 4, 12, 'High', 12, 'Initial assessment: single engineer holds all domain knowledge of consensus engine.', 'Priya Sharma'),
        ('RISK-006', '2026-06-01', 2, 4, 8, 'Medium', 12, 'Pairing sessions completed and comprehensive documentation drafted.', 'Priya Sharma'),
        ('RISK-006', '2026-07-20', 1, 4, 4, 'Low', 8, 'Two additional engineers fully onboarded and autonomous.', 'Priya Sharma'),

        # RISK-007: 16 -> 8 -> 4
        ('RISK-007', '2026-05-02', 4, 4, 16, 'High', 16, 'Initial assessment: manual regression testing taking 3 days per release.', 'Sneha Deshmukh'),
        ('RISK-007', '2026-06-20', 2, 4, 8, 'Medium', 16, '80 Playwright integration tests added to automated GitHub Actions.', 'Sneha Deshmukh'),
        ('RISK-007', '2026-08-01', 1, 4, 4, 'Low', 8, '140 tests now running per pull request; zero critical bugs in prod.', 'Sneha Deshmukh'),

        # RISK-008: 15 -> 9 -> 6
        ('RISK-008', '2026-06-18', 5, 3, 15, 'High', 15, 'Initial assessment: single payment provider outages direct cause of lost orders.', 'Amit Kulkarni'),
        ('RISK-008', '2026-07-20', 3, 3, 9, 'Medium', 15, 'Secondary payment gateway SDK integrated in sandbox.', 'Amit Kulkarni'),
        ('RISK-008', '2026-08-20', 2, 3, 6, 'Medium', 9, 'Automated fallback router deployed in canary test to 20% traffic.', 'Amit Kulkarni'),

        # RISK-009: 20 -> 10 -> 5
        ('RISK-009', '2026-04-30', 4, 5, 20, 'Critical', 20, 'Initial assessment: Redis snapshot recovery was untested and manual.', 'Vikram Deshmukh'),
        ('RISK-009', '2026-06-10', 2, 5, 10, 'High', 20, 'Continuous replication enabled with daily automated restore drill.', 'Vikram Deshmukh'),
        ('RISK-009', '2026-07-25', 1, 5, 5, 'Medium', 10, 'Cross-region immutable backup active; RTO validated under 4 minutes.', 'Vikram Deshmukh'),

        # RISK-010: 12 -> 6
        ('RISK-010', '2026-07-01', 3, 4, 12, 'High', 12, 'Initial assessment: 42% drop-off in user onboarding flow.', 'Sneha Deshmukh'),
        ('RISK-010', '2026-08-10', 2, 3, 6, 'Medium', 12, 'Interactive guided tour launched; drop-off reduced to 18%.', 'Sneha Deshmukh')
    ]

    cur.executemany("""
        INSERT INTO risk_history (
            risk_id, recorded_date, probability, impact, risk_score, risk_level, previous_score, notes, recorded_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, history_records)

    # 6. Insert Notifications
    notifications_data = [
        (1, 'Critical Risk Mitigated', 'RISK-007 (Software Bugs) successfully reduced from High (16) to Low (4) after CI/CD test automation rollout.', 'success', 0),
        (1, 'Target Date Approaching', 'RISK-004 (Schedule Delay) mitigation plan target date is within 3 days (2026-09-01).', 'warning', 0),
        (2, 'Security Audit In Progress', 'Quarterly SOC-2 penetration audit for RISK-002 is scheduled for Friday 10:00 AM.', 'info', 0),
        (1, 'FinOps Milestone Achieved', 'RISK-003 (Budget Overrun) reached 100% progress and saved $14,200 this billing cycle.', 'success', 1),
        (3, 'High Risk Attention Required', 'RISK-005 (Requirement Changes) remains in Open status with a Risk Score of 12.', 'critical', 0)
    ]
    cur.executemany("""
        INSERT INTO notifications (user_id, title, message, type, is_read)
        VALUES (?, ?, ?, ?, ?)
    """, notifications_data)

    # 7. Insert Settings
    settings_data = [
        ('system_title', 'Software Risk Mitigation Matrix Pro', 'Application title displayed across headers and reports'),
        ('threshold_critical', '17', 'Minimum score for Critical risk band (17 - 25)'),
        ('threshold_high', '10', 'Minimum score for High risk band (10 - 16)'),
        ('threshold_medium', '5', 'Minimum score for Medium risk band (5 - 9)'),
        ('threshold_low', '1', 'Minimum score for Low risk band (1 - 4)'),
        ('default_theme', 'dark', 'Default UI theme for new sessions'),
        ('company_name', 'CloudScale Technologies Inc.', 'Organization name for executive reports'),
        ('last_audit_date', '2026-08-25', 'Date of most recent comprehensive risk review')
    ]
    cur.executemany("""
        INSERT INTO settings (key, value, description)
        VALUES (?, ?, ?)
    """, settings_data)

    conn.commit()
    conn.close()
    print("Database successfully initialized and seeded with rich sample data!")

if __name__ == '__main__':
    seed_database()
