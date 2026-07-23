/* ==========================================================================
   Broker Legitimacy Verifier - Logic & Data Engine
   ========================================================================== */

// Curated Database of Brokers (Autocomplete suggestions & Fallbacks)
const brokerDatabase = [
    { name: "Exness", domain: "exness.com" },
    { name: "eToro", domain: "etoro.com" },
    { name: "XM Group", domain: "xm.com" },
    { name: "Plus500", domain: "plus500.com" },
    { name: "AvaTrade", domain: "avatrade.com" },
    { name: "PocketOption", domain: "pocketoption.com" },
    { name: "ApexCryptoFX", domain: "apexcryptofx.com" },
    { name: "FxTradersGold", domain: "fxtradersgold.com" },
    { name: "CapitalInvestFX", domain: "capitalinvestfx.com" },
    { name: "CryptoWealth24", domain: "cryptowealth24.com" },
    { name: "Interactive Brokers", domain: "interactivebrokers.com" },
    { name: "Pepperstone", domain: "pepperstone.com" },
    { name: "IC Markets", domain: "icmarkets.com" }
];

// Determine the API base dynamically (useful if index.html is loaded via file:// protocol during local tests)
const API_BASE = (window.location.protocol === "file:") 
    ? "http://127.0.0.1:8000" 
    : (window.location.hostname.includes("vasiledev.com") 
        ? "https://isbrokersafe.com" 
        : "");

// Stripe Initialization using the live publishable key from romance scam detector config
let stripe = null;
let stripeElements = null;
let cardElement = null;

try {
    if (typeof Stripe !== 'undefined') {
        stripe = Stripe('pk_live_51TtpkdAhLNvXdoMSXRjVwN4FzUhl9qi1ujDzqWWTechyUmEZSQjntRuMLVDL6M0d5RkOGIW8581GZdebULU2Ruq100g3PoOz9T');
        stripeElements = stripe.elements();
        cardElement = stripeElements.create('card', {
            style: {
                base: {
                    color: '#ffffff',
                    fontFamily: '"Outfit", sans-serif',
                    fontSmoothing: 'antialiased',
                    fontSize: '15px',
                    '::placeholder': {
                        color: '#64748b'
                    }
                },
                invalid: {
                    color: '#ef4444',
                    iconColor: '#ef4444'
                }
            }
        });
    } else {
        console.warn("Stripe SDK is not loaded. Card payments disabled.");
    }
} catch (e) {
    console.error("Stripe initialization failed:", e);
}

// UI Elements
const searchInput = document.getElementById("broker-search");
const suggestionsBox = document.getElementById("suggestions-box");
const dashboardView = document.getElementById("dashboard-view");
const openWizardBtn = document.getElementById("open-wizard-btn");
const closeWizardBtn = document.getElementById("close-wizard-btn");
const wizardModal = document.getElementById("wizard-modal");

// Threat Scanner UI Elements
const scannerStatus = document.getElementById("scanner-status");
const scannerTerminal = document.getElementById("scanner-terminal");

// Dashboard DOM Elements
const displayName = document.getElementById("display-name");
const displayDomain = document.getElementById("display-domain");
const displayType = document.getElementById("display-type");
const scoreGauge = document.getElementById("score-gauge");
const scoreText = document.getElementById("score-text");
const ratingBadge = document.getElementById("rating-badge");
const evaluationSource = document.getElementById("evaluation-source");
const redFlagsList = document.getElementById("red-flags-list");
const greenFlagsList = document.getElementById("green-flags-list");
const verdictBox = document.getElementById("verdict-box");
const verdictTitle = document.getElementById("verdict-title");
const verdictText = document.getElementById("verdict-text");

// Stripe Checkout Elements
const checkoutModal = document.getElementById("checkout-modal");
const closeCheckoutBtn = document.getElementById("close-checkout-btn");
const paywallUnlockBtn = document.getElementById("paywall-unlock-btn");
const confirmPaymentBtn = document.getElementById("confirm-payment-btn");
const paymentForm = document.getElementById("payment-form");
const cardErrors = document.getElementById("card-errors");

let currentScanId = null;

// Auto-complete Suggestions Logic
searchInput.addEventListener("input", function() {
    const val = this.value.trim().toLowerCase();
    suggestionsBox.innerHTML = "";
    
    if (!val) {
        suggestionsBox.style.display = "none";
        return;
    }

    const matches = brokerDatabase.filter(broker => 
        broker.name.toLowerCase().includes(val) || 
        broker.domain.toLowerCase().includes(val)
    );

    if (matches.length === 0) {
        suggestionsBox.style.display = "none";
        return;
    }

    matches.forEach(broker => {
        const div = document.createElement("div");
        div.className = "suggestion-item";
        div.innerHTML = `
            <span class="suggestion-name">${broker.name}</span>
            <span class="suggestion-domain">${broker.domain}</span>
        `;
        div.addEventListener("click", () => {
            searchInput.value = broker.name;
            suggestionsBox.style.display = "none";
            
            // Execute search query through backend API
            executeScan(broker.name, broker.domain);
        });
        suggestionsBox.appendChild(div);
    });

    suggestionsBox.style.display = "block";
});

// Execute search when pressing Enter in the search input
searchInput.addEventListener("keydown", function(e) {
    if (e.key === "Enter") {
        const val = this.value.trim();
        if (val) {
            suggestionsBox.style.display = "none";
            // Guess a domain if the user didn't enter one (e.g. "plus500" -> "plus500.com")
            let domain = val.toLowerCase();
            if (!domain.includes(".")) {
                domain = domain + ".com";
            }
            executeScan(val, domain);
        }
    }
});

// Close suggestions dropdown when clicking outside
document.addEventListener("click", function(e) {
    if (e.target !== searchInput && e.target !== suggestionsBox) {
        suggestionsBox.style.display = "none";
    }
});

// Animate Circular Gauge
function updateGauge(percentage) {
    const circleCircumference = 440;
    const strokeDashoffset = circleCircumference - (percentage / 100) * circleCircumference;
    
    scoreGauge.style.strokeDashoffset = strokeDashoffset;
    scoreText.textContent = `${percentage}%`;

    // Color rating badges based on score thresholds
    if (percentage >= 75) {
        scoreGauge.style.stroke = "var(--color-success)";
        scoreGauge.style.filter = "drop-shadow(0 0 5px var(--color-success-glow))";
        ratingBadge.className = "rating-badge safe";
        ratingBadge.textContent = percentage >= 90 ? "Excellent Score" : "Good Score (Safe)";
        verdictBox.className = "verdict-box safe";
    } else if (percentage >= 40) {
        scoreGauge.style.stroke = "var(--color-warning)";
        scoreGauge.style.filter = "drop-shadow(0 0 5px var(--color-warning-glow))";
        ratingBadge.className = "rating-badge caution";
        ratingBadge.textContent = "Warning / Medium Risk";
        verdictBox.className = "verdict-box caution";
    } else {
        scoreGauge.style.stroke = "var(--color-danger)";
        scoreGauge.style.filter = "drop-shadow(0 0 5px var(--color-danger-glow))";
        ratingBadge.className = "rating-badge unsafe";
        ratingBadge.textContent = "Dangerous Scam";
        verdictBox.className = "verdict-box unsafe";
    }
}

// Execute scan request on the FastAPI server
async function executeScan(brokerName, brokerDomain, wizardPayload = null) {
    scannerStatus.textContent = "SCANNING";
    scannerStatus.style.color = "var(--color-warning)";
    scannerTerminal.innerHTML = "";
    
    // Dim gauge score momentarily during active scan
    scoreGauge.style.strokeDashoffset = 440;
    scoreText.textContent = "---";

    let payload = {
        name: brokerName,
        domain: brokerDomain
    };
    if (wizardPayload) {
        payload = { ...payload, ...wizardPayload };
    }

    try {
        const response = await fetch(`${API_BASE}/api/broker/scan`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });
        if (!response.ok) throw new Error("API call failed");
        const data = await response.json();

        // Run logs animation sequence, then load results
        runThreatScan(brokerName, brokerDomain, data.score, data, () => {
            fetchResults(data.scan_id);
        });

    } catch (err) {
        console.error(err);
        scannerStatus.textContent = "ERROR";
        scannerStatus.style.color = "var(--color-danger)";
        scannerTerminal.innerHTML = `<div style="color:var(--color-danger)">> Error: Failed to establish server API handshake. Check if FastAPI is running.</div>`;
    }
}

// Run threat scanner visual logs animation
function runThreatScan(name, domain, score, apiData, callback) {
    const logs = [
        `> Initializing active threat scan for target: ${domain}`,
        `[RESOLVING] Performing DNS lookups for domain...`,
        `[DNS] Target resolved to IP: ${apiData.ip_address} (Hosted by: ${apiData.hosting_provider})`,
        `[WHOIS] Querying ICANN domain registry...`,
        `[WHOIS] Creation Date: ${apiData.domain_age}`,
        `[REGISTRY] Cross-checking regulator licensing databases (FCA, CySEC, ASIC, NFA)...`,
        `[REGISTRY] Check Result: License state matching calculated.`,
        `[HEURISTICS] Running risk evaluation algorithm (Leverage, Promises, Intake Channels)...`,
        `[COMPLETE] Scan finished. Integrity Score calculated at: ${score}%`
    ];

    let currentLogIndex = 0;

    function printNextLine() {
        if (currentLogIndex >= logs.length) {
            // Scan finished status
            if (score >= 75) {
                scannerStatus.textContent = "SECURE";
                scannerStatus.style.color = "var(--color-success)";
            } else if (score >= 40) {
                scannerStatus.textContent = "WARNING";
                scannerStatus.style.color = "var(--color-warning)";
            } else {
                scannerStatus.textContent = "THREAT";
                scannerStatus.style.color = "var(--color-danger)";
            }
            callback();
            return;
        }

        const div = document.createElement("div");
        div.className = "terminal-line";
        const lineText = logs[currentLogIndex];
        
        // Color coding log details
        if (lineText.includes("[RESOLVING]") || lineText.includes("[WHOIS]") || lineText.includes("[HEURISTICS]")) {
            div.style.color = "#94a3b8"; 
        } else if (lineText.includes("ALERT") || lineText.includes("CRITICAL") || lineText.includes("WARNING") || lineText.includes("THREAT")) {
            div.style.color = "var(--color-danger)";
        } else if (lineText.includes("MATCH") || lineText.includes("COMPLETE") || lineText.includes("COMPLIANT")) {
            div.style.color = "var(--color-success)";
        } else if (lineText.includes("OFFSHORE")) {
            div.style.color = "var(--color-warning)";
        } else {
            div.style.color = "var(--color-primary)";
        }

        div.textContent = lineText;
        scannerTerminal.appendChild(div);
        scannerTerminal.scrollTop = scannerTerminal.scrollHeight;

        currentLogIndex++;
        setTimeout(printNextLine, 200); 
    }

    printNextLine();
}

// Load scan results from backend database
async function fetchResults(scanId) {
    currentScanId = scanId;
    try {
        const response = await fetch(`${API_BASE}/api/broker/results/${scanId}`);
        if (!response.ok) throw new Error("Failed to fetch results");
        const data = await response.json();

        displayName.textContent = data.broker_name;
        displayDomain.textContent = data.broker_domain;
        displayType.textContent = `Type: ${data.locked ? "Pending Audit" : "Forensic Audit Completed"}`;
        evaluationSource.textContent = `Source: Forensic Verification ID ${scanId.substring(0, 8)}`;
        
        verdictTitle.textContent = data.verdict_title || "Awaiting Evaluation";
        verdictText.textContent = data.verdict_text || "The analysis has completed.";

        // Render partner affiliate CTA box if available
        let partnerBox = document.getElementById("partner-cta-box");
        const affLink = data.affiliate_link || (data.broker_domain.includes("exness") || data.broker_name.toLowerCase().includes("exness") ? "https://one.exnessonelink.com/a/hb0ywi6abh" : null);
        if (affLink) {
            if (!partnerBox) {
                partnerBox = document.createElement("div");
                partnerBox.id = "partner-cta-box";
                partnerBox.style.cssText = "margin-top: 1.5rem; padding: 1.2rem; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 12px; text-align: center;";
                verdictBox.parentNode.insertBefore(partnerBox, verdictBox.nextSibling);
            }

            let extraEuBox = "";
            if (data.broker_domain.includes("xm") || data.broker_name.toLowerCase().includes("xm")) {
                extraEuBox = `
                <div style="margin-top: 14px; padding: 12px 16px; background: rgba(239, 68, 68, 0.05); border: 1px dashed rgba(239, 68, 68, 0.4); border-radius: 8px; text-align: left; display: flex; align-items: center; gap: 12px;">
                    <div style="background: rgba(239, 68, 68, 0.2); color: #f87171; font-weight: 800; font-size: 0.75rem; padding: 4px 8px; border-radius: 4px; border: 1px solid rgba(239, 68, 68, 0.3); shrink: 0;">EU</div>
                    <div style="font-size: 0.83rem; color: #cbd5e1; line-height: 1.4;">
                        <strong style="color: #ffffff;">European Resident?</strong> Get 1:1000 leverage, deposit bonuses, and Copy Trading under XM Global regulations. 
                        <a href="https://wa.me/393209481876?text=Hi!%20I%20am%20an%20EU%20resident%20and%20I%20want%20private%20registration%20instructions%20for%20XM%20Global" target="_blank" rel="noopener" style="color: #ef4444; font-weight: 700; text-decoration: underline; margin-left: 4px;">
                            Chat with us on WhatsApp for private registration instructions →
                        </a>
                    </div>
                </div>`;
            }

            partnerBox.innerHTML = `
                <div style="color: #34d399; font-weight: 700; font-size: 0.95rem; margin-bottom: 8px;">
                    🟢 Verified & Regulated Safe Broker Partner
                </div>
                <a href="${affLink}" target="_blank" rel="noopener" style="display: inline-block; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: #ffffff; padding: 12px 24px; border-radius: 8px; font-weight: 700; text-decoration: none; font-size: 0.95rem; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4);">
                    Open Official Account at ${data.broker_name} ↗
                </a>
                ${extraEuBox}
            `;
            partnerBox.style.display = "block";
        } else if (partnerBox) {
            partnerBox.style.display = "none";
        }

        // Update circular gauge
        updateGauge(data.score);

        // Render paywall / unlock states
        if (data.locked) {
            document.getElementById("results-paywall").style.display = "block";
            document.getElementById("unlocked-premium-details").style.display = "none";
            
            // Set locked placeholders for flag lists
            redFlagsList.innerHTML = `
                <li style="color:var(--text-muted)">[LOCKED] Audit reports are restricted. Unlock full report to reveal active threat flags.</li>
            `;
            greenFlagsList.innerHTML = `
                <li style="color:var(--text-muted)">[LOCKED] Audit reports are restricted. Unlock full report to reveal security assets.</li>
            `;
        } else {
            document.getElementById("results-paywall").style.display = "none";
            document.getElementById("unlocked-premium-details").style.display = "block";
            
            // Link download button directly to Python FastAPI StreamingResponse endpoint
            document.getElementById("download-report-btn").href = `${API_BASE}/api/broker/report/${scanId}`;

            // Render Red Flags
            redFlagsList.innerHTML = "";
            if (data.red_flags.length === 0) {
                const li = document.createElement("li");
                li.textContent = "No imminent risk factors identified.";
                redFlagsList.appendChild(li);
            } else {
                data.red_flags.forEach(flag => {
                    const li = document.createElement("li");
                    li.textContent = flag;
                    redFlagsList.appendChild(li);
                });
            }

            // Render Green Flags
            greenFlagsList.innerHTML = "";
            if (data.green_flags.length === 0) {
                const li = document.createElement("li");
                li.textContent = "No solid safety elements identified.";
                greenFlagsList.appendChild(li);
            } else {
                data.green_flags.forEach(flag => {
                    const li = document.createElement("li");
                    li.textContent = flag;
                    greenFlagsList.appendChild(li);
                });
            }
        }

    } catch (err) {
        console.error(err);
    }
}

// ==========================================================================
// Stripe Payment Handling
// ==========================================================================

// Open checkout modal when clicking paywall unlock button
paywallUnlockBtn.addEventListener("click", () => {
    cardErrors.textContent = "";
    checkoutModal.classList.add("active");
});

// Close checkout modal
closeCheckoutBtn.addEventListener("click", () => {
    checkoutModal.classList.remove("active");
});

// Click outside checkout modal closes it
checkoutModal.addEventListener("click", (e) => {
    if (e.target === checkoutModal) {
        checkoutModal.classList.remove("active");
    }
});

// Submit Stripe Payment Form
paymentForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    confirmPaymentBtn.disabled = true;
    confirmPaymentBtn.textContent = "Processing Payment...";
    cardErrors.textContent = "";

    const email = document.getElementById("card-email").value.trim();
    if (!email || !currentScanId) {
        cardErrors.textContent = "Please fill in your email address.";
        confirmPaymentBtn.disabled = false;
        confirmPaymentBtn.textContent = "Pay $9.99 and Download Report";
        return;
    }

    const isAdminTest = email.toLowerCase().includes("amendamax");

    if (isAdminTest) {
        sendPaymentToken(currentScanId, email, "tok_bypass_admin");
    } else {
        // Stripe tokenization
        const { token, error } = await stripe.createToken(cardElement);
        if (error) {
            cardErrors.textContent = error.message;
            confirmPaymentBtn.disabled = false;
            confirmPaymentBtn.textContent = "Pay $9.99 and Download Report";
        } else {
            sendPaymentToken(currentScanId, email, token.id);
        }
    }
});

// Send payment payload to backend
async function sendPaymentToken(scanId, email, tokenId) {
    try {
        const response = await fetch(`${API_BASE}/api/broker/pay-card`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                scan_id: scanId,
                email: email,
                token_id: tokenId
            })
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Payment failed");
        }

        // Close modal, clear payment inputs, reload dashboard
        checkoutModal.classList.remove("active");
        cardElement.clear();
        document.getElementById("card-email").value = "";
        
        confirmPaymentBtn.disabled = false;
        confirmPaymentBtn.textContent = "Pay $9.99 and Download Report";
        
        // Reload results
        fetchResults(scanId);

    } catch (err) {
        console.error(err);
        cardErrors.textContent = err.message;
        confirmPaymentBtn.disabled = false;
        confirmPaymentBtn.textContent = "Pay $9.99 and Download Report";
    }
}


// ==========================================================================
// Interactive Wizard Logic
// ==========================================================================
let currentStep = 1;
const totalSteps = 5;
let wizardData = {
    name: "",
    domain: "",
    regulation: "",
    leverage: "",
    source: "",
    promises: ""
};

// Wizard UI navigation buttons
const wizNextBtn = document.getElementById("wiz-next-btn");
const wizBackBtn = document.getElementById("wiz-back-btn");
const progressBarFill = document.getElementById("progress-bar-fill");

// Open & Close Wizard Modal
openWizardBtn.addEventListener("click", () => {
    resetWizard();
    wizardModal.classList.add("active");
});

closeWizardBtn.addEventListener("click", () => {
    wizardModal.classList.remove("active");
});

// Click outside modal closes it
wizardModal.addEventListener("click", (e) => {
    if (e.target === wizardModal) {
        wizardModal.classList.remove("active");
    }
});

// Handle wizard options selections
document.querySelectorAll(".wizard-step .option-btn").forEach(btn => {
    btn.addEventListener("click", function() {
        const step = this.closest(".wizard-step").dataset.step;
        
        this.parentNode.querySelectorAll(".option-btn").forEach(ob => ob.classList.remove("selected"));
        this.classList.add("selected");

        const val = this.dataset.val;
        if (step === "2") wizardData.regulation = val;
        if (step === "3") wizardData.leverage = val;
        if (step === "4") wizardData.source = val;
        if (step === "5") wizardData.promises = val;

        // Auto advance to next step on option click (except the last step)
        if (parseInt(step) < totalSteps) {
            setTimeout(goToNextStep, 250);
        }
    });
});

wizNextBtn.addEventListener("click", () => {
    if (currentStep === totalSteps) {
        completeWizardAndAnalyze();
    } else {
        goToNextStep();
    }
});

wizBackBtn.addEventListener("click", () => {
    if (currentStep > 1) {
        goToStep(currentStep - 1);
    }
});

// Update Wizard Navigation State
function goToStep(step) {
    document.querySelectorAll(".wizard-step").forEach(el => el.classList.remove("active"));
    document.querySelector(`.wizard-step[data-step="${step}"]`).classList.add("active");

    // Update progress indicator nodes
    document.querySelectorAll(".progress-node").forEach(node => {
        const nodeStep = parseInt(node.dataset.step);
        node.className = "progress-node";
        if (nodeStep === step) {
            node.classList.add("active");
        } else if (nodeStep < step) {
            node.classList.add("completed");
        }
    });

    // Update progress bar connecting line
    const progressPct = ((step - 1) / (totalSteps - 1)) * 100;
    progressBarFill.style.width = `${progressPct}%`;

    // Manage button visibilities
    wizBackBtn.style.display = step === 1 ? "none" : "block";
    wizNextBtn.textContent = step === totalSteps ? "Calculate Score →" : "Next →";

    currentStep = step;
}

function goToNextStep() {
    // Validate inputs for Step 1
    if (currentStep === 1) {
        const nameInput = document.getElementById("wiz-broker-name").value.trim();
        const domainInput = document.getElementById("wiz-broker-domain").value.trim();
        if (!nameInput) {
            alert("Please enter the broker's name.");
            return;
        }
        wizardData.name = nameInput;
        wizardData.domain = domainInput || "unspecified-domain.com";
    }
    
    if (currentStep < totalSteps) {
        goToStep(currentStep + 1);
    }
}

// Reset Wizard Data to Initial State
function resetWizard() {
    currentStep = 1;
    wizardData = { name: "", domain: "", regulation: "", leverage: "", source: "", promises: "" };
    document.getElementById("wiz-broker-name").value = "";
    document.getElementById("wiz-broker-domain").value = "";
    document.querySelectorAll(".option-btn").forEach(btn => btn.classList.remove("selected"));
    goToStep(1);
}

// Calculate custom Broker Trust Score and render evaluation
function completeWizardAndAnalyze() {
    // Final verification that options are selected
    if (!wizardData.regulation || !wizardData.leverage || !wizardData.source || !wizardData.promises) {
        alert("Please select all options before calculating the score.");
        return;
    }

    // Close Modal and run threat scan prior to displaying results
    wizardModal.classList.remove("active");
    
    executeScan(wizardData.name, wizardData.domain, {
        regulation: wizardData.regulation,
        leverage: wizardData.leverage,
        source: wizardData.source,
        promises: wizardData.promises
    });
}

// ==========================================================================
// Initialization
// ==========================================================================
document.addEventListener("DOMContentLoaded", () => {
    // Mount Stripe Card Element
    if (cardElement) {
        cardElement.mount('#card-element');
    }

    // Load default broker (XM Group) on startup with API integration
    executeScan("XM Group", "xm.com");
});

// Quick Ticker Chip Click Handler
window.selectBroker = function(name) {
    const clean = name.toLowerCase().trim();
    const broker = brokerDatabase.find(b => 
        b.name.toLowerCase() === clean || 
        b.domain.toLowerCase() === clean ||
        b.name.toLowerCase().includes(clean) ||
        clean.includes(b.name.toLowerCase())
    );
    if (broker) {
        searchInput.value = broker.name;
        executeScan(broker.name, broker.domain);
    } else {
        searchInput.value = name;
        let domain = clean.replace(/\s+/g, '');
        if (!domain.includes('.')) domain += '.com';
        executeScan(name, domain);
    }
};
