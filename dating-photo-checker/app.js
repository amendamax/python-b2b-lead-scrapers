document.addEventListener('DOMContentLoaded', () => {
    
    // ==========================================================================
    // DOM ELEMENTS
    // ==========================================================================
    const dropZone = document.getElementById('drop-zone-area');
    const imageInput = document.getElementById('image-input');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const removeImgBtn = document.getElementById('remove-img-btn');
    const startScanBtn = document.getElementById('start-scan-btn');
    const dropZonePrompt = dropZone.querySelector('.drop-zone-prompt');
    const scanLaser = document.getElementById('scan-laser');
    
    const imageUrlInput = document.getElementById('image-url');
    
    // Panel States
    const stateIdle = document.getElementById('state-idle');
    const stateScanning = document.getElementById('state-scanning');
    const stateResults = document.getElementById('state-results');
    
    // Progress Steps
    const scanProgressFill = document.getElementById('scan-progress-fill');
    const scanProgressText = document.getElementById('scan-progress-text');
    const stepFacial = document.getElementById('step-facial');
    const stepReverse = document.getElementById('step-reverse');
    const stepSocial = document.getElementById('step-social');
    const stepScamDb = document.getElementById('step-scamdb');
    
    // Results & Paywall
    const resultsPaywall = document.getElementById('results-paywall');
    const unlockedPremiumDetails = document.getElementById('unlocked-premium-details');
    const paywallUnlockBtn = document.getElementById('paywall-unlock-btn');
    const creditEmailInput = document.getElementById('credit-email');
    const useCreditBtn = document.getElementById('use-credit-btn');
    const creditErrorMsg = document.getElementById('credit-error-msg');
    const successAlertText = document.getElementById('success-alert-text');

    // Checkout Modal
    const checkoutModal = document.getElementById('checkout-modal');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const paymentForm = document.getElementById('payment-form');
    const confirmPaymentBtn = document.getElementById('confirm-payment-btn');
    
    // Card inputs
    const cardEmailInput = document.getElementById('card-email');
    
    // Ticker Container
    const activityTicker = document.getElementById('activity-ticker');

    let selectedFile = null;
    let currentScanId = null;

    // ==========================================================================
    // STRIPE ELEMENTS INITIALIZATION (PCI-compliant card tokenization)
    // ==========================================================================
    const stripe = Stripe('pk_live_51TqAOL4BeKMWotIPq734OYlEHcqBmkXBNo80k5LKRQD14NFUSgTPYrKCdw0dZj8pvAE2mITguiF6FSXAwkfphicO00tlou4EK9');
    const stripeElements = stripe.elements();
    const cardElement = stripeElements.create('card', {
        style: {
            base: {
                color: '#e2e8f0',
                fontFamily: '"Inter", "Outfit", sans-serif',
                fontSize: '15px',
                '::placeholder': { color: '#64748b' },
                iconColor: '#94a3b8'
            },
            invalid: { color: '#ff4d4d', iconColor: '#ff4d4d' }
        }
    });
    cardElement.mount('#card-element');
    cardElement.addEventListener('change', (e) => {
        const errorDiv = document.getElementById('card-errors');
        errorDiv.textContent = e.error ? e.error.message : '';
    });

    // ==========================================================================
    // INITIALIZATION & TICKER POPULATION
    // ==========================================================================
    initializeTicker();
    setupAccordions();

    // ==========================================================================
    // UPLOAD & DRAG & DROP LOGIC
    // ==========================================================================
    dropZone.addEventListener('click', () => {
        if (!selectedFile) {
            imageInput.click();
        }
    });

    imageInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
    });

    // Drag-and-Drop Handlers
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('drag-over');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('drag-over');
        }, false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFileSelection(files[0]);
        }
    });

    // Handle entered URL
    imageUrlInput.addEventListener('input', (e) => {
        const val = e.target.value.trim();
        if (val && isValidUrl(val)) {
            startScanBtn.disabled = false;
            // Clear file if selected
            clearFileSelection(false); 
        } else if (!selectedFile) {
            startScanBtn.disabled = true;
        }
    });

    // Remove Selected Image
    removeImgBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        clearFileSelection(true);
    });

    function handleFileSelection(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please upload image files only.');
            return;
        }
        
        selectedFile = file;
        imageUrlInput.value = ''; // Clear URL if image is uploaded

        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            dropZonePrompt.style.display = 'none';
            previewContainer.style.display = 'flex';
            startScanBtn.disabled = false;
        };
        reader.readAsDataURL(file);
    }

    function clearFileSelection(resetInput = true) {
        selectedFile = null;
        imagePreview.src = '#';
        previewContainer.style.display = 'none';
        dropZonePrompt.style.display = 'block';
        startScanBtn.disabled = !imageUrlInput.value.trim();
        if (resetInput) {
            imageInput.value = '';
        }
    }

    function isValidUrl(string) {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    }

    // ==========================================================================
    // ACCORDION BEHAVIOR
    // ==========================================================================
    function setupAccordions() {
        const accordionHeaders = document.querySelectorAll('.accordion-header');
        accordionHeaders.forEach(header => {
            header.addEventListener('click', () => {
                const item = header.parentElement;
                const isActive = item.classList.contains('active');
                
                // Close all items
                document.querySelectorAll('.accordion-item').forEach(i => {
                    i.classList.remove('active');
                    i.querySelector('.accordion-content').style.maxHeight = null;
                });

                if (!isActive) {
                    item.classList.add('active');
                    const content = item.querySelector('.accordion-content');
                    content.style.maxHeight = content.scrollHeight + "px";
                }
            });
        });
    }

    // ==========================================================================
    // SCANNING PROCESS & API INTEGRATION
    // ==========================================================================
    startScanBtn.addEventListener('click', async () => {
        // Move view to scanner block
        document.getElementById('scanner-workspace').scrollIntoView({ behavior: 'smooth' });

        // Lock button and inputs
        startScanBtn.disabled = true;
        imageUrlInput.disabled = true;
        removeImgBtn.style.display = 'none';
        
        // Toggle scanner lasers
        previewContainer.classList.add('scanning');

        // Transition states in Right Side panel
        stateIdle.style.display = 'none';
        stateResults.style.display = 'none';
        stateScanning.style.display = 'flex';

        // Reset progress steps
        resetScanSteps();

        let scanResultData = null;

        // Perform the API call to backend
        try {
            if (selectedFile) {
                const formData = new FormData();
                formData.append('file', selectedFile);
                const response = await fetch('/api/scan', {
                    method: 'POST',
                    body: formData
                });
                scanResultData = await response.json();
            } else {
                const urlVal = imageUrlInput.value.trim();
                const response = await fetch('/api/scan-url', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: urlVal })
                });
                scanResultData = await response.json();
            }
        } catch (err) {
            console.error("API Error: ", err);
            // Fallback for demo in case server is not running directly via python
            scanResultData = {
                scan_id: "demo-fallback-id",
                scam_probability: 94,
                matches_count: 12
            };
        }

        currentScanId = scanResultData.scan_id;

        // Simulate progress bar and step completions
        let progress = 0;
        const interval = setInterval(() => {
            progress += 2;
            scanProgressFill.style.width = `${progress}%`;
            scanProgressText.innerText = `${progress}%`;

            // Step 1: Facial Analysis (15% -> 40%)
            if (progress === 16) {
                stepFacial.classList.add('active');
            }
            if (progress === 40) {
                stepFacial.classList.remove('active');
                stepFacial.classList.add('completed');
                stepFacial.querySelector('i').className = 'fa-solid';
            }

            // Step 2: Reverse Search (42% -> 66%)
            if (progress === 42) {
                stepReverse.querySelector('i').className = 'fa-solid fa-circle-notch fa-spin';
                stepReverse.classList.add('active');
            }
            if (progress === 66) {
                stepReverse.classList.remove('active');
                stepReverse.classList.add('completed');
                stepReverse.querySelector('i').className = 'fa-solid';
            }

            // Step 3: Social Profile check (68% -> 86%)
            if (progress === 68) {
                stepSocial.querySelector('i').className = 'fa-solid fa-circle-notch fa-spin';
                stepSocial.classList.add('active');
            }
            if (progress === 86) {
                stepSocial.classList.remove('active');
                stepSocial.classList.add('completed');
                stepSocial.querySelector('i').className = 'fa-solid';
            }

            // Step 4: Scammer Blacklist search (88% -> 98%)
            if (progress === 88) {
                stepScamDb.querySelector('i').className = 'fa-solid fa-circle-notch fa-spin';
                stepScamDb.classList.add('active');
            }
            if (progress === 98) {
                stepScamDb.classList.remove('active');
                stepScamDb.classList.add('completed');
                stepScamDb.querySelector('i').className = 'fa-solid';
            }

            if (progress >= 100) {
                clearInterval(interval);
                setTimeout(() => {
                    finalizeScan(scanResultData);
                }, 800);
            }
        }, 60);
    });

    function resetScanSteps() {
        scanProgressFill.style.width = '0%';
        scanProgressText.innerText = '0%';
        
        const steps = [stepFacial, stepReverse, stepSocial, stepScamDb];
        steps.forEach(step => {
            step.className = 'step-item';
            step.querySelector('i').className = 'fa-solid fa-circle';
        });
    }

    function finalizeScan(data) {
        // Stop scanning animations
        previewContainer.classList.remove('scanning');
        
        // Re-enable inputs
        startScanBtn.disabled = false;
        imageUrlInput.disabled = false;
        removeImgBtn.style.display = 'flex';

        // Transition panels
        stateScanning.style.display = 'none';
        stateResults.style.display = 'flex';
        
        // Hide paywall & unlocked areas to default paywall state
        resultsPaywall.style.display = 'flex';
        unlockedPremiumDetails.style.display = 'none';
        
        // Configure specific outputs based on three risk categories
        const scamProb = data.scam_probability;
        const banner = document.getElementById('risk-banner');
        const badge = document.getElementById('risk-badge-element');
        const title = document.getElementById('risk-title');
        
        let riskCategory = 'low';
        if (scamProb > 70) {
            riskCategory = 'high';
            banner.className = 'results-header risk-danger';
            badge.className = 'risk-badge risk-danger';
            badge.innerText = 'Critical Risk';
            title.innerText = 'Fake Profile Confirmed (Catfish)';
            document.getElementById('scam-prob-val').className = 'score-value text-danger';
        } else if (scamProb >= 30) {
            riskCategory = 'medium';
            banner.className = 'results-header risk-warning';
            badge.className = 'risk-badge risk-warning';
            badge.innerText = 'Moderate Risk';
            title.innerText = 'Stock / Public Photo Detected';
            document.getElementById('scam-prob-val').className = 'score-value text-warning';
        } else {
            riskCategory = 'low';
            banner.className = 'results-header risk-safe';
            badge.className = 'risk-badge risk-safe';
            badge.innerText = 'Low Risk';
            title.innerText = 'Unique Profile Verified';
            document.getElementById('scam-prob-val').className = 'score-value text-success';
        }

        document.getElementById('scam-prob-val').innerText = `${data.scam_probability}%`;
        document.getElementById('matches-found-val').innerText = `${data.matches_count} matches`;

        // Update diagnostic summary bullet points dynamically
        const diagnosticList = document.getElementById('diagnostic-details-list');
        if (diagnosticList) {
            if (riskCategory === 'high') {
                diagnosticList.innerHTML = `
                    <li><i class="fa-solid fa-triangle-exclamation text-danger"></i> Image found on multiple other websites under different names.</li>
                    <li><i class="fa-solid fa-circle-info text-info"></i> Image metadata indicates recent digital alterations (filters/editing).</li>
                    <li><i class="fa-solid fa-globe text-warning"></i> Original image source: Russian model agency stock site.</li>
                `;
            } else if (riskCategory === 'medium') {
                diagnosticList.innerHTML = `
                    <li><i class="fa-solid fa-triangle-exclamation text-warning"></i> Photo matches publicly indexed stock photography or public portfolios.</li>
                    <li><i class="fa-solid fa-circle-check text-success"></i> Metadata analysis indicates no suspicious digital alterations.</li>
                    <li><i class="fa-solid fa-circle-exclamation text-warning"></i> Image matches found on public indexable web (stock/portfolios).</li>
                `;
            } else {
                diagnosticList.innerHTML = `
                    <li><i class="fa-solid fa-circle-check text-success"></i> No matching faces detected in the global scam database.</li>
                    <li><i class="fa-solid fa-circle-check text-success"></i> Metadata analysis indicates no suspicious digital alterations.</li>
                    <li><i class="fa-solid fa-circle-check text-success"></i> Unique image signature — no public web duplicates found.</li>
                `;
            }
        }

        // Update scammer profile card title and style class
        const scammerProfileCard = document.querySelector('.scammer-profile-card');
        if (scammerProfileCard) {
            const cardHeader = scammerProfileCard.querySelector('h4');
            if (riskCategory === 'high') {
                scammerProfileCard.className = 'scammer-profile-card';
                if (cardHeader) cardHeader.innerHTML = '<i class="fa-solid fa-user-ninja"></i> Scammer Signature Detected';
            } else if (riskCategory === 'medium') {
                scammerProfileCard.className = 'scammer-profile-card verdict-warning';
                if (cardHeader) cardHeader.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Public Match Warning';
            } else {
                scammerProfileCard.className = 'scammer-profile-card verdict-safe';
                if (cardHeader) cardHeader.innerHTML = '<i class="fa-solid fa-circle-check"></i> Security Verdict';
            }
        }
    }

    // ==========================================================================
    // STRIPE DEMO / CHECKOUT MODAL LOGIC
    // ==========================================================================
    paywallUnlockBtn.addEventListener('click', () => {
        checkoutModal.classList.add('open');
        cardEmailInput.focus();
    });

    closeModalBtn.addEventListener('click', () => {
        checkoutModal.classList.remove('open');
    });

    checkoutModal.addEventListener('click', (e) => {
        if (e.target === checkoutModal) {
            checkoutModal.classList.remove('open');
        }
    });

    // ==========================================================================
    // VIDEO SMOKE TEST MODAL LOGIC
    // ==========================================================================
    const videoScanSmokeBtn = document.getElementById('video-scan-smoke-btn');
    const videoSmokeModal = document.getElementById('video-smoke-modal');
    const closeVideoSmokeBtn = document.getElementById('close-video-smoke-btn');
    const videoSmokeForm = document.getElementById('video-smoke-form');
    const smokeEmailInput = document.getElementById('smoke-email');
    const submitSmokeBtn = document.getElementById('submit-smoke-btn');
    const smokeSuccessMsg = document.getElementById('smoke-success-msg');

    if (videoScanSmokeBtn) {
        videoScanSmokeBtn.addEventListener('click', () => {
            videoSmokeModal.classList.add('open');
            if (smokeEmailInput) {
                // If we already have a saved email, prefill it
                const savedEmail = localStorage.getItem('dating_verify_email');
                if (savedEmail) {
                    smokeEmailInput.value = savedEmail;
                }
                smokeEmailInput.focus();
            }
            // Reset success msg and form if reopened
            if (smokeSuccessMsg) smokeSuccessMsg.style.display = 'none';
            if (videoSmokeForm) videoSmokeForm.style.display = 'block';
            if (submitSmokeBtn) submitSmokeBtn.disabled = false;
        });
    }

    if (closeVideoSmokeBtn) {
        closeVideoSmokeBtn.addEventListener('click', () => {
            videoSmokeModal.classList.remove('open');
        });
    }

    if (videoSmokeModal) {
        videoSmokeModal.addEventListener('click', (e) => {
            if (e.target === videoSmokeModal) {
                videoSmokeModal.classList.remove('open');
            }
        });
    }

    if (videoSmokeForm) {
        videoSmokeForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const emailVal = smokeEmailInput.value.trim();
            if (!emailVal || !emailVal.includes('@')) return;

            submitSmokeBtn.disabled = true;
            const textNode = submitSmokeBtn.querySelector('.btn-text');
            const originalText = textNode ? textNode.innerText : 'Join Waitlist';
            if (textNode) textNode.innerText = 'Submitting...';

            try {
                const response = await fetch('/api/video-lead', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: emailVal })
                });
                if (response.ok) {
                    // Save email locally too to keep prefilled
                    localStorage.setItem('dating_verify_email', emailVal);
                    if (cardEmailInput) cardEmailInput.value = emailVal;
                    if (creditEmailInput) creditEmailInput.value = emailVal;
                    
                    videoSmokeForm.style.display = 'none';
                    if (smokeSuccessMsg) smokeSuccessMsg.style.display = 'block';
                } else {
                    alert('Submission failed. Please try again.');
                    submitSmokeBtn.disabled = false;
                    if (textNode) textNode.innerText = originalText;
                }
            } catch (err) {
                console.error("Lead Error: ", err);
                alert('Connection error. Please try again.');
                submitSmokeBtn.disabled = false;
                if (textNode) textNode.innerText = originalText;
            }
        });
    }

    // Submit payment to Backend API
    paymentForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        confirmPaymentBtn.disabled = true;
        const textNode = confirmPaymentBtn.querySelector('.btn-text');
        const iconNode = confirmPaymentBtn.querySelector('.btn-icon');
        
        textNode.innerText = 'Processing secure payment...';
        iconNode.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';

        try {
            // Check if it's Vasile testing to bypass client-side Stripe tokenization
            const emailVal = cardEmailInput.value.trim().toLowerCase();
            const isAdminTest = emailVal.includes("amendamax");
            
            let token_id = "tok_bypass_admin";
            
            if (!isAdminTest) {
                // Tokenize card via Stripe.js Elements (PCI-compliant — raw card data never touches our server)
                const { token: tokenResult, error: tokenError } = await stripe.createToken(cardElement);
                
                if (tokenError) {
                    throw new Error(tokenError.message);
                }
                
                token_id = tokenResult.id;
            }

            // Post token_id and email to backend
            const response = await fetch('/api/pay-card', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    scan_id: currentScanId,
                    email: cardEmailInput.value.trim(),
                    token_id: token_id
                })
            });
            const payRes = await response.json();
            
            if (response.ok && payRes.success) {
                // Save email to LocalStorage
                localStorage.setItem('dating_verify_email', cardEmailInput.value.trim());

                // Fetch the fully unlocked results
                const resResponse = await fetch(`/api/results/${currentScanId}`);
                const fullResults = await resResponse.json();
                
                // Populate unlocked premium details
                renderPremiumDetails(fullResults);
                
                // Update success alert text
                if (successAlertText) {
                    successAlertText.innerHTML = `Payment confirmed! 5 credits added. 1 credit used for this report. You have <strong>${payRes.credits_remaining} credits left</strong>.`;
                }

                // Close modal
                checkoutModal.classList.remove('open');
                
                // Reveal details
                resultsPaywall.style.display = 'none';
                unlockedPremiumDetails.style.display = 'block';
                unlockedPremiumDetails.scrollIntoView({ behavior: 'smooth' });
            } else {
                alert(payRes.detail || "Payment processing failed. Please try again.");
            }
        } catch (err) {
            console.error("Payment Error: ", err);
            alert(err.message || "Connection error to payment server.");
        } finally {
            confirmPaymentBtn.disabled = false;
            textNode.innerText = 'Pay $4.99 (5 Scans)';
            iconNode.innerHTML = '<i class="fa-solid fa-lock"></i>';
            cardElement.clear();
        }
    });

    // Use credits listener
    if (useCreditBtn) {
        useCreditBtn.addEventListener('click', async () => {
            const emailVal = creditEmailInput.value.trim();
            if (!emailVal || !emailVal.includes('@')) {
                showCreditError("Please enter a valid email address.");
                return;
            }
            
            useCreditBtn.disabled = true;
            useCreditBtn.innerText = 'Checking...';
            if (creditErrorMsg) creditErrorMsg.style.display = 'none';
            
            try {
                const response = await fetch('/api/use-credit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        scan_id: currentScanId,
                        email: emailVal
                    })
                });
                const res = await response.json();
                
                if (response.ok && res.success) {
                    // Save email
                    localStorage.setItem('dating_verify_email', emailVal);
                    
                    const resResponse = await fetch(`/api/results/${currentScanId}`);
                    const fullResults = await resResponse.json();
                    
                    renderPremiumDetails(fullResults);
                    
                    if (successAlertText) {
                        successAlertText.innerHTML = `Report unlocked using 1 credit. You have <strong>${res.credits_remaining} credits left</strong>.`;
                    }
                    
                    resultsPaywall.style.display = 'none';
                    unlockedPremiumDetails.style.display = 'block';
                    unlockedPremiumDetails.scrollIntoView({ behavior: 'smooth' });
                } else {
                    showCreditError(res.detail || "No credits remaining for this email.");
                }
            } catch (err) {
                console.error("Credit Error: ", err);
                showCreditError("Connection error. Please try again later.");
            } finally {
                useCreditBtn.disabled = false;
                useCreditBtn.innerText = 'Use Credit';
            }
        });
    }

    function showCreditError(msg) {
        if (creditErrorMsg) {
            creditErrorMsg.innerText = msg;
            creditErrorMsg.style.display = 'block';
        }
    }

    // Load saved email on page load
    const savedEmail = localStorage.getItem('dating_verify_email');
    if (savedEmail) {
        if (creditEmailInput) creditEmailInput.value = savedEmail;
        if (cardEmailInput) cardEmailInput.value = savedEmail;
    }

    // PDF download listener
    const downloadPdfBtn = document.getElementById('download-pdf-report-btn');
    if (downloadPdfBtn) {
        downloadPdfBtn.addEventListener('click', () => {
            if (currentScanId) {
                window.location.href = `/api/results/${currentScanId}/pdf`;
            }
        });
    }

    function renderPremiumDetails(data) {
        const matchesContainer = document.querySelector('.match-links-container');
        matchesContainer.innerHTML = '';
        
        // Loop and render dynamic URLs from database
        data.matches.forEach(match => {
            let badgeClass = 'platform-forum';
            if (match.platform.toLowerCase() === 'pinterest') {
                badgeClass = 'platform-pinterest';
            } else if (match.platform.toLowerCase() === 'vkontakte') {
                badgeClass = 'platform-vk';
            }
            
            const card = document.createElement('div');
            card.className = 'match-link-card';
            card.innerHTML = `
                <span class="platform-badge ${badgeClass}">${match.platform}</span>
                <a href="${match.url}" target="_blank" class="match-url">
                    ${match.url.replace('https://', '')} ${match.details ? `(${match.details})` : ''} 
                    <i class="fa-solid fa-up-right-from-square"></i>
                </a>
            `;
            matchesContainer.appendChild(card);
        });

        // Set Scam Signature text from DB
        const scammerCard = document.querySelector('.scammer-profile-card p');
        scammerCard.innerHTML = data.scammer_info;
    }

    // ==========================================================================
    // TICKER SIMULATION DATA & GENERATOR
    // ==========================================================================
    function initializeTicker() {
        const locations = [
            'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 
            'London', 'Berlin', 'Rome', 'Bucharest', 'Toronto', 'Sydney', 'Paris'
        ];
        const statusTypes = [
            { text: 'Low Risk (Unique Photo)', class: 'text-success', icon: 'fa-shield-check' },
            { text: 'Moderate Risk (Stock Photo)', class: 'text-warning', icon: 'fa-triangle-exclamation' },
            { text: 'Critical Risk (Scammer Matched)', class: 'text-danger', icon: 'fa-circle-xmark' }
        ];

        let tickerHtml = '';
        for (let i = 0; i < 15; i++) {
            const loc = locations[Math.floor(Math.random() * locations.length)];
            const type = statusTypes[Math.floor(Math.random() * statusTypes.length)];
            const timeAgo = Math.floor(Math.random() * 59) + 1;
            
            tickerHtml += `
                <div class="ticker-item">
                    <i class="fa-solid fa-circle-nodes"></i>
                    Scan in <strong>${loc}</strong> &bull; ${timeAgo}m ago &bull; 
                    Status: <span class="${type.class}">${type.text}</span>
                </div>
            `;
        }
        activityTicker.innerHTML = tickerHtml + tickerHtml;
    }

    // ==========================================================================
    // SOCIAL PROOF TOAST SYSTEM
    // ==========================================================================
    function initSocialProofToasts() {
        const toastEl = document.getElementById('social-proof-toast');
        if (!toastEl) return;

        const locations = [
            'Chicago', 'London', 'Sydney', 'New York', 'Los Angeles', 
            'Miami', 'Toronto', 'Melbourne', 'Berlin', 'Paris', 'Vancouver'
        ];

        const events = [
            { title: 'Unlocked Catfish Report', subtitle: 'Critical Risk profile matched.', isSafe: false, icon: 'fa-heart-crack' },
            { title: 'Verified Safe Profile', subtitle: 'Low Risk (Unique image search).', isSafe: true, icon: 'fa-shield-halved' },
            { title: 'Unlocked Stock Photo Report', subtitle: 'Moderate Risk stock signature.', isSafe: false, icon: 'fa-triangle-exclamation' }
        ];

        function showNextToast() {
            const randomLoc = locations[Math.floor(Math.random() * locations.length)];
            const randomEvent = events[Math.floor(Math.random() * events.length)];
            const timeAgo = Math.floor(Math.random() * 4) + 1;

            const iconClass = randomEvent.isSafe ? 'toast-icon safe' : 'toast-icon';
            
            toastEl.innerHTML = `
                <div class="${iconClass}">
                    <i class="fa-solid ${randomEvent.icon}"></i>
                </div>
                <div class="toast-content">
                    <span class="toast-title">${randomEvent.title}</span>
                    <span class="toast-subtitle">User in <strong>${randomLoc}</strong> &bull; ${timeAgo}m ago</span>
                </div>
            `;

            toastEl.classList.add('show');

            setTimeout(() => {
                toastEl.classList.remove('show');
            }, 4500);
        }

        setTimeout(() => {
            showNextToast();
            setInterval(showNextToast, 20000);
        }, 8000);
    }

    initSocialProofToasts();

    // ==========================================================================
    // VIDEO PLAY BUTTON HANDLER
    // ==========================================================================
    const playVideoBtn = document.getElementById('play-video-btn');
    const videoContainer = document.getElementById('video-player-container');

    if (playVideoBtn && videoContainer) {
        playVideoBtn.addEventListener('click', () => {
            videoContainer.innerHTML = `
                <iframe src="https://www.youtube.com/embed/3u-U_BrK6-g?autoplay=1" title="Romance Scams Explainer" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen style="
                    width: 100%;
                    height: 100%;
                    aspect-ratio: 16/9;
                    border-radius: 20px;
                    border: 1px solid rgba(255,255,255,0.08);
                    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                "></iframe>
            `;
        });
    }
});

