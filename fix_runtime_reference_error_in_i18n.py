import os

app_files = ['dating-photo-checker/broker-verifier/app.js', 'broker-verifier/app.js']

clean_i18n_en = '''    en: {
        typePending: "Type: Pending Audit",
        typeCompleted: "Type: Forensic Audit Completed",
        sourcePrefix: "Source: Forensic Verification ID",
        lockedRed: "[LOCKED] Audit reports are restricted. Unlock full report to reveal active threat flags.",
        lockedGreen: "[LOCKED] Audit reports are restricted. Unlock full report to reveal security assets.",
        noRisk: "No imminent risk factors identified.",
        noSafety: "No solid safety elements identified.",
        verifiedPartner: "🟢 Verified & Regulated Safe Broker Partner",
        openAccount: "Open Official Account at",
        euResidentTitle: "European Resident?",
        euResidentText: "Get 1:1000 leverage, deposit bonuses, and Copy Trading under XM Global regulations.",
        euWhatsappLink: "Chat with us on WhatsApp for private registration instructions →",
        excellentScore: "Excellent Score",
        goodScore: "Good Score (Safe)",
        warningRisk: "Warning / Medium Risk",
        highRisk: "High Risk",
        scamAlert: "Fraud Warning / Blacklisted",
        awaitingEval: "Awaiting Evaluation",
        scanCompleted: "The analysis has completed."
    },'''

for af in app_files:
    if os.path.exists(af):
        with open(af, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find en: { ... } inside i18n and replace with clean_i18n_en
        import re
        content = re.sub(r'en:\s*\{[\s\S]*?\},', clean_i18n_en, content, count=1)

        with open(af, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed runtime ReferenceError in i18n.en in {af}")

print("i18n.en fixed successfully!")
