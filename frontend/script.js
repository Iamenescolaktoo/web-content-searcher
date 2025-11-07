const newsList = document.getElementById('newsList');
const presetSelect = document.getElementById('presetSelect');
const searchInput = document.getElementById('searchInput');
const categoryFilter = document.getElementById('categoryFilter');
const sentimentFilter = document.getElementById('sentimentFilter');
const refreshBtn = document.getElementById('refreshBtn');

let currentNews = [];

function riskColor(v) {
  if (v > 7) return 'bg-red-500';
  if (v > 4) return 'bg-yellow-500';
  return 'bg-green-500';
}

function filterClientKeywords(list) {
  const bad = new Set(["https","http","trthaberstatic","resimler","video","foto","haber","son","dakika"]);
  const re = /^[A-Za-zÇĞİÖŞÜçğıöşü]{3,}$/;
  return (list || []).filter(k => re.test(k) && !bad.has(k.toLowerCase()));
}

function renderNews(list) {
  newsList.innerHTML = '';
  if (!list.length) {
    newsList.innerHTML = '<p class="col-span-full text-center text-gray-500 text-lg">No news found.</p>';
    return;
  }
  list.forEach(n => {
    const kwsArr = filterClientKeywords(n.keywords);
    const kws = kwsArr.map(k => `<span class="px-2 py-0.5 text-xs text-gray-700 bg-gray-200 rounded">${k}</span>`).join('');
    const cat = n.category ? `<span class="px-2 py-0.5 text-xs font-medium text-blue-800 bg-blue-100 rounded">${n.category}</span>` : '';
    const host = n.source ? new URL(n.source).hostname : '';

    newsList.innerHTML += `
      <div class="bg-white border border-gray-200 rounded p-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs text-gray-500">${host} - ${new Date(n.datetime).toLocaleString()}</span>
          <span class="px-2 py-0.5 text-xs font-medium text-white rounded ${riskColor(n.risk_point)}">${n.risk_point ?? 'N/A'}</span>
        </div>
        <a class="text-lg font-semibold text-gray-900 hover:underline" href="${n.source}" target="_blank" rel="noreferrer">${n.title}</a>
        <div class="flex gap-2 flex-wrap mt-2">${cat}</div>
        ${kwsArr.length ? `
        <div class="mt-2">
          <h4 class="text-sm text-gray-700">Keywords</h4>
          <div class="flex flex-wrap gap-1 mt-1">${kws}</div>
        </div>` : ''}
      </div>
    `;
  });
}

function applyFilters() {
  const q = (searchInput.value || '').toLowerCase();
  const cat = categoryFilter.value;
  const sent = sentimentFilter.value;

  const filtered = currentNews.filter(n => {
    const kw = filterClientKeywords(n.keywords).join(' ').toLowerCase();
    const inText = (n.title || '').toLowerCase().includes(q) || kw.includes(q);
    const catOk = cat ? n.category === cat : true;
    const sentOk = sent ? n.sentiment === sent : true;
    return inText && catOk && sentOk;
  });

  renderNews(filtered);
}

async function fetchAndRender() {
  newsList.innerHTML = '<p class="col-span-full text-center text-gray-500 text-lg">Loading...</p>';
  try {
    const preset = presetSelect.value;
    const r = await fetch(`/api/news?preset=${encodeURIComponent(preset)}&max_news=8&fast=1`);
    const j = await r.json();
    currentNews = j.data || [];
    applyFilters();
  } catch (e) {
    newsList.innerHTML = `<p class="col-span-full text-center text-red-500 text-lg">Error: ${e.message}</p>`;
  }
}

searchInput.addEventListener('input', applyFilters);
categoryFilter.addEventListener('change', applyFilters);
sentimentFilter.addEventListener('change', applyFilters);
refreshBtn.addEventListener('click', fetchAndRender);

document.addEventListener('DOMContentLoaded', fetchAndRender);

const notifyIcon = document.getElementById('notifyIcon');
const notifyDot = document.getElementById('notifyDot');
let hasRedZone = false;

// check for high-risk stories and update icon color
function checkRedZones(newsList) {
  hasRedZone = newsList.some(n => n.risk_point >= 8);
  notifyDot.style.backgroundColor = hasRedZone ? 'red' : 'transparent';
  document.querySelector('#notifyIcon .material-symbols-outlined').textContent =
    hasRedZone ? 'notifications_active' : 'notifications';
}

// wrap the renderNews function so it calls checkRedZones automatically
const originalRender = renderNews;
renderNews = function (list) {
  originalRender(list);
  checkRedZones(list);
};

notifyIcon.addEventListener('click', async () => {
  const email = prompt('Enter your email to receive alert reports:');
  if (!email) return;

  try {
    const res = await fetch('/api/subscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    const j = await res.json();
    alert(j.message || 'Email saved successfully!');
  } catch (err) {
    alert('Error saving email: ' + err.message);
  }
});
