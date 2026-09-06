import os
import io
import csv
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, jsonify, redirect,
    url_for, session, make_response, send_file, flash
)
from werkzeug.security import check_password_hash, generate_password_hash
from database.db import (
    get_db_connection, query_db, execute_db,
    calculate_risk_level, calculate_risk_reduction, get_portfolio_metrics,
    get_suggested_mitigation
)
from database.init_db import seed_database

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'matrix-super-secret-risk-key-2026-cse')

# Ensure database exists and enforce authentication before requests
@app.before_request
def ensure_db_and_auth():
    if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')):
        seed_database()

    # Public endpoints that do not require authentication
    public_endpoints = {'login', 'register', 'demo_login', 'static'}
    if app.config.get('TESTING'):
        return

    if request.endpoint and request.endpoint not in public_endpoints:
        if 'user_id' not in session:
            return redirect(url_for('register'))

# Context processor for global template variables (current user, categories, notifications, portfolio metrics)
@app.context_processor
def inject_globals():
    user = None
    if 'user_id' in session:
        user = query_db("SELECT id, username, full_name, email, role, department, avatar_color FROM users WHERE id = ?", (session['user_id'],), one=True)
    elif app.config.get('TESTING'):
        user = {
            'id': 1,
            'username': 'admin',
            'full_name': 'Rahul Patil',
            'email': 'admin@riskmanager.io',
            'role': 'Admin',
            'department': 'Executive Suite',
            'avatar_color': '#2563eb'
        }
    
    categories = query_db("SELECT * FROM categories ORDER BY id ASC")
    unread_notifs = query_db("SELECT * FROM notifications WHERE is_read = 0 ORDER BY created_at DESC LIMIT 5")
    
    # Calculate global risk metrics directly from SQLite database
    portfolio_metrics = get_portfolio_metrics()

    return {
        'current_user': user,
        'all_categories': categories,
        'global_stats': portfolio_metrics,
        'portfolio_metrics': portfolio_metrics,
        'unread_notifications': unread_notifs,
        'now_year': datetime.now().year
    }

# -------------------------------------------------------------
# Authentication Routes
# -------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        remember = request.form.get('remember') == 'on'

        user = query_db("SELECT * FROM users WHERE username = ? OR email = ?", (username, username), one=True)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session.permanent = remember
            flash(f"Welcome back, {user['full_name']}!", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials. Please check your username and password, or use 1-Click Demo Login.", 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        role = request.form.get('role', 'Risk Manager').strip()
        department = request.form.get('department', 'Engineering').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not full_name or not email or not password:
            flash("Please complete all required fields.", 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash("Passwords do not match. Please verify and try again.", 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash("Password must be at least 6 characters in length.", 'error')
            return render_template('register.html')

        # Check existing username/email
        existing = query_db("SELECT id FROM users WHERE email = ?", (email,), one=True)
        if existing:
            flash("An account with this email address already exists. Please sign in.", 'error')
            return redirect(url_for('login'))

        username = email.split('@')[0].lower().replace('.', '_').replace('-', '_')
        # Ensure unique username
        u_check = query_db("SELECT id FROM users WHERE username = ?", (username,), one=True)
        if u_check:
            username = f"{username}_{int(datetime.now().timestamp()) % 10000}"

        avatar_colors = ['#6366f1', '#8b5cf6', '#06b6d4', '#ec4899', '#10b981', '#f59e0b']
        color = avatar_colors[len(full_name) % len(avatar_colors)]

        user_id, _ = execute_db("""
            INSERT INTO users (username, email, password_hash, full_name, role, department, avatar_color)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (username, email, generate_password_hash(password), full_name, role, department, color))

        session['user_id'] = user_id
        session['username'] = username
        session['role'] = role
        flash(f"Account registered successfully! Welcome to RiskManager, {full_name}.", 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been signed out successfully.", 'info')
    return redirect(url_for('login'))

@app.route('/api/demo-login/<role>', methods=['POST'])
def demo_login(role):
    role_map = {
        'admin': 'admin',
        'manager': 'risk_manager',
        'dev': 'dev_lead',
        'auditor': 'auditor'
    }
    target_username = role_map.get(role, 'admin')
    user = query_db("SELECT * FROM users WHERE username = ?", (target_username,), one=True)
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        return jsonify({'success': True, 'message': f'Logged in as {user["full_name"]} ({user["role"]})', 'redirect': url_for('dashboard')})
    return jsonify({'success': False, 'message': 'User not found'}), 404

# -------------------------------------------------------------
# Frontend Page Views
# -------------------------------------------------------------
@app.route('/')
@app.route('/dashboard')
def dashboard():
    # Overall summary metrics from shared calculation
    portfolio = get_portfolio_metrics()

    # Recent risks list
    recent_risks = query_db("""
        SELECT r.*, c.name as category_name, c.color as category_color, c.icon as category_icon,
               COALESCE(p.name, 'Default Project') as project_name
        FROM risks r
        JOIN categories c ON r.category_id = c.id
        LEFT JOIN projects p ON r.project_id = p.id
        ORDER BY r.updated_at DESC, r.risk_score DESC
        LIMIT 6
    """)

    # Mitigation stats
    mitigation_stats = query_db("""
        SELECT 
            COUNT(*) as total_plans,
            ROUND(AVG(progress_pct), 0) as avg_progress,
            SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_plans,
            SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress_plans
        FROM mitigation_plans
    """, one=True) or {}

    return render_template(
        'dashboard.html',
        stats=portfolio,
        portfolio=portfolio,
        risk_reduction_pct=portfolio['overall_reduction_pct'],
        recent_risks=recent_risks,
        mitigation_stats=mitigation_stats,
        page_title="Executive Risk Dashboard"
    )

@app.route('/matrix')
def matrix_view():
    return render_template('matrix.html', page_title="Interactive 5×5 Risk Matrix")

@app.route('/risks')
def risks_view():
    categories = query_db("SELECT * FROM categories ORDER BY name ASC")
    projects = query_db("SELECT id, name FROM projects ORDER BY name ASC")
    return render_template('risks.html', categories=categories, projects=projects, page_title="Risk Management Repository")

@app.route('/assessment')
@app.route('/projects/new')
def assessment_view():
    categories = query_db("SELECT * FROM categories ORDER BY id ASC")
    users = query_db("SELECT id, full_name, role, department FROM users ORDER BY full_name ASC")
    projects = query_db("""
        SELECT p.*, COUNT(r.id) as risk_count, ROUND(AVG(r.risk_score), 1) as avg_score
        FROM projects p
        LEFT JOIN risks r ON p.id = r.project_id
        GROUP BY p.id
        ORDER BY p.created_at DESC
    """)
    return render_template(
        'assessment.html',
        categories=categories,
        users=users,
        projects=projects,
        page_title="Project Risk Assessment"
    )

@app.route('/monitoring')
def monitoring_view():
    status_filter = request.args.get('status', '').strip()
    categories = query_db("SELECT * FROM categories ORDER BY name ASC")
    
    query = """
        SELECT r.*, c.name as category_name, c.color as category_color, c.icon as category_icon,
               COALESCE(p.name, 'Cloud Banking Mobile App & API Gateway') as project_name,
               COALESCE(p.id, 1) as proj_id
        FROM risks r
        JOIN categories c ON r.category_id = c.id
        LEFT JOIN projects p ON r.project_id = p.id
    """
    params = []
    if status_filter:
        query += " WHERE r.status = ?"
        params.append(status_filter)
    query += " ORDER BY r.risk_score DESC, r.updated_at DESC"
    
    risks = query_db(query, tuple(params))
    
    for idx, r in enumerate(risks):
        # Format display id number e.g. #9 | SBMS-2026
        clean_num = r['id'].replace('RISK-', '') if isinstance(r['id'], str) else str(idx + 1)
        r['display_num'] = clean_num.lstrip('0') or '1'
        r['project_code'] = 'SBMS-2026' if int(clean_num or '1') % 2 == 1 else 'EMP-2026'

    return render_template(
        'monitoring.html',
        risks=risks,
        current_status=status_filter,
        categories=categories,
        page_title="Risk Monitoring & Lifecycle Console"
    )

@app.route('/mapping')
def mapping_view():
    categories = query_db("SELECT * FROM categories ORDER BY name ASC")
    projects = query_db("SELECT id, name FROM projects ORDER BY name ASC")
    
    # Query all mapped risk and mitigation records
    mappings = query_db("""
        SELECT r.id as risk_id, r.name as risk_name, r.risk_score, r.risk_level, r.initial_score,
               r.status as risk_status, r.owner as risk_owner, r.department, r.date_identified,
               c.name as category_name, c.color as category_color, c.icon as category_icon,
               COALESCE(p.name, 'Cloud Banking Mobile App & API Gateway') as project_name,
               m.id as mitigation_id, m.strategy_name, m.action_steps, m.responsible_person as mitigation_owner,
               m.progress_pct, m.status as mitigation_status, m.target_date
        FROM risks r
        JOIN categories c ON r.category_id = c.id
        LEFT JOIN projects p ON r.project_id = p.id
        LEFT JOIN mitigation_plans m ON r.id = m.risk_id
        ORDER BY r.risk_score DESC, m.progress_pct ASC
    """)

    for item in mappings:
        init_s = item.get('initial_score') or item.get('risk_score') or 1
        curr_s = item.get('risk_score') or 0
        item['reduction_pct'] = calculate_risk_reduction(init_s, curr_s)
        item['points_mitigated'] = max(0, init_s - curr_s)

    portfolio = get_portfolio_metrics()

    return render_template(
        'mapping.html',
        mappings=mappings,
        categories=categories,
        projects=projects,
        portfolio=portfolio,
        page_title="Risk ↔ Mitigation Mapping"
    )

@app.route('/risks/<risk_id>')
def risk_details(risk_id):
    risk = query_db("""
        SELECT r.*, c.name as category_name, c.color as category_color, c.icon as category_icon,
               COALESCE(p.name, 'Cloud Banking Mobile App & API Gateway') as project_name
        FROM risks r
        JOIN categories c ON r.category_id = c.id
        LEFT JOIN projects p ON r.project_id = p.id
        WHERE r.id = ?
    """, (risk_id,), one=True)
    
    if not risk:
        flash(f"Risk ID '{risk_id}' not found.", 'error')
        return redirect(url_for('risks_view'))

    # Calculate individual reduction % using unified formula
    init_score = risk['initial_score'] or (risk['initial_probability'] * risk['initial_impact']) or 1
    curr_score = risk['risk_score']
    reduction_pct = calculate_risk_reduction(init_score, curr_score)

    # Mitigation plans for this risk
    mitigations = query_db("""
        SELECT * FROM mitigation_plans WHERE risk_id = ? ORDER BY created_at DESC
    """, (risk_id,))

    # History timeline
    history = query_db("""
        SELECT * FROM risk_history WHERE risk_id = ? ORDER BY recorded_date ASC, id ASC
    """, (risk_id,))

    # Build sequence progression list: e.g. [15, 12, 6]
    score_sequence = []
    if history:
        for h in history:
            score_sequence.append(h['risk_score'])
    else:
        score_sequence = [init_score, curr_score]

    # Calculate "What Changed?" summary
    what_changed = None
    if history and len(history) > 1:
        latest = history[-1]
        prev_s = latest['previous_score'] if latest.get('previous_score') else history[-2]['risk_score']
        curr_s = latest['risk_score']
        pt_diff = prev_s - curr_s
        if pt_diff > 0:
            change_text = f"Risk score reduced from {prev_s} to {curr_s} (-{pt_diff} pts) after mitigation milestone was executed."
        elif pt_diff < 0:
            change_text = f"Risk score increased from {prev_s} to {curr_s} (+{abs(pt_diff)} pts) during reassessment review."
        else:
            change_text = f"Risk score maintained at {curr_s} ({latest['risk_level']} Severity) following audit verification."
        
        what_changed = {
            'text': change_text,
            'previous_score': prev_s,
            'current_score': curr_s,
            'reason': latest['notes'],
            'updated_by': latest['recorded_by'],
            'updated_date': latest['recorded_date'],
            'current_status': risk['status']
        }
    elif history and len(history) == 1:
        latest = history[0]
        what_changed = {
            'text': f"Risk baseline established at score {latest['risk_score']} ({latest['risk_level']} Severity).",
            'previous_score': latest['risk_score'],
            'current_score': latest['risk_score'],
            'reason': latest['notes'] or 'Initial project risk assessment baseline.',
            'updated_by': latest['recorded_by'],
            'updated_date': latest['recorded_date'],
            'current_status': risk['status']
        }
    else:
        what_changed = {
            'text': f"Current risk score is {curr_score} ({risk['risk_level']} Severity).",
            'previous_score': init_score,
            'current_score': curr_score,
            'reason': risk['mitigation_strategy'] or 'Active governance monitoring.',
            'updated_by': risk['owner'],
            'updated_date': risk['date_identified'],
            'current_status': risk['status']
        }

    return render_template(
        'risk-details.html',
        risk=risk,
        reduction_pct=reduction_pct,
        mitigations=mitigations,
        history=history,
        score_sequence=score_sequence,
        what_changed=what_changed,
        page_title=f"Risk Details - {risk['id']}"
    )

@app.route('/mitigation')
def mitigation_view():
    mitigations = query_db("""
        SELECT m.*, r.name as risk_name, r.risk_level, r.risk_score, r.probability, r.impact,
               r.initial_score, r.initial_probability, r.initial_impact,
               c.name as category_name, c.color as category_color
        FROM mitigation_plans m
        JOIN risks r ON m.risk_id = r.id
        JOIN categories c ON r.category_id = c.id
        ORDER BY m.progress_pct ASC, r.risk_score DESC
    """)
    for m in mitigations:
        init_s = m.get('initial_score') or ((m.get('initial_probability') or 1) * (m.get('initial_impact') or 1))
        curr_s = m.get('risk_score') or 0
        m['reduction_pct'] = calculate_risk_reduction(init_s, curr_s)
        m['points_mitigated'] = max(0, init_s - curr_s)

    risks_list = query_db("SELECT id, name, risk_score, risk_level, initial_score FROM risks ORDER BY id ASC")
    portfolio = get_portfolio_metrics()
    return render_template(
        'mitigation.html',
        mitigations=mitigations,
        risks_list=risks_list,
        portfolio=portfolio,
        page_title="Mitigation Strategies & Action Plans"
    )

@app.route('/analytics')
def analytics_view():
    portfolio = get_portfolio_metrics()
    return render_template('analytics.html', portfolio=portfolio, page_title="Risk Analytics & Trends Intelligence")

@app.route('/reports')
def reports_view():
    portfolio = get_portfolio_metrics()
    return render_template('reports.html', portfolio=portfolio, page_title="Risk Reports & Compliance Audits")

@app.route('/settings')
def settings_view():
    settings_rows = query_db("SELECT * FROM settings")
    settings_dict = {row['key']: row['value'] for row in settings_rows}
    users = query_db("SELECT id, username, full_name, email, role, department, avatar_color, created_at FROM users")
    return render_template('settings.html', settings=settings_dict, users=users, page_title="System Configuration & Preferences")

# -------------------------------------------------------------
# RESTful API Endpoints
# -------------------------------------------------------------
@app.route('/api/stats', methods=['GET'])
def get_stats():
    portfolio = get_portfolio_metrics()
    return jsonify(portfolio)


@app.route('/api/risks', methods=['GET'])
def get_risks():
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    level = request.args.get('level', '').strip()
    status = request.args.get('status', '').strip()
    project_id = request.args.get('project_id', '').strip()
    sort_by = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc').lower()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    query = """
        SELECT r.*, c.name as category_name, c.color as category_color, c.icon as category_icon,
               COALESCE(p.name, 'Default Project') as project_name,
               COALESCE((SELECT progress_pct FROM mitigation_plans WHERE risk_id = r.id ORDER BY updated_at DESC LIMIT 1), 0) as mitigation_progress
        FROM risks r
        JOIN categories c ON r.category_id = c.id
        LEFT JOIN projects p ON r.project_id = p.id
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND (r.id LIKE ? OR r.name LIKE ? OR r.owner LIKE ? OR r.department LIKE ? OR r.mitigation_strategy LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term, term, term])

    if category:
        query += " AND r.category_id = ?"
        params.append(category)

    if level:
        query += " AND r.risk_level = ?"
        params.append(level)

    if status:
        query += " AND r.status = ?"
        params.append(status)

    probability = request.args.get('probability', '').strip()
    if probability:
        try:
            query += " AND r.probability = ?"
            params.append(int(probability))
        except ValueError:
            pass

    impact = request.args.get('impact', '').strip()
    if impact:
        try:
            query += " AND r.impact = ?"
            params.append(int(impact))
        except ValueError:
            pass

    score = request.args.get('score', '').strip()
    if score:
        try:
            query += " AND r.risk_score = ?"
            params.append(int(score))
        except ValueError:
            pass

    if project_id:
        query += " AND r.project_id = ?"
        params.append(project_id)

    # Valid sort fields
    valid_sorts = {
        'id': 'r.id',
        'name': 'r.name',
        'probability': 'r.probability',
        'impact': 'r.impact',
        'score': 'r.risk_score',
        'level': 'r.risk_score', # Sort by numerical risk score
        'status': 'r.status',
        'date': 'r.date_identified',
        'owner': 'r.owner'
    }
    sort_col = valid_sorts.get(sort_by, 'r.id')
    sort_dir = 'DESC' if order == 'desc' else 'ASC'
    
    # Get total count before pagination
    count_query = f"SELECT COUNT(*) as total FROM ({query})"
    total_records = query_db(count_query, params, one=True)['total']

    # Add sorting and pagination
    query += f" ORDER BY {sort_col} {sort_dir}"
    offset = (page - 1) * per_page
    query += " LIMIT ? OFFSET ?"
    params.extend([per_page, offset])

    risks = query_db(query, params)

    return jsonify({
        'risks': risks,
        'total': total_records,
        'page': page,
        'per_page': per_page,
        'total_pages': max(1, (total_records + per_page - 1) // per_page)
    })

@app.route('/api/projects', methods=['GET', 'POST'])
def handle_projects_api():
    if request.method == 'POST':
        data = request.get_json() or {}
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'error': 'Project name is required'}), 400

        project_type = data.get('project_type', 'Web Application').strip()
        description = data.get('description', '').strip()
        tech_stack = data.get('tech_stack', '').strip()
        team_size = int(data.get('team_size', 5))
        stage = data.get('stage', 'Development').strip()
        deployment_type = data.get('deployment_type', 'Cloud').strip()
        
        concerns_raw = data.get('concerns', [])
        if isinstance(concerns_raw, list):
            import json as json_lib
            concerns = json_lib.dumps(concerns_raw)
        else:
            concerns = str(concerns_raw)

        created_by = session.get('username') or 'Aditya Patil'

        project_id, _ = execute_db("""
            INSERT INTO projects (name, project_type, description, tech_stack, team_size, stage, deployment_type, concerns, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, project_type, description, tech_stack, team_size, stage, deployment_type, concerns, created_by))

        project = query_db("SELECT * FROM projects WHERE id = ?", (project_id,), one=True)
        return jsonify({'success': True, 'message': 'Project created successfully', 'project_id': project_id, 'project': project}), 201

    # GET: return list of all projects
    projects = query_db("""
        SELECT p.*, COUNT(r.id) as risk_count, ROUND(AVG(r.risk_score), 1) as avg_score,
               SUM(CASE WHEN r.risk_level = 'Critical' THEN 1 ELSE 0 END) as critical_count
        FROM projects p
        LEFT JOIN risks r ON p.id = r.project_id
        GROUP BY p.id
        ORDER BY p.created_at DESC
    """)
    return jsonify({'projects': projects})

@app.route('/api/assessment/suggest-mitigation', methods=['POST'])
def suggest_mitigation_api():
    data = request.get_json() or {}
    category_id = data.get('category_id')
    category_name = data.get('category_name', '')
    threat_name = data.get('threat_name', '')

    if category_id and not category_name:
        cat = query_db("SELECT name FROM categories WHERE id = ?", (category_id,), one=True)
        if cat:
            category_name = cat['name']

    suggestion = get_suggested_mitigation(category_name, threat_name)
    return jsonify({
        'success': True,
        'category_name': category_name,
        'strategy': suggestion['strategy'],
        'action_steps': suggestion['action_steps']
    })

@app.route('/api/assessment/create-risk-and-mitigation', methods=['POST'])
def assessment_create_risk_and_mitigation():
    data = request.get_json() or {}
    
    # 1. Validate risk details
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Risk title / description of what could go wrong is required'}), 400

    category_id = int(data.get('category_id', 1))
    probability = int(data.get('probability', 3))
    impact = int(data.get('impact', 3))
    probability = max(1, min(5, probability))
    impact = max(1, min(5, impact))
    risk_score = probability * impact
    risk_level = calculate_risk_level(risk_score)

    project_id = data.get('project_id')
    if project_id:
        try:
            project_id = int(project_id)
        except Exception:
            project_id = None

    owner = data.get('owner') or session.get('username') or 'Neha Kulkarni'
    department = data.get('department', 'Engineering').strip()
    date_identified = data.get('date_identified') or datetime.now().strftime('%Y-%m-%d')
    description = data.get('description', '').strip()

    mitigation_strategy = data.get('mitigation_strategy', '').strip()
    mitigation_action_steps = data.get('mitigation_action_steps', '').strip()
    mitigation_owner = data.get('mitigation_owner', owner).strip()
    target_date = data.get('target_date') or datetime.now().strftime('%Y-%m-%d')
    create_mitigation = data.get('create_mitigation', False) or bool(mitigation_strategy)

    status = 'Mitigation Planned' if create_mitigation and mitigation_strategy else 'Assessed'

    # Auto-generate next risk ID
    existing_ids = [r['id'] for r in query_db("SELECT id FROM risks")]
    nums = [int(i.replace('RISK-', '')) for i in existing_ids if i.startswith('RISK-') and i.replace('RISK-', '').isdigit()]
    next_num = max(nums) + 1 if nums else 1
    risk_id = f"RISK-{next_num:03d}"

    execute_db("""
        INSERT INTO risks (
            id, project_id, name, description, category_id, probability, impact, risk_score, risk_level,
            initial_probability, initial_impact, initial_score, owner, department, date_identified,
            mitigation_strategy, mitigation_owner, target_date, status, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        risk_id, project_id, name, description, category_id, probability, impact, risk_score, risk_level,
        probability, impact, risk_score, owner, department, date_identified,
        mitigation_strategy, mitigation_owner, target_date, status
    ))

    # Add initial history entry
    execute_db("""
        INSERT INTO risk_history (risk_id, recorded_date, probability, impact, risk_score, risk_level, previous_score, notes, recorded_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        risk_id, date_identified, probability, impact, risk_score, risk_level, risk_score,
        'Initial risk assessment recorded via Project Assessment workflow.', session.get('username', 'Aditya Patil')
    ))

    mitigation_id = None
    if create_mitigation and mitigation_strategy:
        mitigation_id, _ = execute_db("""
            INSERT INTO mitigation_plans (
                risk_id, strategy_name, action_steps, responsible_person, start_date, target_date,
                status, progress_pct, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            risk_id, mitigation_strategy, mitigation_action_steps or f"Primary treatment plan for {risk_id}",
            mitigation_owner, date_identified, target_date,
            'Planned', 0, 'Action plan linked via Project Risk Assessment.'
        ))

    # Create notification
    execute_db("""
        INSERT INTO notifications (user_id, title, message, type)
        VALUES (?, ?, ?, ?)
    """, (
        session.get('user_id', 1),
        f"Assessed New Risk: {risk_id}",
        f"{name} ({risk_level} - Score {risk_score}) added to risk governance register.",
        'critical' if risk_level in ['Critical', 'High'] else 'info'
    ))

    return jsonify({
        'success': True,
        'message': f"Risk {risk_id} successfully assessed and registered!",
        'risk_id': risk_id,
        'risk_score': risk_score,
        'risk_level': risk_level,
        'status': status,
        'mitigation_id': mitigation_id
    }), 201

@app.route('/api/mapping-data', methods=['GET'])
def get_mapping_data():
    category = request.args.get('category', '').strip()
    status = request.args.get('status', '').strip()
    project_id = request.args.get('project_id', '').strip()
    search = request.args.get('search', '').strip()

    query = """
        SELECT r.id as risk_id, r.name as risk_name, r.risk_score, r.risk_level, r.initial_score,
               r.status as risk_status, r.owner as risk_owner, r.department, r.date_identified,
               c.name as category_name, c.color as category_color, c.icon as category_icon,
               COALESCE(p.name, 'Default Project') as project_name,
               m.id as mitigation_id, m.strategy_name, m.action_steps, m.responsible_person as mitigation_owner,
               m.progress_pct, m.status as mitigation_status, m.target_date
        FROM risks r
        JOIN categories c ON r.category_id = c.id
        LEFT JOIN projects p ON r.project_id = p.id
        LEFT JOIN mitigation_plans m ON r.id = m.risk_id
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND (r.id LIKE ? OR r.name LIKE ? OR m.strategy_name LIKE ? OR r.owner LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term, term])

    if category:
        query += " AND r.category_id = ?"
        params.append(category)

    if status:
        query += " AND r.status = ?"
        params.append(status)

    if project_id:
        query += " AND r.project_id = ?"
        params.append(project_id)

    query += " ORDER BY r.risk_score DESC, m.progress_pct ASC"

    mappings = query_db(query, params)
    for item in mappings:
        init_s = item.get('initial_score') or item.get('risk_score') or 1
        curr_s = item.get('risk_score') or 0
        item['reduction_pct'] = calculate_risk_reduction(init_s, curr_s)
        item['points_mitigated'] = max(0, init_s - curr_s)

    return jsonify({'mappings': mappings, 'total': len(mappings)})

@app.route('/api/risks/<risk_id>', methods=['GET'])
def get_single_risk(risk_id):
    risk = query_db("""
        SELECT r.*, c.name as category_name, c.color as category_color, c.icon as category_icon,
               COALESCE(p.name, 'Default Project') as project_name
        FROM risks r
        JOIN categories c ON r.category_id = c.id
        LEFT JOIN projects p ON r.project_id = p.id
        WHERE r.id = ?
    """, (risk_id,), one=True)
    if not risk:
        return jsonify({'error': 'Risk not found'}), 404

    mitigations = query_db("SELECT * FROM mitigation_plans WHERE risk_id = ? ORDER BY id ASC", (risk_id,))
    history = query_db("SELECT * FROM risk_history WHERE risk_id = ? ORDER BY recorded_date ASC, id ASC", (risk_id,))

    return jsonify({
        'risk': risk,
        'mitigations': mitigations,
        'history': history
    })

@app.route('/api/risks', methods=['POST'])
def create_risk():
    data = request.get_json() or {}
    
    # Validation
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Risk name is required'}), 400

    # Auto-generate Risk ID if not provided or format correctly
    existing_ids = [r['id'] for r in query_db("SELECT id FROM risks")]
    custom_id = data.get('id', '').strip().upper()
    
    if custom_id and custom_id not in existing_ids:
        risk_id = custom_id
    else:
        # Determine next ID
        nums = [int(i.replace('RISK-', '')) for i in existing_ids if i.startswith('RISK-') and i.replace('RISK-', '').isdigit()]
        next_num = max(nums) + 1 if nums else 1
        risk_id = f"RISK-{next_num:03d}"

    project_id = data.get('project_id')
    if project_id:
        try:
            project_id = int(project_id)
        except Exception:
            project_id = None

    category_id = int(data.get('category_id', 1))
    probability = int(data.get('probability', 3))
    impact = int(data.get('impact', 3))
    
    # Calculate score and level
    probability = max(1, min(5, probability))
    impact = max(1, min(5, impact))
    risk_score = probability * impact
    risk_level = calculate_risk_level(risk_score)

    owner = data.get('owner', 'Neha Kulkarni').strip()
    department = data.get('department', 'Engineering').strip()
    date_identified = data.get('date_identified') or datetime.now().strftime('%Y-%m-%d')
    mitigation_strategy = data.get('mitigation_strategy', '').strip()
    mitigation_owner = data.get('mitigation_owner', owner).strip()
    target_date = data.get('target_date') or datetime.now().strftime('%Y-%m-%d')
    status = data.get('status', 'Assessed')
    description = data.get('description', '').strip()

    execute_db("""
        INSERT INTO risks (
            id, project_id, name, description, category_id, probability, impact, risk_score, risk_level,
            initial_probability, initial_impact, initial_score, owner, department, date_identified,
            mitigation_strategy, mitigation_owner, target_date, status, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        risk_id, project_id, name, description, category_id, probability, impact, risk_score, risk_level,
        probability, impact, risk_score, owner, department, date_identified,
        mitigation_strategy, mitigation_owner, target_date, status
    ))

    # Add initial history entry
    execute_db("""
        INSERT INTO risk_history (risk_id, recorded_date, probability, impact, risk_score, risk_level, previous_score, notes, recorded_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        risk_id, date_identified, probability, impact, risk_score, risk_level, risk_score,
        'Initial risk registration and assessment.', session.get('username', 'Aditya Patil')
    ))

    # Add default mitigation plan if provided
    if mitigation_strategy:
        execute_db("""
            INSERT INTO mitigation_plans (
                risk_id, strategy_name, action_steps, responsible_person, start_date, target_date, status, progress_pct, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            risk_id, mitigation_strategy, f"Primary mitigation strategy for {risk_id}",
            mitigation_owner, date_identified, target_date,
            'Planned' if status == 'Assessed' else 'In Progress',
            0, 'Mitigation plan initialized upon risk registration.'
        ))

    # Trigger notification
    execute_db("""
        INSERT INTO notifications (user_id, title, message, type)
        VALUES (?, ?, ?, ?)
    """, (
        session.get('user_id', 1),
        f"New Risk Created: {risk_id}",
        f"{name} assessed with Score {risk_score} ({risk_level}).",
        'critical' if risk_level in ['Critical', 'High'] else 'info'
    ))

    return jsonify({
        'success': True,
        'message': f"Risk {risk_id} created successfully!",
        'risk_id': risk_id,
        'risk_score': risk_score,
        'risk_level': risk_level
    }), 201

@app.route('/api/risks/<risk_id>', methods=['PUT'])
def update_risk(risk_id):
    data = request.get_json() or {}
    existing = query_db("SELECT * FROM risks WHERE id = ?", (risk_id,), one=True)
    if not existing:
        return jsonify({'error': 'Risk not found'}), 404

    name = data.get('name', existing['name']).strip()
    description = data.get('description', existing['description']).strip()
    category_id = int(data.get('category_id', existing['category_id']))
    probability = int(data.get('probability', existing['probability']))
    impact = int(data.get('impact', existing['impact']))
    
    probability = max(1, min(5, probability))
    impact = max(1, min(5, impact))
    risk_score = probability * impact
    risk_level = calculate_risk_level(risk_score)

    owner = data.get('owner', existing['owner']).strip()
    department = data.get('department', existing['department']).strip()
    date_identified = data.get('date_identified', existing['date_identified'])
    mitigation_strategy = data.get('mitigation_strategy', existing['mitigation_strategy']).strip()
    mitigation_owner = data.get('mitigation_owner', existing['mitigation_owner']).strip()
    target_date = data.get('target_date', existing['target_date'])
    status = data.get('status', existing['status'])

    execute_db("""
        UPDATE risks SET
            name = ?, description = ?, category_id = ?, probability = ?, impact = ?,
            risk_score = ?, risk_level = ?, owner = ?, department = ?, date_identified = ?,
            mitigation_strategy = ?, mitigation_owner = ?, target_date = ?, status = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        name, description, category_id, probability, impact,
        risk_score, risk_level, owner, department, date_identified,
        mitigation_strategy, mitigation_owner, target_date, status,
        risk_id
    ))

    # If probability or impact changed, record new history milestone
    if probability != existing['probability'] or impact != existing['impact']:
        execute_db("""
            INSERT INTO risk_history (risk_id, recorded_date, probability, impact, risk_score, risk_level, notes, recorded_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            risk_id, datetime.now().strftime('%Y-%m-%d'), probability, impact, risk_score, risk_level,
            f"Risk score reassessed from {existing['risk_score']} to {risk_score}.",
            session.get('username', 'Admin')
        ))

    return jsonify({
        'success': True,
        'message': f"Risk {risk_id} updated successfully!",
        'risk_score': risk_score,
        'risk_level': risk_level
    })

@app.route('/api/risks/<risk_id>', methods=['DELETE'])
def delete_risk(risk_id):
    existing = query_db("SELECT * FROM risks WHERE id = ?", (risk_id,), one=True)
    if not existing:
        return jsonify({'error': 'Risk not found'}), 404

    execute_db("DELETE FROM risks WHERE id = ?", (risk_id,))
    return jsonify({'success': True, 'message': f"Risk {risk_id} deleted successfully."})

@app.route('/api/risks/<risk_id>/history', methods=['POST'])
def add_risk_history(risk_id):
    data = request.get_json() or {}
    existing = query_db("SELECT * FROM risks WHERE id = ?", (risk_id,), one=True)
    if not existing:
        return jsonify({'error': 'Risk not found'}), 404

    probability = int(data.get('probability', existing['probability']))
    impact = int(data.get('impact', existing['impact']))
    probability = max(1, min(5, probability))
    impact = max(1, min(5, impact))
    score = probability * impact
    level = calculate_risk_level(score)
    notes = data.get('notes', 'Periodic risk reassessment').strip()
    recorded_date = data.get('recorded_date') or datetime.now().strftime('%Y-%m-%d')
    recorded_by = session.get('username', 'Admin')

    execute_db("""
        INSERT INTO risk_history (risk_id, recorded_date, probability, impact, risk_score, risk_level, notes, recorded_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (risk_id, recorded_date, probability, impact, score, level, notes, recorded_by))

    # Update current risk table values
    execute_db("""
        UPDATE risks SET probability = ?, impact = ?, risk_score = ?, risk_level = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (probability, impact, score, level, risk_id))

    return jsonify({'success': True, 'message': 'Risk milestone recorded successfully', 'risk_score': score, 'risk_level': level})

# -------------------------------------------------------------
# 5x5 Risk Matrix API
# -------------------------------------------------------------
@app.route('/api/matrix-data', methods=['GET'])
def get_matrix_data():
    """
    Returns a 5x5 grid structure where:
    Y-axis = Impact (5 down to 1)
    X-axis = Probability (1 to 5)
    Each cell contains: count, list of risks with residual risk data, score, level, color
    """
    risks = query_db("""
        SELECT r.*, c.name as category_name, c.color as category_color, c.icon as category_icon,
               COALESCE(p.name, 'Default Project') as project_name,
               COALESCE((SELECT progress_pct FROM mitigation_plans WHERE risk_id = r.id ORDER BY updated_at DESC LIMIT 1), 0) as mitigation_progress,
               (SELECT residual_score FROM mitigation_plans WHERE risk_id = r.id AND residual_score IS NOT NULL ORDER BY updated_at DESC LIMIT 1) as plan_residual_score
        FROM risks r
        JOIN categories c ON r.category_id = c.id
        LEFT JOIN projects p ON r.project_id = p.id
        ORDER BY r.risk_score DESC, r.id ASC
    """)

    # Initialize 5x5 grid map
    # Matrix grid structure: impact (row 5 down to 1), probability (col 1 to 5)
    grid = {}
    for impact in range(1, 6):
        grid[impact] = {}
        for prob in range(1, 6):
            score = prob * impact
            grid[impact][prob] = {
                'impact': impact,
                'probability': prob,
                'score': score,
                'level': calculate_risk_level(score),
                'count': 0,
                'risks': []
            }

    for r in risks:
        p = r['probability']
        i = r['impact']
        init_s = r.get('initial_score') or (r.get('initial_probability', 1) * r.get('initial_impact', 1)) or 1
        curr_s = r.get('risk_score') or (p * i)
        r['reduction_pct'] = calculate_risk_reduction(init_s, curr_s)
        r['residual_score'] = r.get('plan_residual_score') if r.get('plan_residual_score') is not None else curr_s
        r['residual_level'] = calculate_risk_level(r['residual_score'])

        if i in grid and p in grid[i]:
            grid[i][p]['count'] += 1
            grid[i][p]['risks'].append(r)

    # Flatten into 2D array ordered by impact DESC (5 down to 1) and prob ASC (1 to 5)
    matrix_rows = []
    impact_labels = ['Very Low', 'Low', 'Medium', 'High', 'Very High']
    prob_labels = ['Very Low', 'Low', 'Medium', 'High', 'Very High']
    
    for impact in range(5, 0, -1):
        row_cells = []
        for prob in range(1, 6):
            row_cells.append(grid[impact][prob])
        matrix_rows.append({
            'impact_level': impact,
            'impact_label': f"{impact} - {impact_labels[impact - 1]}",
            'cells': row_cells
        })

    return jsonify({
        'matrix_rows': matrix_rows,
        'probability_labels': [f"{idx+1} - {name}" for idx, name in enumerate(prob_labels)],
        'impact_labels': [f"{idx+1} - {name}" for idx, name in enumerate(impact_labels)],
        'total_risks': len(risks)
    })

# -------------------------------------------------------------
# Mitigation Plans API
# -------------------------------------------------------------
@app.route('/api/mitigations', methods=['GET'])
def get_mitigations():
    plans = query_db("""
        SELECT m.*, r.name as risk_name, r.risk_level, r.risk_score, r.probability, r.impact,
               r.initial_score, r.initial_probability, r.initial_impact,
               c.name as category_name, c.color as category_color
        FROM mitigation_plans m
        JOIN risks r ON m.risk_id = r.id
        JOIN categories c ON r.category_id = c.id
        ORDER BY m.progress_pct ASC, r.risk_score DESC
    """)
    for m in plans:
        init_s = m.get('initial_score') or ((m.get('initial_probability') or 1) * (m.get('initial_impact') or 1))
        curr_s = m.get('risk_score') or 0
        m['reduction_pct'] = calculate_risk_reduction(init_s, curr_s)
        m['points_mitigated'] = max(0, init_s - curr_s)
        m['risk_level'] = calculate_risk_level(curr_s)

    return jsonify({'mitigations': plans})

@app.route('/api/mitigations', methods=['POST'])
def create_mitigation():
    data = request.get_json() or {}
    risk_id = data.get('risk_id')
    strategy_name = data.get('strategy_name', '').strip()
    if not risk_id or not strategy_name:
        return jsonify({'error': 'Risk ID and Strategy Name are required'}), 400

    action_steps = data.get('action_steps', '').strip()
    responsible_person = data.get('responsible_person', 'DevOps Lead').strip()
    start_date = data.get('start_date') or datetime.now().strftime('%Y-%m-%d')
    target_date = data.get('target_date') or datetime.now().strftime('%Y-%m-%d')
    status = data.get('status', 'In Progress')
    progress_pct = int(data.get('progress_pct', 0))
    progress_pct = max(0, min(100, progress_pct))
    notes = data.get('notes', '').strip()

    plan_id, _ = execute_db("""
        INSERT INTO mitigation_plans (
            risk_id, strategy_name, action_steps, responsible_person, start_date, target_date,
            status, progress_pct, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (risk_id, strategy_name, action_steps, responsible_person, start_date, target_date, status, progress_pct, notes))

    return jsonify({'success': True, 'message': 'Mitigation plan created successfully', 'id': plan_id}), 201

@app.route('/api/mitigations/<int:plan_id>', methods=['PUT'])
def update_mitigation(plan_id):
    data = request.get_json() or {}
    existing = query_db("SELECT * FROM mitigation_plans WHERE id = ?", (plan_id,), one=True)
    if not existing:
        return jsonify({'error': 'Mitigation plan not found'}), 404

    strategy_name = data.get('strategy_name', existing['strategy_name']).strip()
    action_steps = data.get('action_steps', existing['action_steps']).strip()
    responsible_person = data.get('responsible_person', existing['responsible_person']).strip()
    start_date = data.get('start_date', existing['start_date'])
    target_date = data.get('target_date', existing['target_date'])
    status = data.get('status', existing['status'])
    progress_pct = int(data.get('progress_pct', existing['progress_pct']))
    progress_pct = max(0, min(100, progress_pct))
    notes = data.get('notes', existing['notes']).strip()

    execute_db("""
        UPDATE mitigation_plans SET
            strategy_name = ?, action_steps = ?, responsible_person = ?, start_date = ?, target_date = ?,
            status = ?, progress_pct = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (strategy_name, action_steps, responsible_person, start_date, target_date, status, progress_pct, notes, plan_id))

    return jsonify({'success': True, 'message': 'Mitigation plan updated successfully'})

@app.route('/api/mitigations/<int:plan_id>/progress', methods=['POST'])
def update_mitigation_progress(plan_id):
    data = request.get_json() or {}
    progress_val = data.get('progress_pct') if 'progress_pct' in data else data.get('progress', 0)
    progress_pct = int(progress_val)
    progress_pct = max(0, min(100, progress_pct))

    plan = query_db("SELECT * FROM mitigation_plans WHERE id = ?", (plan_id,), one=True)
    if not plan:
        return jsonify({'error': 'Plan not found'}), 404

    new_status = 'Completed' if progress_pct == 100 else ('Planned' if progress_pct == 0 else 'In Progress')

    execute_db("""
        UPDATE mitigation_plans SET progress_pct = ?, status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
    """, (progress_pct, new_status, plan_id))

    # If 100% complete, also mark the parent risk status if applicable
    if progress_pct == 100:
        execute_db("UPDATE risks SET status = 'Mitigated', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (plan['risk_id'],))

    return jsonify({'success': True, 'progress_pct': progress_pct, 'status': new_status})

# -------------------------------------------------------------
# Analytics & Chart Data API
# -------------------------------------------------------------
@app.route('/api/analytics-data', methods=['GET'])
def get_analytics_data():
    portfolio = get_portfolio_metrics()

    # 1. Risk Level Distribution (Doughnut Chart)
    level_counts = {
        'Critical': portfolio['critical_count'],
        'High': portfolio['high_count'],
        'Medium': portfolio['medium_count'],
        'Low': portfolio['low_count']
    }

    # 2. Risks by Category (Bar Chart)
    category_dist = query_db("""
        SELECT c.name, COUNT(r.id) as count, AVG(r.risk_score) as avg_score
        FROM categories c
        LEFT JOIN risks r ON c.id = r.category_id
        GROUP BY c.id, c.name
        ORDER BY count DESC
    """)

    # 3. Status Breakdown
    status_counts = {
        'Open': portfolio['open_count'],
        'In Progress': portfolio['in_progress_count'],
        'Mitigated': portfolio['mitigated_count'],
        'Closed': portfolio['closed_count']
    }

    # 4. Historical Trend Series (Average score over months/milestones)
    history_trend = query_db("""
        SELECT recorded_date, ROUND(AVG(risk_score), 1) as avg_score, COUNT(id) as count
        FROM risk_history
        GROUP BY recorded_date
        ORDER BY recorded_date ASC
    """)

    # 5. Risk Reduction velocity per risk (Leaderboard sorted by reduction_pct DESC)
    risks_raw = query_db("""
        SELECT id, name, initial_score, risk_score, risk_level
        FROM risks
    """)
    reduction_per_risk = []
    for r in risks_raw:
        init_s = r['initial_score'] or 1
        curr_s = r['risk_score']
        red_pct = calculate_risk_reduction(init_s, curr_s)
        level = calculate_risk_level(curr_s)
        reduction_per_risk.append({
            'id': r['id'],
            'name': r['name'],
            'initial_score': init_s,
            'risk_score': curr_s,
            'reduction_pct': red_pct,
            'risk_level': level
        })
    reduction_per_risk.sort(key=lambda x: (x['reduction_pct'], x['initial_score']), reverse=True)

    # 6. Mitigation Progress distribution
    mitigation_completion = query_db("""
        SELECT 
            SUM(CASE WHEN progress_pct = 100 THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN progress_pct >= 50 AND progress_pct < 100 THEN 1 ELSE 0 END) as in_progress_high,
            SUM(CASE WHEN progress_pct > 0 AND progress_pct < 50 THEN 1 ELSE 0 END) as in_progress_low,
            SUM(CASE WHEN progress_pct = 0 THEN 1 ELSE 0 END) as not_started
        FROM mitigation_plans
    """, one=True) or {}

    return jsonify({
        'portfolio': portfolio,
        'risk_distribution': level_counts,
        'categories': [{'name': r['name'], 'count': r['count'], 'avg_score': round(r['avg_score'] or 0, 1)} for r in category_dist],
        'status_distribution': status_counts,
        'history_trend': history_trend,
        'reduction_leaderboard': reduction_per_risk,
        'mitigation_completion': mitigation_completion
    })

# -------------------------------------------------------------
# Notifications API
# -------------------------------------------------------------
@app.route('/api/notifications/<int:notif_id>/read', methods=['POST'])
def mark_notification_read(notif_id):
    execute_db("UPDATE notifications SET is_read = 1 WHERE id = ?", (notif_id,))
    return jsonify({'success': True})

# -------------------------------------------------------------
# CSV Export Route
# -------------------------------------------------------------
@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    report_type = request.args.get('type', 'risks')
    output = io.StringIO()
    writer = csv.writer(output)

    if report_type == 'risks':
        writer.writerow([
            'Risk ID', 'Risk Name', 'Category', 'Probability (1-5)', 'Impact (1-5)',
            'Risk Score', 'Risk Level', 'Initial Score', 'Risk Reduction %',
            'Owner', 'Department', 'Date Identified', 'Mitigation Strategy', 'Status'
        ])
        risks = query_db("""
            SELECT r.*, c.name as category_name
            FROM risks r
            JOIN categories c ON r.category_id = c.id
            ORDER BY r.risk_score DESC
        """)
        for r in risks:
            init_s = r['initial_score'] or 1
            curr_s = r['risk_score']
            red_pct = calculate_risk_reduction(init_s, curr_s)
            level = calculate_risk_level(curr_s)
            writer.writerow([
                r['id'], r['name'], r['category_name'], r['probability'], r['impact'],
                curr_s, level, init_s, f"{red_pct}%",
                r['owner'], r['department'], r['date_identified'], r['mitigation_strategy'], r['status']
            ])
        filename = f"Software_Risk_Matrix_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    else:
        writer.writerow([
            'Plan ID', 'Risk ID', 'Risk Name', 'Strategy', 'Responsible Person',
            'Start Date', 'Target Date', 'Status', 'Progress %', 'Notes'
        ])
        plans = query_db("""
            SELECT m.*, r.name as risk_name
            FROM mitigation_plans m
            JOIN risks r ON m.risk_id = r.id
            ORDER BY m.id ASC
        """)
        for p in plans:
            writer.writerow([
                p['id'], p['risk_id'], p['risk_name'], p['strategy_name'], p['responsible_person'],
                p['start_date'], p['target_date'], p['status'], f"{p['progress_pct']}%", p['notes']
            ])
        filename = f"Mitigation_Plans_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    response.headers['Content-type'] = 'text/csv'
    return response

# -------------------------------------------------------------
# System & Demo Reset Route
# -------------------------------------------------------------
@app.route('/api/reset-demo-data', methods=['POST'])
@app.route('/api/reset-data', methods=['POST'])
def reset_demo_data():
    try:
        seed_database()
        return jsonify({'success': True, 'message': 'Sample dataset reseeded to pristine state!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/settings', methods=['POST'])
def save_settings():
    data = request.get_json() or {}
    for k, v in data.items():
        execute_db("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, str(v)))
    return jsonify({'success': True, 'message': 'Settings saved successfully'})

if __name__ == '__main__':
    # Run the server on port 5000 in debug mode
    app.run(host='0.0.0.0', port=5000, debug=True)

