/**
 * Main Application Controller for Exam Question Paper Generator
 * CoreAlgorithm PROBLEM95 - Design and Analysis of Algorithms
 */

const App = {
  currentView: 'dashboard',
  theme: 'light',

  init() {
    this.initTheme();
    this.initNavigation();
    this.initMobileMenu();
    this.initGlobalSearch();
    this.loadInitialView();
  },

  initTheme() {
    const savedTheme = localStorage.getItem('daa_exam_theme') || 'light';
    this.setTheme(savedTheme);

    const toggleBtn = document.getElementById('themeToggleBtn');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => {
        const nextTheme = this.theme === 'light' ? 'dark' : 'light';
        this.setTheme(nextTheme);
      });
    }
  },

  setTheme(theme) {
    this.theme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('daa_exam_theme', theme);

    const themeLabel = document.getElementById('themeLabel');
    const themeIcon = document.getElementById('themeIcon');
    if (themeLabel) {
      themeLabel.textContent = theme === 'dark' ? 'Dark Slate' : 'Light Mode';
    }
    if (themeIcon) {
      themeIcon.innerHTML = theme === 'dark' 
        ? `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M1 12h2M21 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4"/></svg>`
        : `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`;
    }

    // Refresh charts on theme switch if Analytics is active
    if (window.AnalyticsView && this.currentView === 'analytics') {
      window.AnalyticsView.renderCharts();
    }
  },

  initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const view = item.getAttribute('data-view');
        if (view) {
          this.switchView(view);
          // Close mobile menu if open
          document.querySelector('.sidebar')?.classList.remove('mobile-open');
        }
      });
    });

    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');
    if (sidebarToggle && sidebar) {
      sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
      });
    }
  },

  initMobileMenu() {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const sidebar = document.querySelector('.sidebar');
    if (mobileMenuBtn && sidebar) {
      mobileMenuBtn.addEventListener('click', () => {
        sidebar.classList.toggle('mobile-open');
      });
    }
  },

  initGlobalSearch() {
    const globalSearch = document.getElementById('globalSearchInput');
    if (globalSearch) {
      globalSearch.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          const val = globalSearch.value.trim();
          if (val) {
            this.switchView('questions');
            const qSearch = document.getElementById('qSearchInput');
            if (qSearch) {
              qSearch.value = val;
              if (window.QuestionBank) window.QuestionBank.loadQuestions(1);
            }
          }
        }
      });
    }
  },

  switchView(viewName) {
    this.currentView = viewName;

    // Update active sidebar nav
    document.querySelectorAll('.nav-item').forEach(item => {
      item.classList.toggle('active', item.getAttribute('data-view') === viewName);
    });

    // Update breadcrumb
    const breadcrumb = document.getElementById('breadcrumbCurrent');
    if (breadcrumb) {
      const titles = {
        dashboard: 'Dashboard',
        syllabus: 'Syllabus Manager',
        questions: 'Question Bank (Reference / Cache)',
        generate: 'Syllabus Paper Generator',
        visualizer: 'Algorithm Lab',
        papers: 'Generated Papers',
        comparison: 'Algorithm Comparison',
        analytics: 'Analytics',
        settings: 'Settings & Presets'
      };
      breadcrumb.textContent = titles[viewName] || viewName;
    }

    // Toggle view sections
    document.querySelectorAll('.view-section').forEach(sec => {
      sec.classList.remove('active');
    });
    const target = document.getElementById(`view-${viewName}`);
    if (target) {
      target.classList.add('active');
    }

    // View-specific initialization triggers
    if (viewName === 'dashboard' && window.DashboardView) window.DashboardView.load();
    if (viewName === 'syllabus' && window.SyllabusManager) window.SyllabusManager.init();
    if (viewName === 'questions' && window.QuestionBank) window.QuestionBank.init();
    if (viewName === 'generate' && window.GeneratorView) window.GeneratorView.init();
    if (viewName === 'visualizer' && window.VisualizerView) window.VisualizerView.init();
    if (viewName === 'papers' && window.PaperHistoryView) window.PaperHistoryView.load();
    if (viewName === 'comparison' && window.ComparisonView) window.ComparisonView.init();
    if (viewName === 'analytics' && window.AnalyticsView) window.AnalyticsView.load();
    if (viewName === 'settings' && window.SettingsView) window.SettingsView.load();
  },

  loadInitialView() {
    this.switchView('dashboard');
  },

  // Modal Helpers
  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('show');
      document.body.style.overflow = 'hidden';
    }
  },

  closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('show');
      document.body.style.overflow = '';
    }
  },

  // Toast Notification System
  showToast(message, type = 'info', duration = 3500) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    let iconSvg = '';
    if (type === 'success') {
      iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>`;
    } else if (type === 'error') {
      iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>`;
    } else if (type === 'warning') {
      iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`;
    } else {
      iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`;
    }

    toast.innerHTML = `
      <div style="color: var(--${type === 'info' ? 'primary' : type}); display: flex; align-items: center;">${iconSvg}</div>
      <div style="flex: 1;">${message}</div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      setTimeout(() => toast.remove(), 250);
    }, duration);
  }
};

document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
