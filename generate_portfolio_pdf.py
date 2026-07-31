import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

pdf_filename = "Vasile_Bratu_Python_Automation_Portfolio.pdf"

doc = SimpleDocTemplate(
    pdf_filename,
    pagesize=letter,
    rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
)

styles = getSampleStyleSheet()

# Custom Color Palette
PRIMARY_COLOR = colors.HexColor("#1A365D")   # Deep Navy
SECONDARY_COLOR = colors.HexColor("#2B6CB0") # Slate Blue
DARK_NEUTRAL = colors.HexColor("#2D3748")    # Charcoal Body Text
LIGHT_BG = colors.HexColor("#F7FAFC")        # Soft Grey Background
BORDER_COLOR = colors.HexColor("#E2E8F0")

# Custom Styles
title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Heading1'],
    fontName='Helvetica-Bold',
    fontSize=22,
    leading=26,
    textColor=PRIMARY_COLOR,
    spaceAfter=4
)

subtitle_style = ParagraphStyle(
    'DocSubTitle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=12,
    leading=16,
    textColor=SECONDARY_COLOR,
    spaceAfter=15
)

section_heading = ParagraphStyle(
    'SectionHeading',
    parent=styles['Heading2'],
    fontName='Helvetica-Bold',
    fontSize=14,
    leading=18,
    textColor=PRIMARY_COLOR,
    spaceBefore=12,
    spaceAfter=6
)

body_style = ParagraphStyle(
    'BodyDark',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=10,
    leading=14,
    textColor=DARK_NEUTRAL,
    spaceAfter=6
)

bold_body = ParagraphStyle(
    'BoldBody',
    parent=body_style,
    fontName='Helvetica-Bold'
)

bullet_style = ParagraphStyle(
    'BulletText',
    parent=body_style,
    leftIndent=15,
    spaceAfter=4
)

story = []

# 1. Header Section (Cleaned of email/phone contact details per Upwork TOS)
story.append(Paragraph("Vasile Bratu", title_style))
story.append(Paragraph("Senior Python & Web Automation Engineer | Web Scraping & API Specialist", subtitle_style))
story.append(Paragraph("<b>GitHub:</b> github.com/amendamax &nbsp;|&nbsp; <b>Upwork Verified Freelancer</b>", body_style))
story.append(Spacer(1, 10))
story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_COLOR, spaceAfter=12))

# 2. Executive Summary
story.append(Paragraph("Executive Summary", section_heading))
story.append(Paragraph(
    "Senior Python Engineer with 6+ years of specialized experience in building complex, stateful web scraping systems, "
    "interactive portal automation, and resilient data extraction pipelines. Proven track record in bypassing modern anti-bot "
    "protections (Cloudflare, DataDome, 2FA workflows), session state management, and delivering clean, executive-ready Excel/DB datasets.",
    body_style
))
story.append(Spacer(1, 8))

# 3. Core Technical Capabilities
story.append(Paragraph("Core Technical Capabilities", section_heading))

caps_data = [
    [Paragraph("<b>Category</b>", bold_body), Paragraph("<b>Technologies & Architecture</b>", bold_body)],
    [Paragraph("Browser Automation", body_style), Paragraph("Python 3.11+, Playwright Async, Selenium, Playwright-Stealth, Puppeteer", body_style)],
    [Paragraph("Session & 2FA Handling", body_style), Paragraph("StorageState JSON, Cookie Persistence, SMS API / Webhook 2FA Capturers", body_style)],
    [Paragraph("Fault-Tolerance & Checkpoints", body_style), Paragraph("SQLite / JSON Checkpoint Engines, Resumable Scraping, Auto-Reauth", body_style)],
    [Paragraph("Backend & Data Pipelines", body_style), Paragraph("FastAPI, PostgreSQL, SQLAlchemy, AWS S3 Vault, Pydantic, REST APIs", body_style)],
    [Paragraph("Executive Data Export", body_style), Paragraph("OpenPyXL (Styled Excel Reports), Pandas, CSV, JSON, Google Sheets API", body_style)]
]

caps_table = Table(caps_data, colWidths=[2.0*inch, 5.0*inch])
caps_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (1,0), LIGHT_BG),
    ('TEXTCOLOR', (0,0), (-1,-1), DARK_NEUTRAL),
    ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ('TOPPADDING', (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
]))
story.append(caps_table)
story.append(Spacer(1, 12))

# 4. Featured Project Case Studies
story.append(Paragraph("Featured Case Studies & Architectural Solutions", section_heading))

# Project 1
story.append(Paragraph("<b>1. Stateful Interactive Portal Scraper & SMS 2FA Engine</b>", bold_body))
story.append(Paragraph("• <b>Challenge:</b> Extracting structured multi-popup data from authenticated interactive web portals requiring occasional SMS 2FA.", bullet_style))
story.append(Paragraph("• <b>Solution:</b> Built an asynchronous Playwright Python pipeline using persistent storage state. Integrated an SMS webhook API to capture 2FA tokens on the fly without human intervention.", bullet_style))
story.append(Paragraph("• <b>Fault Tolerance:</b> Implemented a local SQLite checkpoint engine to log progress per record. The scraper automatically recovers from network disconnects and resumes execution seamlessly.", bullet_style))
story.append(Spacer(1, 6))

# Project 2
story.append(Paragraph("<b>2. Enterprise B2B Lead Scraping & Verification Suite</b>", bold_body))
story.append(Paragraph("• <b>Challenge:</b> Harvesting fresh, verified business lead records across global directories while maintaining low bounce rates.", bullet_style))
story.append(Paragraph("• <b>Solution:</b> Developed multi-source Python extractors with Playwright stealth, automated email syntax and SMTP ping verification, exporting deduplicated, styled Excel workbooks via OpenPyXL.", bullet_style))
story.append(Spacer(1, 6))

# Project 3
story.append(Paragraph("<b>3. FastAPI Backend & S3 Document Vault Microservice</b>", bold_body))
story.append(Paragraph("• <b>Challenge:</b> Building a high-speed async backend for user ingestion, secure S3 file storage, and AI LLM chat sessions.", bullet_style))
story.append(Paragraph("• <b>Solution:</b> Engineered a modular FastAPI application with OAuth2/JWT authentication, PostgreSQL persistence, and pre-signed S3 URLs.", bullet_style))
story.append(Spacer(1, 6))

# Project 4
story.append(Paragraph("<b>4. Asynchronous AI Quantitative Trading Fleet & Options Engine</b>", bold_body))
story.append(Paragraph("• <b>Challenge:</b> Deploying and managing a diversified portfolio of 8 automated trading engines with real-time execution across crypto, indices, forex, and stocks, while maintaining strict drawdown caps and zero API latency.", bullet_style))
story.append(Paragraph("• <b>Solution:</b> Developed a robust VPS-hosted Python infrastructure running Machine Learning Ensemble models (XGBoost & LightGBM), dynamic trend-alignment filters, and a secure Options writing engine (Bull Put spreads with VIX-adaptive Delta and 21-DTE Gamma Risk Shields). Monitored by a central watchdog scheduler and risk sentinel.", bullet_style))
story.append(Paragraph("• <b>Results:</b> Achieved diversified market exposure with 0 active execution errors, 89.4% win rate on index/stock option spreads, and maximum drawdown kept strictly under 5% across backtests.", bullet_style))
story.append(Paragraph("• <b>Architecture & Documentation:</b> github.com/amendamax/ai-quantitative-trading-fleet", bullet_style))
story.append(Spacer(1, 12))

# 5. Published Engineering Articles
story.append(Paragraph("Technical Publications & Open Source", section_heading))
story.append(Paragraph("• <b>How to Build Executive-Ready Excel Reports Directly in Python Using OpenPyXL</b> (Published Engineering Article)", bullet_style))
story.append(Paragraph("• <b>Ethical Web Scraping & GDPR Compliance for Enterprise Data Extraction</b> (Published Engineering Article)", bullet_style))
story.append(Paragraph("• <b>GitHub Open Source Repositories:</b> github.com/amendamax", bullet_style))

# Build Document
doc.build(story)
print(f"[+] PDF curatat conform Upwork TOS: {os.path.abspath(pdf_filename)}")
