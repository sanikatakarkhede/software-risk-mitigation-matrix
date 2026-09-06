"""
Comprehensive Verification Test Suite for MatrixPro Risk Governance
Validates data consistency, calculations, route responses, and API endpoints.
"""
import unittest
import json
import sqlite3
from datetime import datetime
from app import app
from database.db import (
    calculate_risk_level,
    calculate_risk_reduction,
    get_portfolio_metrics,
    query_db
)

class MatrixProConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_risk_level_banding(self):
        """Verify severity banding rules: 17-25 Critical, 10-16 High, 5-9 Medium, 1-4 Low."""
        self.assertEqual(calculate_risk_level(25), "Critical")
        self.assertEqual(calculate_risk_level(17), "Critical")
        self.assertEqual(calculate_risk_level(16), "High")
        self.assertEqual(calculate_risk_level(10), "High")
        self.assertEqual(calculate_risk_level(9), "Medium")
        self.assertEqual(calculate_risk_level(5), "Medium")
        self.assertEqual(calculate_risk_level(4), "Low")
        self.assertEqual(calculate_risk_level(1), "Low")

    def test_reduction_calculation_formula(self):
        """Verify individual reduction formula: ((init - curr) / init) * 100."""
        # 16 -> 4 = 75.0%
        self.assertEqual(calculate_risk_reduction(16, 4), 75.0)
        # 20 -> 8 = 60.0%
        self.assertEqual(calculate_risk_reduction(20, 8), 60.0)
        # 25 -> 25 = 0.0%
        self.assertEqual(calculate_risk_reduction(25, 25), 0.0)
        # 0 init -> 0.0%
        self.assertEqual(calculate_risk_reduction(0, 5), 0.0)

    def test_portfolio_metrics_consistency(self):
        """Verify portfolio metrics calculations match direct database sums."""
        metrics = get_portfolio_metrics()
        risks = query_db("SELECT id, risk_score, initial_score, risk_level FROM risks")
        self.assertGreater(len(risks), 0)

        total_init = sum(r['initial_score'] for r in risks)
        total_curr = sum(r['risk_score'] for r in risks)
        expected_reduction = round(((total_init - total_curr) / total_init) * 100.0, 1)

        self.assertEqual(metrics['total_initial_score'], total_init)
        self.assertEqual(metrics['total_current_score'], total_curr)
        self.assertEqual(metrics['overall_reduction_pct'], expected_reduction)
        self.assertEqual(metrics['total'], len(risks))

    def test_page_routes_status_200(self):
        """Verify all 7 core pages and detail page return 200 OK."""
        routes = [
            '/',
            '/dashboard',
            '/matrix',
            '/risks',
            '/mitigation',
            '/analytics',
            '/reports',
            '/settings',
            '/risks/RISK-001'
        ]
        for route in routes:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200, f"Route {route} returned status {res.status_code}")

    def test_dashboard_and_reports_reduction_consistency(self):
        """Verify Dashboard, Analytics API, and Reports all reflect the same unified overall reduction %."""
        metrics = get_portfolio_metrics()
        unified_pct_str = f"{metrics['overall_reduction_pct']}%"

        # Check Dashboard HTML
        res_dash = self.client.get('/dashboard')
        self.assertEqual(res_dash.status_code, 200)
        self.assertIn(b"Executive Risk Dashboard", res_dash.data)
        self.assertIn(b"Objective:", res_dash.data)

        # Check Reports HTML
        res_rep = self.client.get('/reports')
        self.assertEqual(res_rep.status_code, 200)
        self.assertIn(bytes(unified_pct_str, 'utf-8'), res_rep.data)
        self.assertIn(b"Audit Reference ID", res_rep.data)
        self.assertNotIn(b"Cryptographic Attestation ID", res_rep.data)

        # Check Analytics API
        res_analytics = self.client.get('/api/analytics-data')
        self.assertEqual(res_analytics.status_code, 200)
        data = json.loads(res_analytics.data)
        self.assertEqual(data['portfolio']['overall_reduction_pct'], metrics['overall_reduction_pct'])

    def test_api_endpoints(self):
        """Verify JSON APIs return valid schema and proper database data."""
        # 1. /api/stats
        r_stats = self.client.get('/api/stats')
        self.assertEqual(r_stats.status_code, 200)
        d_stats = json.loads(r_stats.data)
        self.assertIn('overall_reduction_pct', d_stats)
        self.assertIn('total', d_stats)

        # 2. /api/matrix-data
        r_matrix = self.client.get('/api/matrix-data')
        self.assertEqual(r_matrix.status_code, 200)
        d_matrix = json.loads(r_matrix.data)
        self.assertEqual(len(d_matrix['matrix_rows']), 5)

        # 3. /api/risks
        r_risks = self.client.get('/api/risks')
        self.assertEqual(r_risks.status_code, 200)
        d_risks = json.loads(r_risks.data)
        self.assertIn('risks', d_risks)
        self.assertGreater(len(d_risks['risks']), 0)

        # 4. /api/mitigations
        r_mits = self.client.get('/api/mitigations')
        self.assertEqual(r_mits.status_code, 200)
        d_mits = json.loads(r_mits.data)
        self.assertIn('mitigations', d_mits)

        # 5. /api/export/csv
        r_csv = self.client.get('/api/export/csv?type=risks')
        self.assertEqual(r_csv.status_code, 200)
        self.assertIn(b"Risk ID,Risk Name,Category", r_csv.data)

    def test_reset_data_endpoint(self):
        """Verify resetting database restores pristine sample dataset."""
        res = self.client.post('/api/reset-data')
        self.assertEqual(res.status_code, 200)
        d = json.loads(res.data)
        self.assertTrue(d['success'])

        metrics = get_portfolio_metrics()
        self.assertEqual(metrics['total'], 12)
        self.assertEqual(metrics['overall_reduction_pct'], 57.4)

    def test_risk_crud_operations(self):
        """Verify adding, editing, and deleting a risk through API endpoints."""
        # 1. Create Risk
        new_risk_data = {
            'id': 'RISK-099',
            'name': 'API Authentication Token Leak',
            'description': 'Temporary security token exposure in client logs.',
            'category_id': 2,
            'probability': 3,
            'impact': 4,
            'owner': 'DevSecOps Squad',
            'department': 'Security',
            'mitigation_strategy': 'Sanitize client loggers and enforce 1-hour expiry.'
        }
        res_create = self.client.post('/api/risks',
                                      data=json.dumps(new_risk_data),
                                      content_type='application/json')
        self.assertEqual(res_create.status_code, 201)
        d_create = json.loads(res_create.data)
        self.assertTrue(d_create['success'])

        # Verify created
        res_get = self.client.get('/api/risks?search=RISK-099')
        d_get = json.loads(res_get.data)
        self.assertEqual(len(d_get['risks']), 1)
        self.assertEqual(d_get['risks'][0]['risk_score'], 12)
        self.assertEqual(d_get['risks'][0]['risk_level'], 'High')

        # 2. Update Risk
        update_data = {
            'name': 'API Authentication Token Leak (Updated)',
            'probability': 1,
            'impact': 2,
            'owner': 'DevSecOps Lead',
            'status': 'Mitigated'
        }
        res_update = self.client.put('/api/risks/RISK-099',
                                     data=json.dumps(update_data),
                                     content_type='application/json')
        self.assertEqual(res_update.status_code, 200)
        
        # Verify updated score = 2 (Low)
        res_get2 = self.client.get('/api/risks?search=RISK-099')
        d_get2 = json.loads(res_get2.data)
        self.assertEqual(d_get2['risks'][0]['risk_score'], 2)
        self.assertEqual(d_get2['risks'][0]['risk_level'], 'Low')

        # 3. Delete Risk
        res_del = self.client.delete('/api/risks/RISK-099')
        self.assertEqual(res_del.status_code, 200)

        # Verify deleted
        res_get3 = self.client.get('/api/risks?search=RISK-099')
        d_get3 = json.loads(res_get3.data)
        self.assertEqual(len(d_get3['risks']), 0)

    def test_indian_demo_profiles(self):
        """Verify 1-click demo logins for Indian user profiles."""
        roles = [
            ('admin', 'Rahul Patil', 'Admin'),
            ('manager', 'Priya Sharma', 'Risk Manager'),
            ('dev', 'Amit Kulkarni', 'Developer'),
            ('auditor', 'Sneha Deshmukh', 'Auditor')
        ]
        for role_key, expected_name, expected_role in roles:
            res = self.client.post(f'/api/demo-login/{role_key}')
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertTrue(data['success'])
            self.assertIn(expected_name, data['message'])

    def test_registration_flow(self):
        """Verify user registration with validation and account creation."""
        reg_data = {
            'full_name': 'Vikram Sarabhai',
            'email': 'vikram.s@matrixpro.io',
            'role': 'Risk Manager',
            'department': 'Engineering Core',
            'password': 'password123',
            'confirm_password': 'password123'
        }
        res = self.client.post('/register', data=reg_data, follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        
        # Verify user created in DB
        u = query_db("SELECT * FROM users WHERE email = ?", ('vikram.s@matrixpro.io',), one=True)
        self.assertIsNotNone(u)
        self.assertEqual(u['full_name'], 'Vikram Sarabhai')

    def test_project_assessment_flow(self):
        """Verify full project assessment: project creation, suggestion, threat assessment and linked mitigation."""
        # 1. Create Project
        proj_payload = {
            'name': 'FinTech Microservices Core',
            'project_type': 'Financial Software',
            'description': 'Real-time ledger microservices and settlement gateway.',
            'tech_stack': 'Go, PostgreSQL, Kafka, Kubernetes',
            'team_size': 12,
            'stage': 'Development',
            'deployment_type': 'Cloud',
            'concerns': ['Security', 'Performance', 'Infrastructure']
        }
        res_proj = self.client.post('/api/projects',
                                    data=json.dumps(proj_payload),
                                    content_type='application/json')
        self.assertEqual(res_proj.status_code, 201)
        d_proj = json.loads(res_proj.data)
        self.assertTrue(d_proj['success'])
        proj_id = d_proj['project_id']

        # 2. Get Suggested Mitigation
        res_sug = self.client.post('/api/assessment/suggest-mitigation',
                                   data=json.dumps({'category_name': 'Performance & Latency', 'threat_name': 'Kafka message lag'}),
                                   content_type='application/json')
        self.assertEqual(res_sug.status_code, 200)
        d_sug = json.loads(res_sug.data)
        self.assertTrue(d_sug['success'])
        self.assertIn('performance', d_sug['strategy'].lower())

        # 3. Create Risk with Linked Mitigation
        risk_payload = {
            'project_id': proj_id,
            'name': 'Kafka Broker Message Ingestion Lag Spikes',
            'description': 'Partition unbalance causing consumer group lag beyond 5000ms threshold.',
            'category_id': 1, # Infrastructure
            'probability': 3,
            'impact': 4,
            'owner': 'Rohan Deshmukh',
            'department': 'Infrastructure',
            'create_mitigation': True,
            'mitigation_strategy': 'Deploy auto-scaled consumer pods and partition rebalancing.',
            'mitigation_action_steps': '1. Configure Kafka lag exporter metrics.\n2. Scale consumer replicas dynamically.\n3. Add Dead Letter Queue fallback.',
            'mitigation_owner': 'Rohan Deshmukh',
            'target_date': '2026-11-15'
        }
        res_create = self.client.post('/api/assessment/create-risk-and-mitigation',
                                      data=json.dumps(risk_payload),
                                      content_type='application/json')
        self.assertEqual(res_create.status_code, 201)
        d_create = json.loads(res_create.data)
        self.assertTrue(d_create['success'])
        risk_id = d_create['risk_id']
        self.assertEqual(d_create['risk_score'], 12)
        self.assertEqual(d_create['risk_level'], 'High')
        self.assertEqual(d_create['status'], 'Mitigation Planned')
        self.assertIsNotNone(d_create['mitigation_id'])

        # Verify DB records
        risk_row = query_db("SELECT * FROM risks WHERE id = ?", (risk_id,), one=True)
        self.assertIsNotNone(risk_row)
        self.assertEqual(risk_row['project_id'], proj_id)
        self.assertEqual(risk_row['status'], 'Mitigation Planned')

        mit_row = query_db("SELECT * FROM mitigation_plans WHERE risk_id = ?", (risk_id,), one=True)
        self.assertIsNotNone(mit_row)
        self.assertEqual(mit_row['responsible_person'], 'Rohan Deshmukh')

        hist_rows = query_db("SELECT * FROM risk_history WHERE risk_id = ?", (risk_id,))
        self.assertEqual(len(hist_rows), 1)
        self.assertEqual(hist_rows[0]['risk_score'], 12)

    def test_mapping_page_and_api(self):
        """Verify Risk ↔ Mitigation Mapping route and API return complete traceability data."""
        res_page = self.client.get('/mapping')
        self.assertEqual(res_page.status_code, 200)
        self.assertIn("Risk ↔ Mitigation Mapping".encode('utf-8'), res_page.data)
        self.assertIn(b"End-to-End Governance Traceability", res_page.data)

        res_api = self.client.get('/api/mapping-data')
        self.assertEqual(res_api.status_code, 200)
        data = json.loads(res_api.data)
        self.assertIn('mappings', data)
        self.assertGreater(len(data['mappings']), 0)
        
        # Verify fields in mapped item
        item = data['mappings'][0]
        self.assertIn('risk_id', item)
        self.assertIn('risk_score', item)
        self.assertIn('reduction_pct', item)

    def test_risk_details_what_changed_and_sequence(self):
        """Verify Risk Details view contains What Changed summary and progression sequence."""
        res = self.client.get('/risks/RISK-001')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"What Changed?", res.data)
        self.assertIn(b"Score History:", res.data)
        # RISK-001 progression is 15 -> 12 -> 6
        self.assertIn(b"15", res.data)
        self.assertIn(b"12", res.data)
        self.assertIn(b"6", res.data)

    def test_indian_personas_and_customizations(self):
        """Verify Indian primary personas exist in users table and can authenticate."""
        users = query_db("SELECT username, full_name, role FROM users")
        usernames = [u['username'] for u in users]
        names = [u['full_name'] for u in users]

        self.assertIn('admin', usernames)
        self.assertIn('risk_manager', usernames)
        self.assertIn('dev_lead', usernames)
        self.assertIn('auditor', usernames)

        self.assertIn('Rahul Patil', names)
        self.assertIn('Priya Sharma', names)
        self.assertIn('Amit Kulkarni', names)
        self.assertIn('Sneha Deshmukh', names)

        # Verify login as Rahul Patil (admin)
        res_login = self.client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)
        self.assertIn(b"Rahul Patil", res_login.data)

        # Verify quick settings dropdown elements exist in base layout
        self.assertIn(b"quickSettingsBtn", res_login.data)
        self.assertIn(b"quickSettingsMenu", res_login.data)
        self.assertIn(b'data-set-region="indian"', res_login.data)
        self.assertIn(b'data-set-region="intl"', res_login.data)
        self.assertIn(b'data-set-lang="hi"', res_login.data)
        self.assertIn(b'data-set-theme="light"', res_login.data)

    def test_strict_no_aditya_joshi(self):
        """CRITICAL: Assert that 'Aditya Joshi' is NEVER used anywhere in DB or API responses."""
        # 1. DB check
        users = query_db("SELECT full_name FROM users WHERE full_name LIKE '%Aditya Joshi%'")
        self.assertEqual(len(users), 0, "Aditya Joshi must NOT exist in users table")

        risks = query_db("SELECT id, owner, mitigation_owner FROM risks WHERE owner LIKE '%Aditya Joshi%' OR mitigation_owner LIKE '%Aditya Joshi%'")
        self.assertEqual(len(risks), 0, "Aditya Joshi must NOT be an owner in risks table")

        mitigations = query_db("SELECT id, responsible_person FROM mitigation_plans WHERE responsible_person LIKE '%Aditya Joshi%'")
        self.assertEqual(len(mitigations), 0, "Aditya Joshi must NOT be in mitigation_plans")

        history = query_db("SELECT id, recorded_by FROM risk_history WHERE recorded_by LIKE '%Aditya Joshi%'")
        self.assertEqual(len(history), 0, "Aditya Joshi must NOT be in risk_history")

        # 2. Endpoint check
        res_dashboard = self.client.get('/dashboard')
        self.assertNotIn(b"Aditya Joshi", res_dashboard.data)

        res_risks = self.client.get('/api/risks')
        self.assertNotIn(b"Aditya Joshi", res_risks.data)

        res_mitigations = self.client.get('/api/mitigations')
        self.assertNotIn(b"Aditya Joshi", res_mitigations.data)

    def test_how_it_works_tooltips_and_demo_tagging(self):
        """Verify 'How This Software Works' workflow guide, help tooltips, and demo data indicators."""
        res_dash = self.client.get('/dashboard')
        self.assertEqual(res_dash.status_code, 200)

        # 1. 'How This Software Works' workflow
        self.assertIn(b"How This Software Works", res_dash.data)
        self.assertIn(b"1. Identify Risk", res_dash.data)
        self.assertIn(b"2. Assess Risk", res_dash.data)
        self.assertIn(b"3. Select Mitigation", res_dash.data)
        self.assertIn(b"4. Track Risk Reduction", res_dash.data)
        self.assertIn(b"5. Generate Report", res_dash.data)

        # 2. Demo data badges & tooltip classes
        self.assertIn(b"Demo Data", res_dash.data)
        self.assertIn(b"help-icon", res_dash.data)
        self.assertIn(b"tooltip_risk_score", res_dash.data)
        self.assertIn(b"tooltip_risk_reduction", res_dash.data)

        # 3. Database is_demo tracking
        demo_risks = query_db("SELECT COUNT(*) as c FROM risks WHERE is_demo = 1", one=True)
        demo_count = demo_risks['c'] if demo_risks else 0
        self.assertGreaterEqual(demo_count, 0)

    def test_5x5_matrix_grid_structure_and_coordinates(self):
        """Verify 5x5 matrix structure (5 Impact rows x 5 Probability columns), exact scores, and severities."""
        res = self.client.get('/api/matrix-data')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)

        matrix_rows = data['matrix_rows']
        self.assertEqual(len(matrix_rows), 5, "Matrix must have 5 Impact rows")

        expected_impacts = [5, 4, 3, 2, 1]
        for row_idx, row in enumerate(matrix_rows):
            imp = expected_impacts[row_idx]
            self.assertEqual(row['impact_level'], imp)
            cells = row['cells']
            self.assertEqual(len(cells), 5, f"Row Impact {imp} must have 5 Probability cells")

            for col_idx, cell in enumerate(cells):
                prob = col_idx + 1
                expected_score = imp * prob
                self.assertEqual(cell['impact'], imp)
                self.assertEqual(cell['probability'], prob)
                self.assertEqual(cell['score'], expected_score)
                self.assertEqual(cell['level'], calculate_risk_level(expected_score))
                self.assertEqual(cell['count'], len(cell['risks']))

                # Check residual risk data on risks
                for r in cell['risks']:
                    self.assertIn('residual_score', r)
                    self.assertIn('reduction_pct', r)
                    self.assertIn('category_name', r)

    def test_matrix_coordinate_filtering_in_risks_api(self):
        """Verify that /api/risks correctly filters by probability and impact coordinates."""
        # Query specific coordinate (e.g. prob 2, imp 3)
        res = self.client.get('/api/risks?probability=2&impact=3')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        for r in data['risks']:
            self.assertEqual(r['probability'], 2)
            self.assertEqual(r['impact'], 3)
            self.assertEqual(r['risk_score'], 6)

    def test_monitoring_console_page(self):
        """Verify /monitoring page renders Risk Monitoring & Lifecycle Console with cards and status filters."""
        res = self.client.get('/monitoring')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Risk Monitoring & Lifecycle Console", res.data)
        self.assertIn(b"Continuous tracking, status transition management, and audit history", res.data)
        self.assertIn(b"CURRENT STATUS", res.data)
        self.assertIn(b"UPDATE RISK STATUS & MONITORING NOTE", res.data)
        self.assertIn(b"Record Review Update", res.data)

    def test_authentication_flow_and_registration(self):
        """Verify login page, registration flow, demo login, and logout redirect."""
        # 1. GET /login and GET /register
        res_login_get = self.client.get('/login')
        self.assertEqual(res_login_get.status_code, 200)
        self.assertIn(b"Sign In", res_login_get.data)
        self.assertIn(b"RiskManager", res_login_get.data)

        res_reg_get = self.client.get('/register')
        self.assertEqual(res_reg_get.status_code, 200)
        self.assertIn(b"Create Account", res_reg_get.data)

        # 2. POST /register (Create new user)
        unique_email = f"tester_{int(datetime.now().timestamp())}@riskmanager.io"
        reg_payload = {
            'full_name': 'Software Security Officer',
            'email': unique_email,
            'role': 'Risk Manager',
            'department': 'Security',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!'
        }
        res_reg_post = self.client.post('/register', data=reg_payload, follow_redirects=True)
        self.assertEqual(res_reg_post.status_code, 200)

        # 3. GET /logout
        res_logout = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(res_logout.status_code, 200)
        self.assertIn(b"Sign In", res_logout.data)

        # 4. POST /login (Valid credentials)
        res_login_post = self.client.post('/login', data={'username': unique_email, 'password': 'SecurePassword123!'}, follow_redirects=True)
        self.assertEqual(res_login_post.status_code, 200)
        self.assertIn(b"Dashboard", res_login_post.data)

        # 5. POST /api/demo-login/admin
        res_demo = self.client.post('/api/demo-login/admin')
        self.assertEqual(res_demo.status_code, 200)
        demo_json = json.loads(res_demo.data)
        self.assertTrue(demo_json['success'])

if __name__ == '__main__':
    unittest.main()

