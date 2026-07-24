import os

app_files = ['dating-photo-checker/broker-verifier/app.js', 'broker-verifier/app.js']

for af in app_files:
    if os.path.exists(af):
        with open(af, 'r', encoding='utf-8') as f:
            content = f.read()

        # Wrap searchInput event listeners safely
        content = content.replace('searchInput.addEventListener("input", function() {', 'if (searchInput) {\nsearchInput.addEventListener("input", function() {')
        content = content.replace('searchInput.addEventListener("keydown", function(e) {', 'searchInput.addEventListener("keydown", function(e) {')
        
        # Make sure the closing brace for searchInput check is added
        old_close = '''            executeScan(firstMatch.name, firstMatch.domain);
        }
    }
});'''
        new_close = '''            executeScan(firstMatch.name, firstMatch.domain);
        }
    }
});
} // end if (searchInput)'''

        if old_close in content and 'end if (searchInput)' not in content:
            content = content.replace(old_close, new_close)

        # Wrap openWizardBtn listener safely
        content = content.replace('openWizardBtn.addEventListener("click", () => {', 'if (openWizardBtn) {\nopenWizardBtn.addEventListener("click", () => {')
        content = content.replace('closeWizardBtn.addEventListener("click", () => {', '}\nif (closeWizardBtn) {\ncloseWizardBtn.addEventListener("click", () => {')
        content = content.replace('wizardModal.addEventListener("click", (e) => {', '}\nif (wizardModal) {\nwizardModal.addEventListener("click", (e) => {')

        # Wrap paywall buttons safely
        content = content.replace('paywallUnlockBtn.addEventListener("click", () => {', '}\nif (paywallUnlockBtn) {\npaywallUnlockBtn.addEventListener("click", () => {')
        content = content.replace('closeCheckoutBtn.addEventListener("click", () => {', '}\nif (closeCheckoutBtn) {\ncloseCheckoutBtn.addEventListener("click", () => {')
        content = content.replace('paymentForm.addEventListener("submit", async (e) => {', '}\nif (paymentForm) {\npaymentForm.addEventListener("submit", async (e) => {')

        with open(af, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Hardened null checks in {af}")

print("App.js null checks hardened successfully!")
