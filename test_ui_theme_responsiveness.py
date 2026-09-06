"""
UI & Theme Responsiveness Verification Test Suite
Tests:
1. CSS variables & compatibility aliases for Dark and Light themes.
2. Light mode styling across Sidebar, Topbar, Matrix, Cards, Tables, Modals, Forms.
3. Header flex layout, min-width: 0, responsive search shrinking, and Add button visibility.
4. JS ThemeManager methods (toggle, setTheme, init) and QuickSettingsManager delegators.
5. Anti-flicker preload scripts in base, login, and register templates.
6. HTML rendering for all portal pages.
"""

import unittest
import re
from app import app

class UIThemeResponsivenessTests(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        with open('static/css/style.css', 'r', encoding='utf-8') as f:
            self.css = f.read()

        with open('static/js/app.js', 'r', encoding='utf-8') as f:
            self.js = f.read()

        with open('templates/base.html', 'r', encoding='utf-8') as f:
            self.base_html = f.read()

        with open('templates/login.html', 'r', encoding='utf-8') as f:
            self.login_html = f.read()

        with open('templates/register.html', 'r', encoding='utf-8') as f:
            self.register_html = f.read()

    def test_css_theme_variables_and_aliases(self):
        """Verify CSS tokens and aliases exist for both Dark and Light themes."""
        self.assertIn('--border-color:', self.css)
        self.assertIn('--bg-secondary:', self.css)
        self.assertIn('--bg-card:', self.css)
        self.assertIn('[data-theme="dark"]', self.css)
        self.assertIn('[data-theme="light"]', self.css)

    def test_light_mode_sidebar_and_components_styled(self):
        """Verify Light Mode has dedicated styling for sidebar, topbar, cards, and tables."""
        self.assertIn('[data-theme="light"] .sidebar', self.css)
        self.assertIn('[data-theme="light"] .nav-link', self.css)
        self.assertIn('[data-theme="light"] .card', self.css)
        self.assertIn('[data-theme="light"] .data-table', self.css)
        self.assertIn('[data-theme="light"] .form-control', self.css)
        self.assertIn('[data-theme="light"] .modal-window', self.css)

    def test_matrix_cell_heatmap_not_overwritten_in_light_mode(self):
        """Verify the 5x5 heatmap cell colors are not wiped out by white background in light mode."""
        self.assertNotIn('[data-theme="light"] .matrix-cell {\n  background-color: #ffffff;\n}', self.css)
        self.assertIn('[data-theme="light"] .matrix-cell.cell-critical', self.css)
        self.assertIn('[data-theme="light"] .matrix-cell.cell-high', self.css)
        self.assertIn('[data-theme="light"] .matrix-cell.cell-medium', self.css)
        self.assertIn('[data-theme="light"] .matrix-cell.cell-low', self.css)

    def test_header_and_main_wrapper_responsiveness(self):
        """Verify main-wrapper, topbar, topbar-left, topbar-center, and user-chip have proper flex/min-width constraints."""
        self.assertIn('.main-wrapper {', self.css)
        self.assertIn('max-width: calc(100% - var(--sidebar-width));', self.css)
        self.assertIn('min-width: 0;', self.css)
        self.assertIn('.user-chip-name {', self.css)
        self.assertIn('#quickAddRiskBtn {', self.css)
        self.assertIn('@media (max-width: 1400px)', self.css)
        self.assertIn('@media (max-width: 1250px)', self.css)
        self.assertIn('@media (max-width: 992px)', self.css)

    def test_grid_tracks_use_minmax_zero(self):
        """Verify charts and kpi grids use minmax(0, 1fr) to prevent overflow blowout."""
        self.assertIn('grid-template-columns: repeat(2, minmax(0, 1fr));', self.css)
        self.assertIn('grid-template-columns: repeat(3, minmax(0, 1fr));', self.css)

    def test_theme_manager_methods_in_js(self):
        """Verify ThemeManager has toggle(), setTheme(), init(), and synchronizes UI & charts."""
        self.assertIn('toggle()', self.js)
        self.assertIn('setTheme(theme, syncUI', self.js)
        self.assertIn('localStorage.setItem(\'srmm_theme\'', self.js)
        self.assertIn('refreshAllCharts', self.js)

    def test_quick_settings_delegators_in_js(self):
        """Verify QuickSettingsManager has setRegion and setLanguage."""
        self.assertIn('setRegion(val)', self.js)
        self.assertIn('setLanguage(val)', self.js)

    def test_anti_flicker_script_in_templates(self):
        """Verify base.html, login.html, and register.html include the early preload theme script."""
        script_pattern = r"localStorage\.getItem\(['\"]srmm_theme['\"]\)"
        self.assertTrue(re.search(script_pattern, self.base_html))
        self.assertTrue(re.search(script_pattern, self.login_html))
        self.assertTrue(re.search(script_pattern, self.register_html))

    def test_all_routes_render_html_with_new_classes(self):
        """Verify all routes return 200 OK and render correctly with user-chip-name and header controls."""
        routes = ['/dashboard', '/matrix', '/risks', '/mitigation', '/analytics', '/reports', '/settings', '/login', '/register']
        for r in routes:
            res = self.client.get(r)
            self.assertEqual(res.status_code, 200, f"Route {r} failed with {res.status_code}")
            if r not in ['/login', '/register']:
                self.assertIn(b'quickAddRiskBtn', res.data)
                self.assertIn(b'themeToggleBtn', res.data)
                self.assertIn(b'user-chip-name', res.data)

if __name__ == '__main__':
    unittest.main()
