/**
 * Software Risk Mitigation Matrix Pro - Core Application Engine
 * Includes I18n Translation (English/Hindi), Region Customization (Indian/International),
 * Theme Engine (Dark/Light), and Top-Right Quick Settings.
 */

// ==========================================================================
// 1. TRANSLATION & I18N ENGINE
// ==========================================================================
const I18nEngine = {
  currentLang: 'en',

  translations: {
    en: {
      // Topbar & Nav
      nav_dashboard: "Dashboard",
      nav_matrix: "5×5 Risk Matrix",
      nav_risks: "Risk Register",
      nav_assessment: "Project Assessment",
      nav_mitigation: "Mitigation Plans",
      nav_mapping: "Risk ↔ Mitigation Mapping",
      nav_analytics: "Analytics & Trends",
      nav_reports: "Compliance Reports",
      nav_settings: "Settings & Team",
      search_placeholder: "Search risks, owners, mitigations, CVEs...",
      notifications: "Notifications",
      sign_out: "Sign Out",

      // Actions & Buttons
      btn_add_risk: "Add Risk",
      btn_save_risk: "Save Risk",
      btn_edit: "Edit",
      btn_delete: "Delete",
      btn_cancel: "Cancel",
      btn_export_csv: "Export CSV",
      btn_search: "Search",
      btn_reset_filters: "Reset Filters",
      btn_view_details: "View Details",
      btn_record_reassessment: "Record Reassessment",
      btn_assess_new_threat: "Assess New Threat",
      btn_create_project: "Create Project",
      btn_continue: "Continue",
      btn_back: "Back",
      btn_sign_in: "Sign In",
      btn_create_account: "Create Account",
      btn_switch_demo: "Switch Demo User",
      btn_reset_dataset: "Reset Dataset",
      btn_filter: "Filter",
      btn_apply: "Apply",
      btn_close: "Close",
      btn_matrix_view: "5×5 Matrix View",

      // Risk Severities
      sev_critical: "Critical",
      sev_high: "High",
      sev_medium: "Medium",
      sev_low: "Low",

      // Risk Lifecycle Statuses
      stat_identified: "Identified",
      stat_assessed: "Assessed",
      stat_mitigation_planned: "Mitigation Planned",
      stat_in_progress: "In Progress",
      stat_under_review: "Under Review",
      stat_reduced: "Reduced",
      stat_mitigated: "Mitigated",
      stat_closed: "Closed",

      // Headers & Labels
      lbl_total_risks: "Total Active Risks",
      lbl_critical_severity: "Critical Severity",
      lbl_high_severity: "High Severity",
      lbl_medium_severity: "Medium Severity",
      lbl_low_severity: "Low Severity",
      lbl_overall_reduction: "Overall Risk Reduction",
      lbl_risk_score: "Risk Score",
      lbl_initial_score: "Initial Score",
      lbl_current_score: "Current Score",
      lbl_risk_desc: "Risk Description",
      lbl_mitigation_strategy: "Mitigation Strategy",
      lbl_action_steps: "Action Steps",
      lbl_likelihood: "Likelihood",
      lbl_impact: "Impact Severity",
      lbl_owner: "Responsible Owner",
      lbl_department: "Department",
      lbl_target_date: "Target Date",
      lbl_category: "Category",
      lbl_status: "Status",
      lbl_progress: "Progress",
      lbl_reduction: "Risk Reduction",
      lbl_what_changed: "What Changed?",
      lbl_score_history: "Score History",
      lbl_audit_ref: "Audit Reference ID",
      lbl_objective: "Objective: Identify, prioritize and reduce software risks through measurable mitigation actions.",
      lbl_no_risks_found: "No risks found matching your criteria",
      lbl_no_mitigations: "No mitigation plans recorded yet",
      lbl_quick_reassess: "Quick Reassess",
      lbl_mitigation_progress: "Mitigation Progress",
      tooltip_risk_score: "Shows how serious a risk is based on its likelihood and impact.",
      tooltip_residual_risk: "The risk that remains after mitigation.",
      tooltip_mitigation: "Action steps taken to reduce the chance or impact of a risk.",
      tooltip_risk_reduction: "Shows how much the risk has decreased after mitigation.",
      tooltip_monte_carlo: "Uses many possible scenarios to estimate potential outcomes.",
      tooltip_financial_exposure: "Estimated monetary cost or loss if the risk occurs.",
      lbl_demo_data: "Demo Data",
      lbl_user_data: "User Analysis",
      lbl_how_it_works: "How This Software Works",
      step_identify_title: "1. Identify Risk",
      step_identify_desc: "Find and write down potential threats or issues in your software project.",
      step_assess_title: "2. Assess Risk",
      step_assess_desc: "Rate the likelihood and impact from 1 to 5 to get a clear Risk Score.",
      step_mitigate_title: "3. Select Mitigation",
      step_mitigate_desc: "Plan practical actions and assign an owner to fix or reduce the risk.",
      step_track_title: "4. Track Risk Reduction",
      step_track_desc: "Monitor progress as the risk score decreases towards safe levels.",
      step_report_title: "5. Generate Report",
      step_report_desc: "Export audit-ready reports and executive summaries with one click.",

      // Quick Settings & Profile
      quick_settings: "Quick Settings",
      region_title: "Region / User Type",
      lang_title: "Language",
      theme_title: "Theme",
      opt_indian: "Indian (INR ₹)",
      opt_intl: "International (USD $)",
      opt_en: "English",
      opt_hi: "हिंदी (Hindi)",
      opt_dark: "Dark",
      opt_light: "Light",
      profile_role_admin: "Admin",
      profile_role_manager: "Risk Manager",
      profile_role_dev: "Developer",
      profile_role_auditor: "Auditor"
    },

    hi: {
      // Topbar & Nav
      nav_dashboard: "डैशबोर्ड",
      nav_matrix: "5×5 जोखिम मैट्रिक्स",
      nav_risks: "जोखिम रजिस्टर",
      nav_assessment: "परियोजना जोखिम मूल्यांकन",
      nav_mitigation: "निवारण योजनाएं",
      nav_mapping: "जोखिम ↔ निवारण मैपिंग",
      nav_analytics: "एनालिटिक्स और रुझान",
      nav_reports: "अनुपालन रिपोर्ट",
      nav_settings: "सेटिंग्स और टीम",
      search_placeholder: "जोखिम, स्वामी, निवारण योजना, CVE खोजें...",
      notifications: "सूचनाएं",
      sign_out: "साइन आउट",

      // Actions & Buttons
      btn_add_risk: "जोखिम जोड़ें",
      btn_save_risk: "जोखिम सेव करें",
      btn_edit: "संपादित करें",
      btn_delete: "हटाएं",
      btn_cancel: "रद्द करें",
      btn_export_csv: "CSV निर्यात करें",
      btn_search: "खोजें",
      btn_reset_filters: "फ़िल्टर रीसेट करें",
      btn_view_details: "विवरण देखें",
      btn_record_reassessment: "पुनर्मूल्यांकन दर्ज करें",
      btn_assess_new_threat: "नया खतरा जांचें",
      btn_create_project: "परियोजना बनाएं",
      btn_continue: "आगे बढ़ें",
      btn_back: "पीछे जाएं",
      btn_sign_in: "साइन इन करें",
      btn_create_account: "खाता बनाएं",
      btn_switch_demo: "डेमो यूज़र बदलें",
      btn_reset_dataset: "डेटासेट रीसेट करें",
      btn_filter: "फ़िल्टर",
      btn_apply: "लागू करें",
      btn_close: "बंद करें",
      btn_matrix_view: "5×5 मैट्रिक्स देखें",

      // Risk Severities
      sev_critical: "क्रिटिकल",
      sev_high: "उच्च",
      sev_medium: "मध्यम",
      sev_low: "निम्न",

      // Risk Lifecycle Statuses
      stat_identified: "पहचाना गया",
      stat_assessed: "मूल्यांकित",
      stat_mitigation_planned: "योजना बनाई गई",
      stat_in_progress: "प्रगति पर",
      stat_under_review: "समीक्षाधीन",
      stat_reduced: "कम किया गया",
      stat_mitigated: "शमित",
      stat_closed: "बंद",

      // Headers & Labels
      lbl_total_risks: "कुल सक्रिय जोखिम",
      lbl_critical_severity: "क्रिटिकल गंभीरता",
      lbl_high_severity: "उच्च गंभीरता",
      lbl_medium_severity: "मध्यम गंभीरता",
      lbl_low_severity: "निम्न गंभीरता",
      lbl_overall_reduction: "कुल जोखिम में कमी",
      lbl_risk_score: "जोखिम स्कोर",
      lbl_initial_score: "प्रारंभिक स्कोर",
      lbl_current_score: "वर्तमान स्कोर",
      lbl_risk_desc: "जोखिम का विवरण",
      lbl_mitigation_strategy: "जोखिम कम करने की रणनीति",
      lbl_action_steps: "कार्यवाही के कदम",
      lbl_likelihood: "संभावना",
      lbl_impact: "प्रभाव गंभीरता",
      lbl_owner: "जिम्मेदार स्वामी",
      lbl_department: "विभाग",
      lbl_target_date: "लक्षित तिथि",
      lbl_category: "श्रेणी",
      lbl_status: "स्थिति",
      lbl_progress: "प्रगति",
      lbl_reduction: "जोखिम में कमी",
      lbl_what_changed: "क्या बदलाव हुआ?",
      lbl_score_history: "स्कोर इतिहास",
      lbl_audit_ref: "ऑडिट संदर्भ आईडी",
      lbl_objective: "उद्देश्य: मापने योग्य निवारण कार्रवाइयों के माध्यम से सॉफ़्टवेयर जोखिमों को पहचानना, प्राथमिकता देना और कम करना।",
      lbl_no_risks_found: "आपकी खोज के अनुसार कोई जोखिम नहीं मिला",
      lbl_no_mitigations: "अभी तक कोई निवारण योजना दर्ज नहीं की गई है",
      lbl_quick_reassess: "त्वरित पुनर्मूल्यांकन",
      lbl_mitigation_progress: "निवारण प्रगति",
      tooltip_risk_score: "संभाव्यता और प्रभाव के आधार पर जोखिम की गंभीरता दर्शाता है।",
      tooltip_residual_risk: "निवारण के बाद बचा हुआ जोखिम।",
      tooltip_mitigation: "जोखिम को कम करने के लिए उठाए गए सुधारात्मक कदम।",
      tooltip_risk_reduction: "निवारण के बाद जोखिम में आई कमी को दर्शाता है।",
      tooltip_monte_carlo: "विभिन्न परिस्थितियों के आधार पर संभावित परिणामों का अनुमान लगाता है।",
      tooltip_financial_exposure: "जोखिम होने पर होने वाले संभावित वित्तीय नुकसान का अनुमान।",
      lbl_demo_data: "डेमो डेटा",
      lbl_user_data: "यूज़र विश्लेषण",
      lbl_how_it_works: "यह सॉफ़्टवेयर कैसे काम करता है",
      step_identify_title: "1. जोखिम पहचानें",
      step_identify_desc: "अपने सॉफ़्टवेयर प्रोजेक्ट में संभावित खतरों या समस्याओं को खोजें और दर्ज करें।",
      step_assess_title: "2. जोखिम का मूल्यांकन करें",
      step_assess_desc: "स्पष्ट जोखिम स्कोर प्राप्त करने के लिए 1 से 5 तक संभावना और प्रभाव का मूल्यांकन करें।",
      step_mitigate_title: "3. निवारण योजना चुनें",
      step_mitigate_desc: "जोखिम को ठीक करने या कम करने के लिए व्यावहारिक कदम उठाएं और एक स्वामी नियुक्त करें।",
      step_track_title: "4. जोखिम कमी ट्रैक करें",
      step_track_desc: "सुरक्षित स्तर तक जोखिम स्कोर कम होने पर प्रगति की निगरानी करें।",
      step_report_title: "5. रिपोर्ट तैयार करें",
      step_report_desc: "एक क्लिक में ऑडिट के लिए तैयार रिपोर्ट और सारांश निर्यात करें।",

      // Quick Settings & Profile
      quick_settings: "त्वरित सेटिंग्स",
      region_title: "क्षेत्र / यूज़र प्राथमिकता",
      lang_title: "भाषा",
      theme_title: "थीम",
      opt_indian: "भारतीय (INR ₹)",
      opt_intl: "अंतर्राष्ट्रीय (USD $)",
      opt_en: "English",
      opt_hi: "हिंदी",
      opt_dark: "डार्क",
      opt_light: "लाइट",
      profile_role_admin: "व्यवस्थापक (Admin)",
      profile_role_manager: "जोखिम प्रबंधक",
      profile_role_dev: "डेवलपर",
      profile_role_auditor: "लेखा परीक्षक (Auditor)"
    }
  },

  init() {
    const savedLang = localStorage.getItem('srmm_lang') || 'en';
    this.setLanguage(savedLang, false);
  },

  setLanguage(lang, syncUI = true) {
    this.currentLang = lang === 'hi' ? 'hi' : 'en';
    localStorage.setItem('srmm_lang', this.currentLang);
    document.cookie = `srmm_lang=${this.currentLang}; path=/; max-age=31536000; SameSite=Lax`;
    document.documentElement.setAttribute('lang', this.currentLang);

    // Apply translations across all data-i18n attributes
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (this.translations[this.currentLang] && this.translations[this.currentLang][key]) {
        el.innerText = this.translations[this.currentLang][key];
      }
    });

    // Placeholders
    const placeholders = document.querySelectorAll('[data-i18n-placeholder]');
    placeholders.forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      if (this.translations[this.currentLang] && this.translations[this.currentLang][key]) {
        el.setAttribute('placeholder', this.translations[this.currentLang][key]);
      }
    });

    // Tooltips & Titles
    const titles = document.querySelectorAll('[data-i18n-title]');
    titles.forEach(el => {
      const key = el.getAttribute('data-i18n-title');
      if (this.translations[this.currentLang] && this.translations[this.currentLang][key]) {
        el.setAttribute('title', this.translations[this.currentLang][key]);
      }
    });

    if (syncUI) {
      QuickSettingsManager.syncActiveButtons();
      QuickSettingsManager.updateProfileMetadata();
    }
  },

  t(key, fallback = '') {
    const langDict = this.translations[this.currentLang] || this.translations['en'];
    return langDict[key] || (this.translations['en'] ? this.translations['en'][key] : '') || fallback || key;
  }
};

// ==========================================================================
// 2. REGION & USER TYPE CUSTOMIZATION ENGINE (Indian vs International)
// ==========================================================================
const RegionEngine = {
  currentRegion: 'indian',

  // Name Mappings (Strictly NO Aditya Joshi)
  personMap: {
    // Standard 4 Personas
    'Rahul Patil': { indian: 'Rahul Patil', intl: 'Alex Morgan', role: 'Admin' },
    'Priya Sharma': { indian: 'Priya Sharma', intl: 'Emma Wilson', role: 'Risk Manager' },
    'Amit Kulkarni': { indian: 'Amit Kulkarni', intl: 'Daniel Smith', role: 'Developer' },
    'Sneha Deshmukh': { indian: 'Sneha Deshmukh', intl: 'Olivia Brown', role: 'Auditor' },
    'Vikram Deshmukh': { indian: 'Vikram Deshmukh', intl: 'Michael Johnson', role: 'Data Lead' },
    'Aditya Patil': { indian: 'Rahul Patil', intl: 'Alex Morgan', role: 'Admin' },
    'Neha Kulkarni': { indian: 'Priya Sharma', intl: 'Emma Wilson', role: 'Risk Manager' },
    'Rohan Deshmukh': { indian: 'Amit Kulkarni', intl: 'Daniel Smith', role: 'Developer' },
    'Alex Rivera': { indian: 'Rahul Patil', intl: 'Alex Morgan', role: 'Admin' },
    'Alex Morgan': { indian: 'Rahul Patil', intl: 'Alex Morgan', role: 'Admin' },
    'Emma Wilson': { indian: 'Priya Sharma', intl: 'Emma Wilson', role: 'Risk Manager' },
    'Daniel Smith': { indian: 'Amit Kulkarni', intl: 'Daniel Smith', role: 'Developer' },
    'Olivia Brown': { indian: 'Sneha Deshmukh', intl: 'Olivia Brown', role: 'Auditor' },
    'Michael Johnson': { indian: 'Vikram Deshmukh', intl: 'Michael Johnson', role: 'Data Lead' }
  },

  projectMap: {
    'UPI & Cloud Banking Mobile App Gateway': {
      indian: 'UPI & Cloud Banking Mobile App Gateway',
      intl: 'Global Cloud Banking & API Gateway'
    },
    'Cloud Banking Mobile App & API Gateway': {
      indian: 'UPI & Cloud Banking Mobile App Gateway',
      intl: 'Global Cloud Banking & API Gateway'
    }
  },

  init() {
    const savedRegion = localStorage.getItem('srmm_region') || 'indian';
    this.setRegion(savedRegion, false);
  },

  setRegion(region, syncUI = true) {
    this.currentRegion = (region === 'intl' || region === 'international') ? 'intl' : 'indian';
    localStorage.setItem('srmm_region', this.currentRegion);
    document.cookie = `srmm_region=${this.currentRegion}; path=/; max-age=31536000; SameSite=Lax`;
    document.documentElement.setAttribute('data-region', this.currentRegion);

    this.applyPersonNames();
    this.applyCurrencies();
    this.applyProjects();

    if (syncUI) {
      QuickSettingsManager.syncActiveButtons();
      QuickSettingsManager.updateProfileMetadata();
    }
  },

  applyPersonNames() {
    const isIndian = this.currentRegion === 'indian';

    // Elements with data-person
    document.querySelectorAll('[data-person]').forEach(el => {
      const original = el.getAttribute('data-person').trim();
      const mapped = this.personMap[original];
      if (mapped) {
        el.innerText = isIndian ? mapped.indian : mapped.intl;
      }
    });

    // Elements containing raw names
    const nameKeys = Object.keys(this.personMap);
    document.querySelectorAll('.owner-name, .risk-owner, .user-name, .lead-name, .author-name, .demo-user-card strong, .table-owner').forEach(el => {
      let text = el.innerText.trim();
      for (const k of nameKeys) {
        const item = this.personMap[k];
        if (text === item.indian || text === item.intl || text === k) {
          el.innerText = isIndian ? item.indian : item.intl;
          break;
        }
      }
    });
  },

  applyCurrencies() {
    const isIndian = this.currentRegion === 'indian';

    // Format financial values (e.g. ₹5,53,111 / ₹14,200 vs $6,500 / $14,200)
    document.querySelectorAll('[data-currency-val]').forEach(el => {
      const val = parseFloat(el.getAttribute('data-currency-val'));
      if (!isNaN(val)) {
        el.innerText = this.formatMoney(val);
      }
    });

    // Replace explicit currency badges and spans
    document.querySelectorAll('.financial-val, .currency-text').forEach(el => {
      let t = el.innerText;
      if (isIndian) {
        t = t.replace(/\$14,200/g, '₹14,200')
             .replace(/\$6,500/g, '₹5,53,111')
             .replace(/\$([0-9,]+)/g, '₹$1');
      } else {
        t = t.replace(/₹14,200/g, '$14,200')
             .replace(/₹5,53,111/g, '$6,500')
             .replace(/₹([0-9,]+)/g, '$$$1');
      }
      el.innerText = t;
    });
  },

  applyProjects() {
    const isIndian = this.currentRegion === 'indian';
    document.querySelectorAll('[data-project-title], .project-title-text').forEach(el => {
      const original = el.getAttribute('data-project-title') || el.innerText.trim();
      const mapped = this.projectMap[original];
      if (mapped) {
        el.innerText = isIndian ? mapped.indian : mapped.intl;
      }
    });
  },

  formatMoney(num) {
    const isIndian = this.currentRegion === 'indian';
    if (isIndian) {
      // Indian numbering system
      const formatted = new Intl.NumberFormat('en-IN').format(num);
      return `₹${formatted}`;
    } else {
      // International USD format
      const formatted = new Intl.NumberFormat('en-US').format(num);
      return `$${formatted}`;
    }
  }
};

// ==========================================================================
// 3. THEME MANAGEMENT (Dark / Light)
// ==========================================================================
const ThemeManager = {
  init() {
    const savedTheme = localStorage.getItem('srmm_theme') || 'dark';
    this.setTheme(savedTheme, false);

    const toggleBtn = document.getElementById('themeToggleBtn');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', (e) => {
        e.preventDefault();
        this.toggle();
      });
    }
  },

  toggle() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    this.setTheme(newTheme);
  },

  setTheme(theme, syncUI = true) {
    const activeTheme = theme === 'light' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', activeTheme);
    localStorage.setItem('srmm_theme', activeTheme);
    document.cookie = `srmm_theme=${activeTheme}; path=/; max-age=31536000; SameSite=Lax`;
    
    // Update Topbar Theme Switcher UI
    const themeIcon = document.getElementById('topbarThemeIcon');
    const themeLabel = document.getElementById('topbarThemeLabel');
    if (themeIcon) {
      themeIcon.className = activeTheme === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
      themeIcon.style.color = activeTheme === 'dark' ? '#f59e0b' : '#2563eb';
    }
    if (themeLabel) {
      themeLabel.innerText = activeTheme === 'dark' ? 'Light Mode' : 'Dark Mode';
    }

    // Update Floating Theme Icons (Login / Register)
    const loginThemeIcon = document.getElementById('loginThemeIcon') || document.getElementById('regThemeIcon');
    if (loginThemeIcon) {
      loginThemeIcon.className = activeTheme === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
    }

    const toggleBtn = document.getElementById('themeToggleBtn');
    if (toggleBtn) {
      toggleBtn.setAttribute('title', activeTheme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode');
    }

    if (syncUI && window.QuickSettingsManager) {
      QuickSettingsManager.syncActiveButtons();
      QuickSettingsManager.updateProfileMetadata();
    }

    // Refresh charts if on a page with active charts
    if (window.ChartEngine && window.ChartEngine.instances) {
      if (window.refreshAllCharts) {
        window.refreshAllCharts();
      }
    }
  }
};

// ==========================================================================
// 4. TOP-RIGHT QUICK SETTINGS CONTROLLER
// ==========================================================================
const QuickSettingsManager = {
  init() {
    this.bindEvents();
    this.syncActiveButtons();
    this.updateProfileMetadata();
  },

  setRegion(val) {
    RegionEngine.setRegion(val);
    this.syncActiveButtons();
    this.updateProfileMetadata();
  },

  setLanguage(val) {
    I18nEngine.setLanguage(val);
    this.syncActiveButtons();
    this.updateProfileMetadata();
  },

  bindEvents() {
    // Quick Settings Dropdown Toggle
    const btn = document.getElementById('quickSettingsBtn');
    const menu = document.getElementById('quickSettingsMenu');
    if (btn && menu) {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = menu.style.display === 'block';
        menu.style.display = isOpen ? 'none' : 'block';
      });

      document.addEventListener('click', (e) => {
        if (!menu.contains(e.target) && !btn.contains(e.target)) {
          menu.style.display = 'none';
        }
      });
    }

    // Segmented Buttons in Quick Settings Popover & Settings Page
    document.querySelectorAll('[data-set-region]').forEach(el => {
      el.addEventListener('click', () => {
        const val = el.getAttribute('data-set-region');
        RegionEngine.setRegion(val);
        Toast.show('Region Preference', val === 'indian' ? 'Indian (INR ₹) active' : 'International (USD $) active', 'info', 2000);
      });
    });

    document.querySelectorAll('[data-set-lang]').forEach(el => {
      el.addEventListener('click', () => {
        const val = el.getAttribute('data-set-lang');
        I18nEngine.setLanguage(val);
        Toast.show('Language', val === 'hi' ? 'हिंदी भाषा चुनी गई' : 'English language active', 'info', 2000);
      });
    });

    document.querySelectorAll('[data-set-theme]').forEach(el => {
      el.addEventListener('click', () => {
        const val = el.getAttribute('data-set-theme');
        ThemeManager.setTheme(val);
      });
    });
  },

  syncActiveButtons() {
    const region = RegionEngine.currentRegion;
    const lang = I18nEngine.currentLang;
    const theme = document.documentElement.getAttribute('data-theme') || 'dark';

    document.querySelectorAll('[data-set-region]').forEach(el => {
      el.classList.toggle('active', el.getAttribute('data-set-region') === region);
    });

    document.querySelectorAll('[data-set-lang]').forEach(el => {
      el.classList.toggle('active', el.getAttribute('data-set-lang') === lang);
    });

    document.querySelectorAll('[data-set-theme]').forEach(el => {
      el.classList.toggle('active', el.getAttribute('data-set-theme') === theme);
    });
  },

  updateProfileMetadata() {
    const region = RegionEngine.currentRegion;
    const lang = I18nEngine.currentLang;
    const theme = document.documentElement.getAttribute('data-theme') || 'dark';

    const regionLabel = region === 'indian' ? '🇮🇳 India' : '🌐 Intl';
    const langLabel = lang === 'hi' ? '🌐 हिंदी' : '🌐 EN';
    const themeLabel = theme === 'dark' ? '🌙 Dark' : '☀️ Light';

    const text = `${regionLabel} • ${langLabel} • ${themeLabel}`;
    document.querySelectorAll('.profile-prefs-pill, #sidebarUserPrefs').forEach(el => {
      el.innerText = text;
    });

    // Update demo user buttons on login & settings
    const isIndian = region === 'indian';
    const adminBtn = document.getElementById('demoBtnAdmin');
    const mgrBtn = document.getElementById('demoBtnManager');
    const devBtn = document.getElementById('demoBtnDev');
    const audBtn = document.getElementById('demoBtnAuditor');

    if (adminBtn) adminBtn.innerHTML = `<i class="fa-solid fa-crown"></i> ${isIndian ? 'Rahul Patil' : 'Alex Morgan'} (Admin)`;
    if (mgrBtn) mgrBtn.innerHTML = `<i class="fa-solid fa-shield-halved"></i> ${isIndian ? 'Priya Sharma' : 'Emma Wilson'} (Risk Manager)`;
    if (devBtn) devBtn.innerHTML = `<i class="fa-solid fa-code"></i> ${isIndian ? 'Amit Kulkarni' : 'Daniel Smith'} (Developer)`;
    if (audBtn) audBtn.innerHTML = `<i class="fa-solid fa-file-shield"></i> ${isIndian ? 'Sneha Deshmukh' : 'Olivia Brown'} (Auditor)`;
  }
};

// ==========================================================================
// 5. TOAST NOTIFICATION SYSTEM
// ==========================================================================
const Toast = {
  container: null,

  init() {
    let el = document.getElementById('toastContainer');
    if (!el) {
      el = document.createElement('div');
      el.id = 'toastContainer';
      el.className = 'toast-container';
      document.body.appendChild(el);
    }
    this.container = el;
  },

  show(title, message, type = 'info', duration = 3500) {
    if (!this.container) this.init();

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const iconMap = {
      success: 'fa-check',
      error: 'fa-triangle-exclamation',
      warning: 'fa-bell',
      info: 'fa-circle-info'
    };

    toast.innerHTML = `
      <div class="toast-icon">
        <i class="fa-solid ${iconMap[type] || 'fa-info'}"></i>
      </div>
      <div class="toast-content">
        <div class="toast-title">${title}</div>
        <div class="toast-message">${message}</div>
      </div>
      <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
    `;

    this.container.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 10);

    if (duration > 0) {
      setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 400);
      }, duration);
    }
  }
};

// ==========================================================================
// 6. MODAL SYSTEM
// ==========================================================================
const ModalManager = {
  open(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    }
  },

  close(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('active');
      document.body.style.overflow = '';
    }
  },

  initGlobalListeners() {
    document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
      backdrop.addEventListener('click', (e) => {
        if (e.target === backdrop) {
          backdrop.classList.remove('active');
          document.body.style.overflow = '';
        }
      });
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        document.querySelectorAll('.modal-backdrop.active').forEach(modal => {
          modal.classList.remove('active');
          document.body.style.overflow = '';
        });
      }

      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('globalSearchInput');
        if (searchInput) {
          searchInput.focus();
          searchInput.select();
        }
      }
    });
  }
};

// ==========================================================================
// 7. CALCULATION & NUMBER ANIMATIONS
// ==========================================================================
function animateValue(obj, start, end, duration, decimals = 0, suffix = '') {
  if (!obj) return;
  let startTimestamp = null;
  const step = (timestamp) => {
    if (!startTimestamp) startTimestamp = timestamp;
    const progress = Math.min((timestamp - startTimestamp) / duration, 1);
    const easeOutProgress = 1 - Math.pow(1 - progress, 3);
    const currentVal = (start + (end - start) * easeOutProgress).toFixed(decimals);
    obj.innerText = currentVal + suffix;
    if (progress < 1) {
      window.requestAnimationFrame(step);
    }
  };
  window.requestAnimationFrame(step);
}

function calculateRiskScore(probability, impact) {
  const p = parseInt(probability, 10) || 1;
  const i = parseInt(impact, 10) || 1;
  const score = p * i;
  let level = 'Low';
  let badgeClass = 'badge-risk-low';

  if (score >= 17) {
    level = 'Critical';
    badgeClass = 'badge-risk-critical';
  } else if (score >= 10) {
    level = 'High';
    badgeClass = 'badge-risk-high';
  } else if (score >= 5) {
    level = 'Medium';
    badgeClass = 'badge-risk-medium';
  }

  return { score, level, badgeClass, probability: p, impact: i };
}

function setupLiveRiskCalculator(probInputId, impInputId, scoreDisplayId, levelDisplayId) {
  const probEl = document.getElementById(probInputId);
  const impEl = document.getElementById(impInputId);
  const scoreEl = document.getElementById(scoreDisplayId);
  const levelEl = document.getElementById(levelDisplayId);

  if (!probEl || !impEl) return;

  function update() {
    const calc = calculateRiskScore(probEl.value, impEl.value);
    if (scoreEl) scoreEl.innerText = calc.score;
    if (levelEl) {
      const translatedLevel = I18nEngine.t(`sev_${calc.level.toLowerCase()}`, calc.level);
      levelEl.innerText = translatedLevel;
      levelEl.className = `badge ${calc.badgeClass}`;
    }
  }

  probEl.addEventListener('input', update);
  impEl.addEventListener('input', update);
  probEl.addEventListener('change', update);
  impEl.addEventListener('change', update);
  update();
}

function setupMobileNav() {
  const menuBtn = document.getElementById('mobileMenuBtn');
  const sidebar = document.querySelector('.sidebar');
  if (menuBtn && sidebar) {
    menuBtn.addEventListener('click', () => {
      sidebar.classList.toggle('mobile-open');
    });

    document.addEventListener('click', (e) => {
      if (sidebar.classList.contains('mobile-open') && !sidebar.contains(e.target) && !menuBtn.contains(e.target)) {
        sidebar.classList.remove('mobile-open');
      }
    });
  }
}

function setupGlobalSearch() {
  const searchInput = document.getElementById('globalSearchInput');
  if (searchInput) {
    searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const query = encodeURIComponent(searchInput.value.trim());
        if (query) {
          window.location.href = `/risks?search=${query}`;
        }
      }
    });
  }
}

function loginAsDemo(role) {
  fetch(`/api/demo-login/${role}`, { method: 'POST' })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        Toast.show('Authenticated', data.message, 'success');
        setTimeout(() => window.location.href = data.redirect, 500);
      } else {
        Toast.show('Error', data.message, 'error');
      }
    })
    .catch(() => Toast.show('Error', 'Demo login request failed', 'error'));
}

function markNotificationRead(id, btn) {
  fetch(`/api/notifications/${id}/read`, { method: 'POST' })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        if (btn) {
          const item = btn.closest('.notif-item');
          if (item) item.style.opacity = '0.5';
          btn.remove();
        }
        Toast.show('Notification', 'Marked as read', 'info');
      }
    });
}

// ==========================================================================
// 8. DOM READY BOOTSTRAP
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
  ThemeManager.init();
  I18nEngine.init();
  RegionEngine.init();
  QuickSettingsManager.init();
  Toast.init();
  ModalManager.initGlobalListeners();
  setupMobileNav();
  setupGlobalSearch();

  // Animate KPI numbers
  document.querySelectorAll('[data-counter]').forEach(el => {
    const target = parseFloat(el.getAttribute('data-counter'));
    const decimals = parseInt(el.getAttribute('data-decimals') || '0', 10);
    const suffix = el.getAttribute('data-suffix') || '';
    animateValue(el, 0, target, 1200, decimals, suffix);
  });
});
