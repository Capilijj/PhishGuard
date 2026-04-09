// Admin dashboard chart initialization
Chart.defaults.color       = '#8ab88a';
Chart.defaults.borderColor = '#1e3a1e';
Chart.defaults.font.family = "'Share Tech Mono', monospace";
Chart.defaults.font.size   = 10;

var GREEN = '#00ff41';
var CYAN  = '#00e5ff';

var barCtx = document.getElementById('barChart').getContext('2d');
new Chart(barCtx, {
  type: 'bar',
  data: {
    labels: JSON.parse(document.getElementById('barChart').dataset.labels || '["MON","TUE","WED","THU","FRI","SAT","SUN"]'),
    datasets: [{
      label: 'SIMULATIONS',
      data:  JSON.parse(document.getElementById('barChart').dataset.data || '[0,0,0,0,0,0,0]'),
      backgroundColor: 'rgba(0,255,65,.2)',
      borderColor:     GREEN,
      borderWidth:     1,
      borderRadius:    2,
    }]
  },
  options: {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { color: '#1e3a1e' }, ticks: { color: '#5a8a5a' } },
      y: { grid: { color: '#1e3a1e' }, ticks: { color: '#5a8a5a' }, beginAtZero: true }
    }
  }
});

var lineCtx = document.getElementById('lineChart').getContext('2d');
new Chart(lineCtx, {
  type: 'line',
  data: {
    labels: JSON.parse(document.getElementById('lineChart').dataset.labels || '["WK1","WK2","WK3","WK4"]'),
    datasets: [{
      label: 'REGISTRATIONS',
      data:  JSON.parse(document.getElementById('lineChart').dataset.data || '[0,0,0,0]'),
      borderColor:     CYAN,
      backgroundColor: 'rgba(0,229,255,.08)',
      borderWidth:     2,
      pointBackgroundColor: CYAN,
      pointRadius:     4,
      tension:         .35,
      fill:            true,
    }]
  },
  options: {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { color: '#1e3a1e' }, ticks: { color: '#5a8a5a' } },
      y: { grid: { color: '#1e3a1e' }, ticks: { color: '#5a8a5a' }, beginAtZero: true }
    }
  }
});
