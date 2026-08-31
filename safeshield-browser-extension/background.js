// SafeShield Background Service Worker
const API_BASE = 'https://isbrokersafe.com/api/v1';

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url && tab.url.startsWith('http')) {
    checkUrlSafety(tab.url, tabId);
  }
});

chrome.tabs.onActivated.addListener(activeInfo => {
  chrome.tabs.get(activeInfo.tabId, tab => {
    if (tab && tab.url && tab.url.startsWith('http')) {
      checkUrlSafety(tab.url, tab.id);
    }
  });
});

async function checkUrlSafety(url, tabId) {
  try {
    const parsed = new URL(url);
    const domain = parsed.hostname.replace(/^www\./, '');
    if (domain.includes('google.') || domain.includes('bing.') || domain === 'localhost' || domain.includes('render.com')) {
      chrome.action.setBadgeText({ text: '', tabId: tabId });
      return;
    }
    const response = await fetch(API_BASE + '/broker/check?domain=' + encodeURIComponent(domain));
    if (!response.ok) return;
    const data = await response.json();
    if (data.is_blacklisted || data.risk_level === 'CRITICAL' || data.risk_level === 'HIGH') {
      chrome.action.setBadgeBackgroundColor({ color: '#EF4444', tabId: tabId });
      chrome.action.setBadgeText({ text: 'RISK', tabId: tabId });
    } else if (data.is_regulated || data.risk_level === 'SAFE' || data.risk_level === 'LOW') {
      chrome.action.setBadgeBackgroundColor({ color: '#10B981', tabId: tabId });
      chrome.action.setBadgeText({ text: 'SAFE', tabId: tabId });
    } else {
      chrome.action.setBadgeText({ text: '', tabId: tabId });
    }
  } catch (err) {
    console.error('SafeShield URL check error:', err);
  }
}
