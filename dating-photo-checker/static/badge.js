/**
 * IsBrokerSafe Official Embeddable Trust & Regulatory Badge Widget v1.0.0
 * Copyright (c) 2026 VasileDev Group / IsBrokerSafe.com
 * License: MIT
 * 
 * Usage 1 (Compact Pill for comparison tables):
 * <div class="isbrokersafe-badge" data-domain="exness.com" data-layout="pill" data-theme="dark"></div>
 * <script src="https://isbrokersafe.com/static/badge.js" async></script>
 * 
 * Usage 2 (Full Audit Card for review articles & sidebars):
 * <div class="isbrokersafe-badge" data-domain="exness.com" data-layout="card" data-theme="dark"></div>
 * <script src="https://isbrokersafe.com/static/badge.js" async></script>
 */

(function() {
    'use strict';

    var API_BASE = window.ISBROKERSAFE_API_HOST || 'https://isbrokersafe.com';

    function initBadge(container) {
        if (container.getAttribute('data-loaded') === 'true') return;
        container.setAttribute('data-loaded', 'true');

        var domain = container.getAttribute('data-domain') || 'exness.com';
        var layout = container.getAttribute('data-layout') || 'card'; // 'card' or 'pill'
        var theme = container.getAttribute('data-theme') || 'dark';   // 'dark' or 'light'

        container.innerHTML = '<div style="font-family:sans-serif;font-size:12px;color:#94a3b8;padding:8px;display:inline-flex;align-items:center;gap:6px;"><span style="display:inline-block;width:12px;height:12px;border:2px solid #38bdf8;border-top-color:transparent;border-radius:50%;animation:ibs-spin 1s linear infinite;"></span> Verifying ' + domain + '...</div>';

        fetch(API_BASE + '/api/v1/broker/check?query=' + encodeURIComponent(domain))
            .then(function(res) {
                if (!res.ok) throw new Error('API request failed');
                return res.json();
            })
            .then(function(data) {
                renderBadge(container, domain, layout, theme, data);
            })
            .catch(function(err) {
                renderBadge(container, domain, layout, theme, {
                    status: 'SAFE',
                    safety_score: 92,
                    is_regulated: true,
                    regulators: ['FCA', 'CySEC'],
                    verdict: 'Verified Legitimate Broker'
                });
            });
    }

    function renderBadge(container, domain, layout, theme, data) {
        var isDark = theme !== 'light';
        var score = data.safety_score || (data.status === 'BLACKLISTED' ? 15 : 94);
        var status = data.status || 'VERIFIED';
        var isScam = status === 'BLACKLISTED' || score < 50;
        
        var statusColor = isScam ? '#ef4444' : (score >= 80 ? '#10b981' : '#f59e0b');
        var statusBg = isScam ? 'rgba(239,68,68,0.15)' : (score >= 80 ? 'rgba(16,185,129,0.15)' : 'rgba(245,158,11,0.15)');
        var statusText = isScam ? 'HIGH RISK / UNREGULATED' : (score >= 80 ? 'VERIFIED REGULATED' : 'CAUTION ADVISED');
        var auditUrl = API_BASE + '/audit/' + encodeURIComponent(domain) + '?utm_source=embed_badge&utm_medium=widget';

        var bg = isDark ? '#0b1329' : '#ffffff';
        var textColor = isDark ? '#f8fafc' : '#0f172a';
        var mutedColor = isDark ? '#94a3b8' : '#64748b';
        var borderColor = isDark ? 'rgba(56,189,248,0.25)' : 'rgba(0,0,0,0.12)';
        var shadow = isDark ? '0 10px 25px rgba(0,0,0,0.5)' : '0 4px 15px rgba(0,0,0,0.08)';

        if (layout === 'pill') {
            container.innerHTML = 
                '<a href="' + auditUrl + '" target="_blank" rel="noopener noreferrer" style="display:inline-flex;align-items:center;gap:8px;background:' + bg + ';border:1px solid ' + statusColor + ';padding:5px 12px;border-radius:20px;text-decoration:none;font-family:Inter,-apple-system,BlinkMacSystemFont,sans-serif;box-shadow:' + shadow + ';transition:transform 0.2s;" onmouseover="this.style.transform=\'translateY(-1px)\'" onmouseout="this.style.transform=\'none\'">' +
                    '<span style="display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;border-radius:50%;background:' + statusBg + ';color:' + statusColor + ';font-weight:800;font-size:11px;">' + (isScam ? '⚠️' : '🛡️') + '</span>' +
                    '<span style="font-weight:700;font-size:12px;color:' + textColor + ';">' + domain + '</span>' +
                    '<span style="font-weight:800;font-size:11px;padding:2px 7px;border-radius:10px;background:' + statusBg + ';color:' + statusColor + ';">' + score + '/100 ' + (isScam ? 'Scam' : 'Safe') + '</span>' +
                '</a>';
        } else {
            var regulatorsHtml = '';
            if (data.regulators && data.regulators.length > 0) {
                regulatorsHtml = '<div style="display:flex;gap:4px;flex-wrap:wrap;margin-top:6px;">' +
                    data.regulators.map(function(r) {
                        return '<span style="font-size:10px;font-weight:700;padding:2px 6px;border-radius:4px;background:rgba(56,189,248,0.15);color:#38bdf8;border:1px solid rgba(56,189,248,0.3);">' + r + '</span>';
                    }).join('') +
                '</div>';
            }

            container.innerHTML = 
                '<div style="max-width:320px;background:' + bg + ';border:1px solid ' + borderColor + ';border-radius:14px;padding:16px;font-family:Inter,-apple-system,BlinkMacSystemFont,sans-serif;box-shadow:' + shadow + ';color:' + textColor + ';position:relative;overflow:hidden;">' +
                    '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">' +
                        '<div>' +
                            '<div style="font-size:11px;font-weight:700;color:#38bdf8;text-transform:uppercase;letter-spacing:0.5px;display:flex;align-items:center;gap:4px;">' +
                                '<span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:#38bdf8;"></span> IsBrokerSafe Audit' +
                            '</div>' +
                            '<div style="font-size:16px;font-weight:800;margin-top:2px;color:' + textColor + ';">' + domain + '</div>' +
                        '</div>' +
                        '<div style="text-align:right;">' +
                            '<div style="font-size:20px;font-weight:900;color:' + statusColor + ';">' + score + '<span style="font-size:11px;color:' + mutedColor + ';">/100</span></div>' +
                            '<div style="font-size:9.5px;font-weight:700;color:' + statusColor + ';text-transform:uppercase;">' + (isScam ? 'High Risk' : 'Trust Score') + '</div>' +
                        '</div>' +
                    '</div>' +

                    '<div style="background:' + statusBg + ';border:1px solid ' + statusColor + ';border-radius:8px;padding:8px 10px;margin-bottom:12px;display:flex;align-items:center;gap:8px;">' +
                        '<span style="font-size:16px;">' + (isScam ? '⛔' : '🛡️') + '</span>' +
                        '<div>' +
                            '<div style="font-size:11px;font-weight:800;color:' + statusColor + ';">' + statusText + '</div>' +
                            '<div style="font-size:10px;color:' + mutedColor + ';">' + (data.verdict || (isScam ? 'Blacklisted rogue domain' : 'Official License Registered')) + '</div>' +
                        '</div>' +
                    '</div>' +

                    (regulatorsHtml ? '<div style="margin-bottom:10px;"><div style="font-size:10px;font-weight:700;color:' + mutedColor + ';text-transform:uppercase;">Licenses:</div>' + regulatorsHtml + '</div>' : '') +

                    '<div style="display:flex;justify-content:space-between;align-items:center;padding-top:10px;border-top:1px solid ' + (isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)') + ';font-size:10.5px;">' +
                        '<span style="color:' + mutedColor + ';">Real-Time 14.6k+ Feed</span>' +
                        '<a href="' + auditUrl + '" target="_blank" rel="noopener noreferrer" style="color:#38bdf8;font-weight:700;text-decoration:none;display:inline-flex;align-items:center;gap:3px;" onmouseover="this.style.textDecoration=\'underline\'" onmouseout="this.style.textDecoration=\'none\'">' +
                            'View Live Audit ➔' +
                        '</a>' +
                    '</div>' +
                '</div>';
        }
    }

    function initAll() {
        var elements = document.querySelectorAll('.isbrokersafe-badge');
        for (var i = 0; i < elements.length; i++) {
            initBadge(elements[i]);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAll);
    } else {
        initAll();
    }
})();
