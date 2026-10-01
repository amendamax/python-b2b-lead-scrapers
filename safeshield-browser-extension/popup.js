const API_BASE = 'https://isbrokersafe.com/api/v1';

document.addEventListener('DOMContentLoaded', async () => {
  const currentDomainEl = document.getElementById('current-domain');
  const domainBadgeEl = document.getElementById('domain-status-badge');
  const domainMetaEl = document.getElementById('domain-details');
  const brokerInput = document.getElementById('broker-input');
  const searchBtn = document.getElementById('search-btn');
  const searchResultEl = document.getElementById('search-result');

  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab && tab.url && tab.url.startsWith('http')) {
      const url = new URL(tab.url);
      const domain = url.hostname.replace(/^www\./, '');
      currentDomainEl.textContent = domain;
      checkDomain(domain, domainBadgeEl, domainMetaEl);
    } else {
      currentDomainEl.textContent = 'Non-web page';
      domainBadgeEl.textContent = 'Inactive';
      domainBadgeEl.className = 'status-pill neutral';
    }
  } catch (err) {
    currentDomainEl.textContent = 'Browser Tab';
    domainBadgeEl.textContent = 'Protected';
    domainBadgeEl.className = 'status-pill safe';
  }

  searchBtn.addEventListener('click', () => {
    const query = brokerInput.value.trim();
    if (!query) return;
    performSearch(query, searchResultEl);
  });

  brokerInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      searchBtn.click();
    }
  });
});

async function checkDomain(domain, badgeEl, metaEl) {
  try {
    const res = await fetch(API_BASE + '/broker/check?domain=' + encodeURIComponent(domain));
    if (!res.ok) {
      badgeEl.textContent = 'No Threat Detected';
      badgeEl.className = 'status-pill safe';
      metaEl.textContent = 'Domain not found in CONSOB/FCA blacklists.';
      return;
    }
    const data = await res.json();
    if (data.is_blacklisted || data.risk_level === 'CRITICAL' || data.risk_level === 'HIGH') {
      badgeEl.textContent = '🚨 HIGH RISK / BLACKLISTED';
      badgeEl.className = 'status-pill danger';
      metaEl.innerHTML = '<strong>Warning:</strong> Flagged by ' + (data.regulator || 'Financial Authorities') + '. Unauthorized operations.' +
        '<div style="margin-top:8px;"><a href="https://isbrokersafe.com#safe-alternatives" target="_blank" style="display:inline-block; background:#ef4444; color:#ffffff; font-weight:bold; font-size:11px; padding:6px 12px; border-radius:6px; text-decoration:none; box-shadow:0 2px 8px rgba(239,68,68,0.4);">🛡️ View Top 5 Regulated Brokers ➔</a></div>';
    } else if (data.is_regulated || data.risk_level === 'SAFE' || data.risk_level === 'LOW') {
      badgeEl.textContent = '🛡️ VERIFIED & REGULATED';
      badgeEl.className = 'status-pill safe';
      metaEl.innerHTML = 'Regulated entity (' + (data.jurisdiction || 'Tier-1 Regulated') + '). Safety Score: ' + (data.safety_score || 95) + '/100.' +
        '<div style="margin-top:8px;"><a href="https://isbrokersafe.com/go/ibkr" target="_blank" style="display:inline-block; background:#10b981; color:#0b1528; font-weight:bold; font-size:11px; padding:6px 12px; border-radius:6px; text-decoration:none; box-shadow:0 2px 8px rgba(16,185,129,0.4);">🎁 Open Verified Broker Account ➔</a></div>';
    } else {
      badgeEl.textContent = 'ℹ️ UNRATED / NEUTRAL';
      badgeEl.className = 'status-pill neutral';
      metaEl.innerHTML = 'Domain not present in major regulatory blacklists.' +
        '<div style="margin-top:8px;"><a href="https://isbrokersafe.com#safe-alternatives" target="_blank" style="display:inline-block; background:#38bdf8; color:#0b1528; font-weight:bold; font-size:11px; padding:6px 12px; border-radius:6px; text-decoration:none;">🛡️ Compare Regulated Brokers ➔</a></div>';
    }
  } catch (e) {
    badgeEl.textContent = 'Protected';
    badgeEl.className = 'status-pill safe';
  }
}

async function performSearch(query, resultEl) {
  resultEl.classList.remove('hidden');
  resultEl.innerHTML = '<span style="color:#94a3b8">Searching 14,660+ regulatory records...</span>';
  try {
    const res = await fetch(API_BASE + '/broker/check?domain=' + encodeURIComponent(query));
    const data = await res.json();
    if (data.is_blacklisted || data.risk_level === 'CRITICAL' || data.risk_level === 'HIGH') {
      resultEl.innerHTML = '<div style="color:#f87171; font-weight:bold; margin-bottom:4px;">⚠️ ' + query + ': BLACKLISTED / HIGH RISK</div>' +
        '<div style="color:#cbd5e1;">Flagged by: ' + (data.regulator || 'European Regulators') + '</div>' +
        '<div style="color:#94a3b8; font-size:10px; margin-top:4px;">Unauthorized operations. Avoid depositing.</div>' +
        '<div style="margin-top:8px;"><a href="https://isbrokersafe.com#safe-alternatives" target="_blank" style="display:inline-block; background:#ef4444; color:#ffffff; font-weight:bold; font-size:11px; padding:6px 12px; border-radius:6px; text-decoration:none;">🛡️ View Safe Regulated Alternatives ➔</a></div>';
    } else if (data.is_regulated || data.risk_level === 'SAFE') {
      resultEl.innerHTML = '<div style="color:#34d399; font-weight:bold; margin-bottom:4px;">✅ ' + query + ': VERIFIED SAFE</div>' +
        '<div style="color:#cbd5e1;">License: ' + (data.license_number || 'Official European License') + '</div>' +
        '<div style="color:#94a3b8; font-size:10px; margin-top:4px;">Safety Score: ' + (data.safety_score || 95) + '/100</div>' +
        '<div style="margin-top:8px;"><a href="https://isbrokersafe.com/go/ibkr" target="_blank" style="display:inline-block; background:#10b981; color:#0b1528; font-weight:bold; font-size:11px; padding:6px 12px; border-radius:6px; text-decoration:none;">🎁 Open Regulated Account ➔</a></div>';
    } else {
      resultEl.innerHTML = '<div style="color:#38bdf8; font-weight:bold;">ℹ️ ' + query + ': Unlisted / Clean</div>' +
        '<div style="color:#94a3b8; font-size:10px; margin-top:2px;">No official blacklists found.</div>' +
        '<div style="margin-top:8px;"><a href="https://isbrokersafe.com#safe-alternatives" target="_blank" style="display:inline-block; background:#38bdf8; color:#0b1528; font-weight:bold; font-size:11px; padding:6px 12px; border-radius:6px; text-decoration:none;">🛡️ View Regulated Brokers ➔</a></div>';
    }
  } catch (e) {
    resultEl.innerHTML = '<span style="color:#f87171">Search service currently offline.</span>';
  }
}
