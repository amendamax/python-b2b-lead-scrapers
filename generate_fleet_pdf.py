import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

pdf_filename = "AI_Quantitative_Trading_Fleet_Report.pdf"

doc = SimpleDocTemplate(
    pdf_filename,
    pagesize=letter,
    rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
)

styles = getSampleStyleSheet()

# Color Palette
PRIMARY_COLOR = colors.HexColor("#1A365D")   # Deep Navy
SECONDARY_COLOR = colors.HexColor("#2B6CB0") # Slate Blue
DARK_NEUTRAL = colors.HexColor("#2D3748")    # Charcoal Text
LIGHT_BG = colors.HexColor("#F7FAFC")        # Soft Grey Background
BORDER_COLOR = colors.HexColor("#E2E8F0")

# Styles
title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Heading1'],
    fontName='Helvetica-Bold',
    fontSize=18,
    leading=22,
    textColor=PRIMARY_COLOR,
    spaceAfter=4
)

subtitle_style = ParagraphStyle(
    'DocSubTitle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=11,
    leading=14,
    textColor=SECONDARY_COLOR,
    spaceAfter=12
)

section_heading = ParagraphStyle(
    'SectionHeading',
    parent=styles['Heading2'],
    fontName='Helvetica-Bold',
    fontSize=13,
    leading=16,
    textColor=PRIMARY_COLOR,
    spaceBefore=12,
    spaceAfter=6
)

bot_title_style = ParagraphStyle(
    'BotTitle',
    parent=styles['Heading3'],
    fontName='Helvetica-Bold',
    fontSize=10,
    leading=12,
    textColor=SECONDARY_COLOR,
    spaceBefore=6,
    spaceAfter=4
)

body_style = ParagraphStyle(
    'BodyDark',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9,
    leading=12,
    textColor=DARK_NEUTRAL,
    spaceAfter=4
)

bold_body = ParagraphStyle(
    'BoldBody',
    parent=body_style,
    fontName='Helvetica-Bold'
)

bullet_style = ParagraphStyle(
    'BulletText',
    parent=body_style,
    leftIndent=12,
    spaceAfter=3
)

story = []

# 1. Header
story.append(Paragraph("AI QUANTITATIVE TRADING FLEET", title_style))
story.append(Paragraph("Technical Specifications & Historical Backtesting Performance Report", subtitle_style))
story.append(Paragraph("<b>Architect:</b> Vasile Bratu &nbsp;|&nbsp; <b>Deploy Environment:</b> Live High-Availability VPS 24/7", body_style))
story.append(Spacer(1, 8))
story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_COLOR, spaceAfter=10))

# 2. Executive Summary
story.append(Paragraph("Executive Summary", section_heading))
story.append(Paragraph(
    "This technical report outlines the strategy, architecture, and backtesting metrics of the quantitative trading fleet "
    "actively deployed on the production VPS. The fleet consists of 8 automated Python engines utilizing Machine Learning "
    "(XGBoost, LightGBM), statistical arbitrage, and options writing mechanics to trade multiple asset classes with low-drawdown profiles.",
    body_style
))
story.append(Spacer(1, 6))

# 3. Component Matrix Table
story.append(Paragraph("Fleet Component Matrix", section_heading))

matrix_data = [
    [
        Paragraph("<b>Bot / Engine Name</b>", bold_body), 
        Paragraph("<b>Asset Class</b>", bold_body), 
        Paragraph("<b>Core Strategy / Regime</b>", bold_body), 
        Paragraph("<b>Backtest ROI</b>", bold_body), 
        Paragraph("<b>Max DD</b>", bold_body)
    ],
    [
        Paragraph("1. BTCUSD Super Bot", body_style),
        Paragraph("Crypto", body_style),
        Paragraph("ML XGBoost Dual-Regime (ADX/RSI)", body_style),
        Paragraph("+17.86%", body_style),
        Paragraph("5.29%", body_style)
    ],
    [
        Paragraph("2. NASDAQ Super Bot v5.0", body_style),
        Paragraph("Indices", body_style),
        Paragraph("Ensemble ML (XGB+LGBM) Inter-market", body_style),
        Paragraph("+65.79%", body_style),
        Paragraph("6.17%", body_style)
    ],
    [
        Paragraph("3. US30 Session Breakout", body_style),
        Paragraph("Indices", body_style),
        Paragraph("NY Open Institutional Vol Breakout", body_style),
        Paragraph("+22.70%", body_style),
        Paragraph("4.67%", body_style)
    ],
    [
        Paragraph("4. EURO Super Bot v5.0", body_style),
        Paragraph("Forex", body_style),
        Paragraph("VWAP Std Dev Range Mean Reversion", body_style),
        Paragraph("+1.97%", body_style),
        Paragraph("0.98%", body_style)
    ],
    [
        Paragraph("5. EURUSD Swing Architect", body_style),
        Paragraph("Forex", body_style),
        Paragraph("M15 Structural Swing (H1/H4 Filter)", body_style),
        Paragraph("+11.20%", body_style),
        Paragraph("3.45%", body_style)
    ],
    [
        Paragraph("6. GOLD Breakout Sniper", body_style),
        Paragraph("Commodities", body_style),
        Paragraph("M15 Z-Score Volume Breakout (ATR)", body_style),
        Paragraph("+34.51%", body_style),
        Paragraph("5.12%", body_style)
    ],
    [
        Paragraph("7. Pepperstone Accelerator 500", body_style),
        Paragraph("Micro Indices", body_style),
        Paragraph("Order Book Imbalance Scalper (0.01 lot)", body_style),
        Paragraph("+25.70%", body_style),
        Paragraph("8.20%", body_style)
    ],
    [
        Paragraph("8. IBKR Options Bot", body_style),
        Paragraph("US Equities", body_style),
        Paragraph("Bull Put spreads (VIX-Adaptive Delta)", body_style),
        Paragraph("+14.2% Ann.", body_style),
        Paragraph("11.5%", body_style)
    ]
]

# Total width is 532 (8.5 inch letter = 612 - 80 margin)
matrix_table = Table(matrix_data, colWidths=[1.4*inch, 0.9*inch, 2.7*inch, 1.2*inch, 1.0*inch])
matrix_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
    ('TEXTCOLOR', (0,0), (-1,-1), DARK_NEUTRAL),
    ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
]))
story.append(matrix_table)
story.append(Spacer(1, 10))

# 4. Strategy & Deep-Dive Specifications
story.append(Paragraph("Strategy & Deep-Dive Specifications", section_heading))

# Bot 1
story.append(Paragraph("1. BTCUSD 24/7 Super Bot (C:\\BTC_SUPER_BOT)", bot_title_style))
story.append(Paragraph("• <b>Logic:</b> Employs an XGBoost Classifier trained on historical Bitcoin volatility. It dynamically switches between two market regimes: ADX > 25 activates trend-following aligned with the M15 EMA 50; ADX < 25 activates mean reversion based on RSI extreme levels (RSI < 35 / > 65).", bullet_style))
story.append(Paragraph("• <b>Risk Management:</b> Stop Loss at 1.5x ATR, Take Profit at 2.5x ATR (1:2.5 Risk/Reward ratio). Maximum 2 concurrent positions.", bullet_style))
story.append(Paragraph("• <b>Backtest Results:</b> +17.86% ROI, 5.29% Max Drawdown, 55.1% Win Rate.", bullet_style))

# Bot 2
story.append(Paragraph("2. NASDAQ Super Bot v5.0 (C:\\NASDAQ_SUPER_BOT_V5)", bot_title_style))
story.append(Paragraph("• <b>Logic:</b> An ensemble of XGBoost and LightGBM models trained on M5 order flow. It detects inter-market spread divergence between NASDAQ (US100) and S&P500 (US500) to capture explosive micro-trends.", bullet_style))
story.append(Paragraph("• <b>Risk Management:</b> Integrated with <b>FTMO Guard v5.0</b> (hard stop on 4.5% daily drawdown or 8.0% total drawdown). Automated news blackout (30m before, 15m after high-impact news) and daily rollover freeze (23:50 to 00:10).", bullet_style))
story.append(Paragraph("• <b>Backtest Results:</b> +65.79% ROI, 6.17% Max Drawdown, 43.1% Win Rate with highly positive R:R.", bullet_style))

# Bot 3
story.append(Paragraph("3. US30 Session Breakout (C:\\US30_SUPER_BOT)", bot_title_style))
story.append(Paragraph("• <b>Logic:</b> Specializes in institutional breakout moves during the New York market open. Features an XGBoost Classifier optimized for the initial 2 hours of NY volatility.", bullet_style))
story.append(Paragraph("• <b>Risk Management:</b> Strict temporal filter (active execution only between 14:30 and 21:00 UTC). SL at 1.5x ATR, TP at 2.5x ATR.", bullet_style))
story.append(Paragraph("• <b>Backtest Results:</b> +22.70% ROI, 4.67% Max Drawdown, 54.5% Win Rate, Profit Factor: 3.04.", bullet_style))

# Bot 4
story.append(Paragraph("4. EURO Super Bot v5.0 (C:\\EURO_SUPER_BOT_V5)", bot_title_style))
story.append(Paragraph("• <b>Logic:</b> Ultra-low risk Mean Reversion bot tracking volume-weighted average price (VWAP) deviations and standard deviation bands.", bullet_style))
story.append(Paragraph("• <b>Risk Management:</b> Designed for maximum capital preservation. Backtested drawdown limited to under 1.00% overall. Employs dynamic trailing stops.", bullet_style))
story.append(Paragraph("• <b>Backtest Results:</b> +1.97% ROI, 0.98% Max Drawdown, 50.0% Win Rate, Profit Factor: 2.97.", bullet_style))

# Bot 5
story.append(Paragraph("5. EURUSD Swing Architect (C:\\EURUSD_SWING_ARCHITECT)", bot_title_style))
story.append(Paragraph("• <b>Logic:</b> Classic M15 swing trading engine executing trades on H1/H4 structural support and resistance confirmations.", bullet_style))
story.append(Paragraph("• <b>Risk Management:</b> Strict 1.0% risk per trade. Automatic trailing stop to Breakeven (BE) once a 1:1 R:R is reached.", bullet_style))
story.append(Paragraph("• <b>Backtest Results:</b> +11.20% ROI, 3.45% Max Drawdown, 58.2% Win Rate.", bullet_style))

# Bot 6
story.append(Paragraph("6. GOLD Breakout Sniper (C:\\GOLD_BREAKOUT_SNIPER)", bot_title_style))
story.append(Paragraph("• <b>Logic:</b> Volatility momentum breakout engine tracking volume Z-score and ATR expansion. Enters on high-volume breakouts.", bullet_style))
story.append(Paragraph("• <b>Risk Management:</b> Banned execution during the Asian session. Stop Loss and Take Profit calculated dynamically via ATR.", bullet_style))
story.append(Paragraph("• <b>Backtest Results:</b> +34.51% ROI, 5.12% Max Drawdown, 48.5% Win Rate.", bullet_style))

# Bot 7
story.append(Paragraph("7. Pepperstone Accelerator 500 (C:\\PEPPERSTONE_ACCELERATOR_500)", bot_title_style))
story.append(Paragraph("• <b>Logic:</b> High-frequency order book imbalance scalper optimized for micro index contracts.", bullet_style))
story.append(Paragraph("• <b>Risk Management:</b> Strict leverage caps and minimal lot sizes (0.01 - 0.02) to safely trade small account balances.", bullet_style))
story.append(Paragraph("• <b>Backtest Results:</b> +25.70% ROI, 8.20% Max Drawdown, 62.0% Win Rate (on 500 EUR account).", bullet_style))

# Bot 8
story.append(Paragraph("8. IBKR Options Bot (C:\\ib_options_bot)", bot_title_style))
story.append(Paragraph("• <b>Logic:</b> Automated credit spread engine selling Bull Put Spreads (0.15 Delta Short, protective Put 5 strikes below) with 30-45 DTE on 12 liquid tech leaders (AAPL, MSFT, TSLA, NVDA, SPY, etc.).", bullet_style))
story.append(Paragraph("• <b>Safeguards:</b> VIX-Adaptive Delta (strike buffer adjusted dynamically), Gamma Risk Shield (closes positions at 21 DTE to eliminate late-stage gamma risk), and Earnings Blackout (no trades within 14 days of earnings).", bullet_style))
story.append(Paragraph("• <b>Backtest Results:</b> +14.2% annualized ROI, 89.4% Spread Win Rate, 11.5% Portfolio Max Drawdown.", bullet_style))
story.append(Spacer(1, 6))

# 5. Centralized Safeguards
story.append(Paragraph("Centralized Safeguards & Operations", section_heading))
story.append(Paragraph("• <b>FleetWatchdog:</b> A system watchdog running outside sandbox environments via Windows Task Scheduler (PID 7388) that automatically restarts any terminated python engine within 5 seconds of connection drops.", bullet_style))
story.append(Paragraph("• <b>FN Risk Sentinel:</b> An independent Python process (PID 6320) monitoring aggregate equity. Enforces a hard stop and closes all open market positions if aggregate drawdown breaches pre-configured limits.", bullet_style))
story.append(Spacer(1, 6))

# 6. Disclaimer
story.append(HRFlowable(width="100%", thickness=1, color=BORDER_COLOR, spaceBefore=8, spaceAfter=8))
story.append(Paragraph(
    "<b>Disclaimer:</b> These algorithmic systems are designed for proprietary research and personal portfolio management. "
    "Past performance is not indicative of future results. Algorithmic trading on leverage carries substantial risk of capital loss.",
    body_style
))

# Build Document
doc.build(story)
print(f"[+] Quant Fleet PDF Report created: {os.path.abspath(pdf_filename)}")
