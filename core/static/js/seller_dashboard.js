document.addEventListener("DOMContentLoaded", function() {
  const adsViewsJSON = JSON.parse(document.getElementById('ads-views-data').textContent);
  window.adsViews = adsViewsJSON;

  console.log("adsViews loaded:", window.adsViews);

  const ctx = document.getElementById('adsViewChart');
  if (ctx) {
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'],
        datasets: [{
          label: 'Views',
          data: window.adsViews,
          backgroundColor: '#0d6efd'
        }]
      },
      options: {
        plugins: { legend: { display: false }},
        scales: { y: { beginAtZero: true } }
      }
    });
  }
});
