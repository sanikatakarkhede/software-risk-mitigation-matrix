/**
 * Chart.js Visualizations & Theme-Adaptive Plugins
 */

const ChartEngine = {
  instances: {},

  getThemeColors() {
    const isDark = (document.documentElement.getAttribute('data-theme') || 'dark') === 'dark';
    return {
      textColor: isDark ? '#94a3b8' : '#64748b',
      gridColor: isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(15, 23, 42, 0.06)',
      tooltipBg: isDark ? '#1e293b' : '#ffffff',
      tooltipText: isDark ? '#f8fafc' : '#0f172a',
      tooltipBorder: isDark ? 'rgba(255, 255, 255, 0.1)' : '#e2e8f0'
    };
  },

  destroy(id) {
    if (this.instances[id]) {
      this.instances[id].destroy();
      delete this.instances[id];
    }
  },

  // 1. Risk Distribution Doughnut Chart
  renderDistribution(canvasId, levelCounts) {
    this.destroy(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const colors = this.getThemeColors();
    const data = {
      labels: ['Critical', 'High', 'Medium', 'Low'],
      datasets: [{
        data: [
          levelCounts.Critical || 0,
          levelCounts.High || 0,
          levelCounts.Medium || 0,
          levelCounts.Low || 0
        ],
        backgroundColor: [
          '#ef4444', // Critical Red
          '#f97316', // High Orange
          '#f59e0b', // Medium Amber
          '#10b981'  // Low Green
        ],
        borderColor: colors.tooltipBg,
        borderWidth: 3,
        hoverOffset: 8
      }]
    };

    this.instances[canvasId] = new Chart(ctx, {
      type: 'doughnut',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '72%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: colors.textColor,
              font: { family: "'Inter', sans-serif", size: 12, weight: 600 },
              padding: 18,
              usePointStyle: true,
              pointStyle: 'circle'
            }
          },
          tooltip: {
            backgroundColor: colors.tooltipBg,
            titleColor: colors.tooltipText,
            bodyColor: colors.tooltipText,
            borderColor: colors.tooltipBorder,
            borderWidth: 1,
            padding: 12,
            boxPadding: 6,
            usePointStyle: true,
            callbacks: {
              label: function(context) {
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const val = context.raw || 0;
                const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
                return ` ${context.label}: ${val} risks (${pct}%)`;
              }
            }
          }
        },
        animation: {
          animateScale: true,
          animateRotate: true
        }
      }
    });
  },

  // 2. Risk Trend Line Chart
  renderTrend(canvasId, trendData) {
    this.destroy(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const colors = this.getThemeColors();
    const labels = trendData.map(d => d.recorded_date);
    const scores = trendData.map(d => d.avg_score);

    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 260);
    gradient.addColorStop(0, 'rgba(99, 102, 241, 0.45)');
    gradient.addColorStop(1, 'rgba(99, 102, 241, 0.0)');

    this.instances[canvasId] = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels.length ? labels : ['May', 'Jun', 'Jul', 'Aug'],
        datasets: [{
          label: 'Average Risk Score',
          data: scores.length ? scores : [18.2, 14.5, 9.8, 6.4],
          borderColor: '#6366f1',
          borderWidth: 3,
          backgroundColor: gradient,
          fill: true,
          tension: 0.38,
          pointBackgroundColor: '#6366f1',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointRadius: 5,
          pointHoverRadius: 7
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            grid: { color: colors.gridColor },
            ticks: { color: colors.textColor, font: { family: "'Inter', sans-serif" } }
          },
          y: {
            min: 0,
            max: 25,
            grid: { color: colors.gridColor },
            ticks: { color: colors.textColor, font: { family: "'Inter', sans-serif" } }
          }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: colors.tooltipBg,
            titleColor: colors.tooltipText,
            bodyColor: colors.tooltipText,
            borderColor: colors.tooltipBorder,
            borderWidth: 1,
            padding: 12
          }
        }
      }
    });
  },

  // 3. Risks by Category Bar Chart
  renderCategories(canvasId, categoryData) {
    this.destroy(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const colors = this.getThemeColors();
    const labels = categoryData.map(c => c.name);
    const counts = categoryData.map(c => c.count);

    this.instances[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Number of Risks',
          data: counts,
          backgroundColor: [
            'rgba(99, 102, 241, 0.85)',
            'rgba(239, 68, 68, 0.85)',
            'rgba(16, 185, 129, 0.85)',
            'rgba(245, 158, 11, 0.85)',
            'rgba(139, 92, 246, 0.85)',
            'rgba(6, 182, 212, 0.85)',
            'rgba(236, 72, 153, 0.85)'
          ],
          borderRadius: 6,
          borderSkipped: false
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            grid: { display: false },
            ticks: {
              color: colors.textColor,
              font: { family: "'Inter', sans-serif", size: 11 },
              callback: function(val, index) {
                const label = this.getLabelForValue(index) || '';
                return label.length > 14 ? label.substr(0, 12) + '…' : label;
              }
            }
          },
          y: {
            beginAtZero: true,
            ticks: { stepSize: 1, color: colors.textColor },
            grid: { color: colors.gridColor }
          }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: colors.tooltipBg,
            titleColor: colors.tooltipText,
            bodyColor: colors.tooltipText,
            borderColor: colors.tooltipBorder,
            borderWidth: 1,
            padding: 12
          }
        }
      }
    });
  },

  // 4. Single Risk History Progression Line Chart
  renderSingleRiskHistory(canvasId, historyData) {
    this.destroy(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const colors = this.getThemeColors();
    const labels = historyData.map(h => h.recorded_date);
    const scores = historyData.map(h => h.risk_score);

    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 220);
    gradient.addColorStop(0, 'rgba(16, 185, 129, 0.4)');
    gradient.addColorStop(1, 'rgba(16, 185, 129, 0.0)');

    this.instances[canvasId] = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Risk Score Over Time',
          data: scores,
          borderColor: '#10b981',
          borderWidth: 3,
          backgroundColor: gradient,
          fill: true,
          tension: 0.3,
          pointBackgroundColor: '#10b981',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            grid: { color: colors.gridColor },
            ticks: { color: colors.textColor }
          },
          y: {
            min: 0,
            max: 25,
            grid: { color: colors.gridColor },
            ticks: { color: colors.textColor }
          }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: colors.tooltipBg,
            titleColor: colors.tooltipText,
            bodyColor: colors.tooltipText,
            borderColor: colors.tooltipBorder,
            borderWidth: 1,
            padding: 12
          }
        }
      }
    });
  }
};

window.refreshAllCharts = function() {
  // Triggers chart re-render with updated colors when theme toggles
  if (window.loadDashboardCharts) window.loadDashboardCharts();
  if (window.loadAnalyticsCharts) window.loadAnalyticsCharts();
};
