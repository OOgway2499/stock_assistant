"""
HTML Test Report Generator — Beautiful dark-theme report.
"""

import os
from datetime import datetime


def generate_html_report(results: dict, output_path: str = None):
    """
    Generate a beautiful HTML test report.

    Args:
        results: dict with keys:
            - categories: list of {name, total, passed, failed, skipped, tests: [{name, status, message, time}]}
            - total, passed, failed, skipped, score
            - total_time
            - data_source_health: dict
            - recommendations: list of strings
        output_path: where to save HTML (default: tests/test_report.html)
    """
    if output_path is None:
        output_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "test_report.html"
        )

    total = results.get("total", 0)
    passed = results.get("passed", 0)
    failed = results.get("failed", 0)
    skipped = results.get("skipped", 0)
    score = results.get("score", 0)
    total_time = results.get("total_time", 0)
    categories = results.get("categories", [])
    health = results.get("data_source_health", {})
    recommendations = results.get("recommendations", [])
    now = datetime.now().strftime("%d %B %Y, %I:%M %p")

    # Build category rows
    cat_rows = ""
    for cat in categories:
        if cat['failed'] > 0:
            status = "❌"
        elif cat['passed'] > 0:
            status = "✅"
        elif cat['skipped'] > 0:
            status = "⏭️"
        else:
            status = "⚠️"

        cat_rows += f"""
        <tr>
            <td>{cat['name']}</td>
            <td>{cat['total']}</td>
            <td class="pass">{cat['passed']}</td>
            <td class="fail">{cat['failed']}</td>
            <td class="skip">{cat['skipped']}</td>
            <td>{status}</td>
        </tr>"""

    # Build detailed test rows
    detail_rows = ""
    skipped_rows = ""
    for cat in categories:
        detail_rows += f'<h3 class="cat-header">{cat["name"]}</h3>'
        for t in cat.get("tests", []):
            if t["status"] == "passed":
                icon = "✅"
                cls = "passed"
            elif t["status"] == "skipped":
                icon = "⏭️"
                cls = "skipped"
                # Add to skipped summary section
                msg = t.get("message", "").replace("<", "&lt;").replace(">", "&gt;")
                skipped_rows += f"""
                <div class="test-row skipped">
                    <span class="test-icon">⏭️</span>
                    <span class="test-name">{t['name']}</span>
                    <div class="test-msg">{msg}</div>
                </div>"""
            else:
                icon = "❌"
                cls = "failed"

            msg = t.get("message", "").replace("<", "&lt;").replace(">", "&gt;")
            time_str = f'{t.get("time", 0):.1f}s'
            detail_rows += f"""
            <div class="test-row {cls}">
                <span class="test-icon">{icon}</span>
                <span class="test-name">{t['name']}</span>
                <span class="test-time">{time_str}</span>
                {f'<div class="test-msg">{msg}</div>' if msg and cls != 'passed' else ''}
            </div>"""

    # Build health rows
    health_rows = ""
    for source, status in health.items():
        if status['ok']:
            icon = "✅"
            cls = "pass"
        elif "skipped" in status['label'].lower() or "not configured" in status['label'].lower():
            icon = "⏭️"
            cls = "skip"
        else:
            icon = "❌"
            cls = "fail"

        health_rows += f"""
        <div class="health-row">
            <span>{icon}</span>
            <span class="health-name">{source}</span>
            <span class="health-status {cls}">{status['label']}</span>
        </div>"""

    # Build recommendations
    rec_html = ""
    if recommendations:
        for rec in recommendations:
            rec_html += f'<div class="rec-item">💡 {rec}</div>'
    else:
        rec_html = '<div class="rec-item success">🎉 All tests passed! No fixes needed.</div>'

    # Score color
    if score >= 95:
        score_color = "#4ade80"
    elif score >= 70:
        score_color = "#facc15"
    else:
        score_color = "#f87171"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Test Report — Indian Stock Market AI Assistant</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#0d1117; color:#e6edf3; font-family:'Segoe UI',system-ui,-apple-system,sans-serif; padding:24px; }}
.header {{ text-align:center; margin-bottom:32px; }}
.header h1 {{ font-size:28px; margin-bottom:4px; }}
.header .subtitle {{ color:#8b949e; font-size:14px; }}
.cards {{ display:grid; grid-template-columns:repeat(5,1fr); gap:16px; margin-bottom:32px; }}
.card {{ background:#161b22; border:1px solid #30363d; border-radius:12px; padding:20px; text-align:center; }}
.card .label {{ color:#8b949e; font-size:12px; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px; }}
.card .value {{ font-size:32px; font-weight:700; }}
.card .value.pass {{ color:#4ade80; }}
.card .value.fail {{ color:#f87171; }}
.card .value.skip {{ color:#facc15; font-size:24px; line-height:38px; }}
table {{ width:100%; border-collapse:collapse; margin-bottom:32px; background:#161b22; border-radius:12px; overflow:hidden; }}
th {{ background:#21262d; color:#8b949e; text-align:left; padding:12px 16px; font-size:13px; text-transform:uppercase; letter-spacing:1px; }}
td {{ padding:12px 16px; border-bottom:1px solid #21262d; }}
td.pass, .health-status.pass {{ color:#4ade80; font-weight:600; }}
td.fail, .health-status.fail {{ color:#f87171; font-weight:600; }}
td.skip, .health-status.skip {{ color:#facc15; font-weight:600; }}
.section {{ margin-bottom:32px; }}
.section h2 {{ font-size:20px; margin-bottom:16px; border-bottom:1px solid #30363d; padding-bottom:8px; }}
.cat-header {{ color:#58a6ff; font-size:16px; margin:20px 0 10px; }}
.test-row {{ background:#161b22; border:1px solid #30363d; border-radius:8px; padding:10px 16px; margin:6px 0; display:flex; flex-wrap:wrap; align-items:center; gap:10px; }}
.test-row.passed {{ border-left:3px solid #4ade80; }}
.test-row.failed {{ border-left:3px solid #f87171; }}
.test-row.skipped {{ border-left:3px solid #facc15; }}
.test-icon {{ font-size:16px; }}
.test-name {{ flex:1; font-size:14px; }}
.test-time {{ color:#8b949e; font-size:12px; }}
.test-msg {{ width:100%; color:#8b949e; font-size:13px; padding:4px 0 0 28px; font-family:monospace; white-space:pre-wrap; }}
.health-row {{ background:#161b22; border:1px solid #30363d; border-radius:8px; padding:10px 16px; margin:6px 0; display:flex; align-items:center; gap:10px; }}
.health-name {{ flex:1; font-weight:500; }}
.health-status {{ font-size:13px; }}
.rec-item {{ background:#161b22; border:1px solid #30363d; border-radius:8px; padding:10px 16px; margin:6px 0; font-size:14px; line-height:1.5; }}
.rec-item.success {{ border-left:3px solid #4ade80; }}
</style>
</head>
<body>
<div class="header">
    <h1>🇮🇳 Indian Stock Market AI Assistant</h1>
    <div class="subtitle">Test Report — {now}</div>
</div>

<div class="cards">
    <div class="card"><div class="label">Total Tests</div><div class="value">{total}</div></div>
    <div class="card"><div class="label">Passed</div><div class="value pass">{passed} ✅</div></div>
    <div class="card"><div class="label">Failed</div><div class="value fail">{failed} ❌</div></div>
    <div class="card"><div class="label">Skipped (Not Failed)</div><div class="value skip">{skipped} ⏭️</div></div>
    <div class="card"><div class="label">Score (Configured)</div><div class="value" style="color:{score_color}">{score:.1f}%</div></div>
</div>

<div class="section">
    <h2>📊 Category Summary</h2>
    <table>
        <tr><th>Category</th><th>Tests</th><th>Passed</th><th>Failed</th><th>Skipped</th><th>Status</th></tr>
        {cat_rows}
    </table>
</div>

{f'''
<div class="section">
    <h2>⏭️ Skipped Tests (Need Configuration)</h2>
    <div style="color:#8b949e; margin-bottom:12px; font-size:14px;">These tests were skipped because credentials are not set in the .env file. They are NOT counted as failures.</div>
    {skipped_rows}
</div>''' if skipped_rows else ''}

<div class="section">
    <h2>🏥 Data Source Health</h2>
    {health_rows}
</div>

<div class="section">
    <h2>💡 Recommendations</h2>
    {rec_html}
</div>

<div class="section">
    <h2>🔍 Detailed Results</h2>
    {detail_rows}
</div>

<div style="text-align:center; color:#8b949e; margin-top:40px; font-size:12px; padding:20px;">
    ⏱️ Total Time: {total_time:.1f}s | Generated: {now} | 🇮🇳 Made in India
</div>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path
