"""
Deep programmatic verification script for the updated 5x5 Risk Assessment Matrix
"""
import unittest
import json
from app import app
from database.db import get_db_connection, query_db

class DeepMatrixVerification(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_matrix_page_html(self):
        """Verify matrix page contains all necessary elements."""
        res = self.client.get('/matrix')
        self.assertEqual(res.status_code, 200)
        html = res.data.decode('utf-8')
        
        # Check Explanation
        self.assertIn("Use the matrix to identify how serious each software risk is based on its probability and impact.", html)
        
        # Check Legend
        self.assertIn("Critical", html)
        self.assertIn("High", html)
        self.assertIn("Medium", html)
        self.assertIn("Low", html)
        
        # Check Axis
        self.assertIn("IMPACT", html)
        self.assertIn("PROBABILITY", html)
        self.assertIn("Very High", html)
        self.assertIn("Very Low", html)
        
        # Check Inspector Panel
        self.assertIn("Matrix Cell Inspector", html)
        self.assertIn("inspectorCoordBadge", html)
        self.assertIn("inspectorScoreVal", html)
        self.assertIn("inspectorRisksList", html)
        self.assertIn("Clear Matrix Filter", html)
        self.assertIn("View in Risk Register", html)

    def test_api_matrix_data_full_25_cells(self):
        """Verify /api/matrix-data has 5 rows, 5 cells each, and exact mathematical scores."""
        res = self.client.get('/api/matrix-data')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        
        self.assertIn('matrix_rows', data)
        self.assertEqual(len(data['matrix_rows']), 5)
        
        expected_impacts = [5, 4, 3, 2, 1]
        for idx, row in enumerate(data['matrix_rows']):
            imp = expected_impacts[idx]
            self.assertEqual(row['impact_level'], imp)
            self.assertEqual(len(row['cells']), 5)
            
            for p_idx, cell in enumerate(row['cells']):
                prob = p_idx + 1
                expected_score = imp * prob
                self.assertEqual(cell['impact'], imp)
                self.assertEqual(cell['probability'], prob)
                self.assertEqual(cell['score'], expected_score)
                
                # Check severity thresholds
                if expected_score >= 17:
                    self.assertEqual(cell['level'], 'Critical')
                elif expected_score >= 10:
                    self.assertEqual(cell['level'], 'High')
                elif expected_score >= 5:
                    self.assertEqual(cell['level'], 'Medium')
                else:
                    self.assertEqual(cell['level'], 'Low')

    def test_matrix_cell_filtering_in_risk_register(self):
        """Verify /risks?probability=2&impact=3 returns filtered records."""
        res = self.client.get('/api/risks?probability=2&impact=3')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertGreater(data['total'], 0)
        for r in data['risks']:
            self.assertEqual(r['probability'], 2)
            self.assertEqual(r['impact'], 3)
            self.assertEqual(r['risk_score'], 6)

    def test_add_risk_places_in_matrix_cell(self):
        """Verify creating a risk with prob 4 and imp 5 places it into score 20 cell."""
        payload = {
            'name': 'Zero-Day TLS Vulnerability',
            'category_id': 2,
            'probability': 4,
            'impact': 5,
            'status': 'Open',
            'owner': 'SecOps Team',
            'department': 'Security',
            'mitigation_strategy': 'Patch OpenSSL library immediately across all clusters.'
        }
        res_create = self.client.post('/api/risks', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res_create.status_code, 201)
        data_create = json.loads(res_create.data)
        self.assertEqual(data_create['risk_score'], 20)
        self.assertEqual(data_create['risk_level'], 'Critical')
        risk_id = data_create['risk_id']
        
        # Verify in matrix
        res_matrix = self.client.get('/api/matrix-data')
        data_matrix = json.loads(res_matrix.data)
        
        # Find cell with impact 5, prob 4
        target_cell = None
        for row in data_matrix['matrix_rows']:
            if row['impact_level'] == 5:
                target_cell = row['cells'][3] # prob 4
                break
        
        self.assertIsNotNone(target_cell)
        self.assertEqual(target_cell['score'], 20)
        risk_ids_in_cell = [r['id'] for r in target_cell['risks']]
        self.assertIn(risk_id, risk_ids_in_cell)
        
        # Clean up
        self.client.delete(f'/api/risks/{risk_id}')

if __name__ == '__main__':
    unittest.main()
