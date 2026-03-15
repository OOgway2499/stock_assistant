"""
🇮🇳 Indian Stock Market AI Assistant — Master Test Runner
Run all tests with beautiful CLI output and HTML report generation.

Usage:
  python run_tests.py           ← run all tests
  python run_tests.py --data    ← data sources only
  python run_tests.py --tools   ← tools only
  python run_tests.py --llm     ← LLM only
  python run_tests.py --guard   ← topic guard only
  python run_tests.py --quick   ← skip LLM tests (faster)
"""

import sys
import os
import re
import time
import argparse
import subprocess
import webbrowser

# Add project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Fore:
        GREEN = RED = YELLOW = CYAN = WHITE = MAGENTA = RESET = ""
    class Style:
        BRIGHT = RESET_ALL = ""


# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════

TEST_CATEGORIES = [
    {"name": "Data Sources", "file": "tests/test_data_sources.py", "flag": "--data", "emoji": "📊"},
    {"name": "Tools",        "file": "tests/test_tools.py",        "flag": "--tools", "emoji": "🔧"},
    {"name": "Topic Guard",  "file": "tests/test_topic_guard.py",  "flag": "--guard", "emoji": "🛡️"},
    {"name": "Market Hours", "file": "tests/test_market_hours.py", "flag": "--hours", "emoji": "🕐"},
    {"name": "LLM Responses","file": "tests/test_llm.py",         "flag": "--llm",   "emoji": "🤖"},
]


def print_banner():
    print(f"\n{Fore.CYAN}╔══════════════════════════════════════════════════╗")
    print(f"║   {Fore.WHITE}🇮🇳 Indian Stock Market AI Assistant{Fore.CYAN}           ║")
    print(f"║   {Fore.WHITE}Complete Test Suite{Fore.CYAN}                            ║")
    print(f"║   {Fore.WHITE}{time.strftime('%d %b %Y, %I:%M %p')}{Fore.CYAN}                       ║")
    print(f"╚══════════════════════════════════════════════════╝{Style.RESET_ALL}\n")


def run_category(cat: dict, index: int, total: int) -> dict:
    """Run a single test category and return results."""
    name = cat["name"]
    emoji = cat["emoji"]
    filepath = cat["file"]

    print(f"  [{index}/{total}] {emoji} Testing {name}...", end=" ", flush=True)
    start = time.time()

    cmd = [
        sys.executable, "-m", "pytest",
        filepath,
        "-v", "--tb=short", "--no-header", "-q",
        "--timeout=45",
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            timeout=300,
        )
        output = result.stdout + result.stderr
        elapsed = round(time.time() - start, 1)
    except subprocess.TimeoutExpired:
        elapsed = round(time.time() - start, 1)
        print(f"{Fore.RED}TIMEOUT ({elapsed}s){Style.RESET_ALL}")
        return {
            "name": name, "total": 0, "passed": 0, "failed": 1,
            "skipped": 0, "time": elapsed, "tests": [
                {"name": "timeout", "status": "failed",
                 "message": "Category timed out after 300s", "time": elapsed}
            ]
        }

    # Parse individual test lines
    tests = []
    for line in output.split("\n"):
        line = line.strip()
        if "PASSED" in line:
            test_name = line.split("::")[1].split(" ")[0] if "::" in line else line
            tests.append({"name": test_name, "status": "passed", "message": "", "time": 0})
        elif "FAILED" in line:
            test_name = line.split("::")[1].split(" ")[0] if "::" in line else line
            tests.append({"name": test_name, "status": "failed", "message": line, "time": 0})
        elif "SKIPPED" in line:
            test_name = line.split("::")[1].split(" ")[0] if "::" in line else line
            # Extract skip reason
            reason = ""
            reason_match = re.search(r"SKIPPED\s*\((.+?)\)", line) or re.search(r"SKIPPED.*?-\s*(.+)", line)
            if reason_match:
                reason = reason_match.group(1)
            tests.append({"name": test_name, "status": "skipped", "message": reason or "Skipped", "time": 0})

    # Parse the summary line (e.g. "5 passed, 1 failed, 2 skipped in 3.2s")
    p, f, s = 0, 0, 0
    for line in output.split("\n"):
        pm = re.search(r"(\d+) passed", line)
        fm = re.search(r"(\d+) failed", line)
        sm = re.search(r"(\d+) skipped", line)
        if pm:
            p = max(p, int(pm.group(1)))
        if fm:
            f = max(f, int(fm.group(1)))
        if sm:
            s = max(s, int(sm.group(1)))

    total_tests = p + f + s

    # Status display
    parts = []
    if p > 0:
        parts.append(f"{Fore.GREEN}{p} passed ✅")
    if f > 0:
        parts.append(f"{Fore.RED}{f} failed ❌")
    if s > 0:
        parts.append(f"{Fore.YELLOW}{s} skipped ⏭️")

    status_str = ", ".join(parts) if parts else f"{Fore.GREEN}0 tests"
    print(f"{status_str}{Style.RESET_ALL} ({elapsed}s)")

    return {
        "name": name, "total": total_tests, "passed": p, "failed": f,
        "skipped": s, "time": elapsed, "tests": tests,
    }


def get_data_source_health(categories_results):
    """Determine health status based on test results."""
    health = {}

    ds = next((c for c in categories_results if c["name"] == "Data Sources"), None)
    tools = next((c for c in categories_results if c["name"] == "Tools"), None)
    llm = next((c for c in categories_results if c["name"] == "LLM Responses"), None)

    # yfinance
    yf_ok = ds and ds["passed"] > 0 if ds else False
    health["yfinance"] = {"ok": yf_ok, "label": "Working (15 min delay)" if yf_ok else "Not working"}

    # NSE India
    nse_ok = ds and ds["passed"] >= 4 if ds else False
    health["NSE India API"] = {"ok": nse_ok, "label": "Working" if nse_ok else "Rate-limited or down"}

    # Angel One
    angel_tests = [t for t in (ds["tests"] if ds else []) if "angel" in t["name"].lower()]
    angel_skipped = all(t["status"] == "skipped" for t in angel_tests) if angel_tests else True
    angel_ok = any(t["status"] == "passed" for t in angel_tests)
    if angel_skipped:
        health["Angel One"] = {"ok": False, "label": "Not configured (skipped)"}
    elif angel_ok:
        health["Angel One"] = {"ok": True, "label": "Connected"}
    else:
        health["Angel One"] = {"ok": False, "label": "Login failed"}

    # News Sources
    try:
        from tools.news import check_news_health
        news_health = check_news_health()
        
        if "MoneyControl" in news_health:
            health["MoneyControl RSS"] = {
                "ok": news_health["MoneyControl"].get("working", False),
                "label": news_health["MoneyControl"].get("status", "Unknown")
            }
        if "Economic Times" in news_health:
            health["Economic Times RSS"] = {
                "ok": news_health["Economic Times"].get("working", False),
                "label": news_health["Economic Times"].get("status", "Unknown")
            }
        if "Yahoo Finance" in news_health:
            health["Yahoo Finance News"] = {
                "ok": news_health["Yahoo Finance"].get("working", False),
                "label": news_health["Yahoo Finance"].get("status", "Unknown")
            }
        if "_overall" in news_health:
            health["Overall News"] = {
                "ok": news_health["_overall"].get("sources_working", 0) > 0,
                "label": news_health["_overall"].get("status", "Unknown")
            }
    except Exception as e:
        health["News Sources"] = {"ok": False, "label": f"Health check failed: {e}"}

    # Groq LLM
    if llm:
        health["Groq LLM"] = {"ok": llm["passed"] > 0, "label": "Working" if llm["passed"] > 0 else "Not working"}
    else:
        health["Groq LLM"] = {"ok": False, "label": "Not tested"}

    return health


def get_recommendations(categories_results, health):
    """Generate fix recommendations for failed tests."""
    recs = []
    for cat in categories_results:
        if cat["failed"] > 0:
            for t in cat.get("tests", []):
                if t["status"] == "failed":
                    name = t["name"].lower()
                    if "angel" in name:
                        recs.append("Angel One: Check ANGEL_TOTP_SECRET in .env — enable TOTP in Angel One app.")
                    elif "yfinance" in name or "stock_price" in name:
                        recs.append("yfinance: Check internet. Try: pip install yfinance --upgrade")
                    elif "nse" in name or "indices" in name or "gainers" in name:
                        recs.append("NSE India: NSE may be rate-limiting. Try again in a few seconds.")
                    elif "llm" in name or "groq" in name or "disclaimer" in name:
                        recs.append("Groq LLM: Check GROQ_API_KEY in .env. Verify at console.groq.com")
                    elif "topic" in name or "guard" in name:
                        recs.append("Topic Guard: Check utils/topic_guard.py keyword logic.")
    return list(set(recs))


def main():
    parser = argparse.ArgumentParser(description="Run stock assistant tests")
    parser.add_argument("--data", action="store_true", help="Data sources only")
    parser.add_argument("--tools", action="store_true", help="Tools only")
    parser.add_argument("--llm", action="store_true", help="LLM only")
    parser.add_argument("--guard", action="store_true", help="Topic guard only")
    parser.add_argument("--hours", action="store_true", help="Market hours only")
    parser.add_argument("--quick", action="store_true", help="Skip LLM tests")
    parser.add_argument("--no-report", action="store_true", help="Skip HTML report")
    args = parser.parse_args()

    print_banner()

    # Determine which categories to run
    selected_flags = {
        "--data": args.data, "--tools": args.tools, "--llm": args.llm,
        "--guard": args.guard, "--hours": args.hours,
    }
    any_selected = any(selected_flags.values())

    cats_to_run = []
    for cat in TEST_CATEGORIES:
        if args.quick and cat["flag"] == "--llm":
            continue
        if any_selected and not selected_flags.get(cat["flag"], False):
            continue
        cats_to_run.append(cat)

    print(f"  Running {len(cats_to_run)} test categories...\n")
    start_all = time.time()

    results = []
    for i, cat in enumerate(cats_to_run, 1):
        r = run_category(cat, i, len(cats_to_run))
        results.append(r)

    total_time = round(time.time() - start_all, 1)

    # Aggregate
    total_tests = sum(r["total"] for r in results)
    total_passed = sum(r["passed"] for r in results)
    total_failed = sum(r["failed"] for r in results)
    total_skipped = sum(r["skipped"] for r in results)

    # Score excludes skipped tests
    configured_tests = total_tests - total_skipped
    score = (total_passed / configured_tests * 100) if configured_tests > 0 else 0

    # Print summary
    print(f"\n{'━' * 50}")
    for r in results:
        icon = f"{Fore.GREEN}✅" if r["failed"] == 0 else f"{Fore.RED}⚠️"
        skip_note = f" ({r['skipped']} skipped)" if r['skipped'] > 0 else ""
        print(f"  {icon} {r['name']:20s}: {r['passed']}/{r['total']} passed{skip_note}{Style.RESET_ALL}")
    print(f"{'━' * 50}")

    print(f"  {Fore.GREEN}✅ Passed   : {total_passed}{Style.RESET_ALL}")
    if total_failed > 0:
        print(f"  {Fore.RED}❌ Failed   : {total_failed}{Style.RESET_ALL}")
    else:
        print(f"  {Fore.GREEN}❌ Failed   : 0{Style.RESET_ALL}")
    if total_skipped > 0:
        print(f"  {Fore.YELLOW}⏭️  Skipped  : {total_skipped}  (credentials not configured){Style.RESET_ALL}")

    score_color = Fore.GREEN if score >= 95 else (Fore.YELLOW if score >= 70 else Fore.RED)
    print(f"  {score_color}🎯 Score    : {score:.1f}% ({total_passed}/{configured_tests} configured tests){Style.RESET_ALL}")
    print(f"  {Fore.WHITE}⏱️  Time     : {total_time}s")

    # Show skipped test details
    if total_skipped > 0:
        print(f"\n  {Fore.YELLOW}⏭️  {total_skipped} test(s) skipped — credentials not configured")
        print(f"     To enable: Set Angel One credentials in .env file")
        print(f"     These will automatically run once configured{Style.RESET_ALL}")

    # Generate HTML report
    if not args.no_report:
        try:
            from tests.test_report import generate_html_report

            health = get_data_source_health(results)
            recs = get_recommendations(results, health)

            report_data = {
                "total": total_tests,
                "passed": total_passed,
                "failed": total_failed,
                "skipped": total_skipped,
                "score": score,
                "total_time": total_time,
                "categories": results,
                "data_source_health": health,
                "recommendations": recs,
            }
            report_path = generate_html_report(report_data)
            print(f"  {Fore.CYAN}📄 Report   : {report_path}{Style.RESET_ALL}")

            try:
                webbrowser.open(f"file:///{os.path.abspath(report_path)}")
            except Exception:
                pass
        except Exception as e:
            print(f"  {Fore.YELLOW}⚠️ Report generation failed: {e}{Style.RESET_ALL}")

    print(f"{'━' * 50}")

    # Final verdict
    if total_failed == 0 and score >= 95:
        print(f"\n  {Fore.GREEN}🎉 PERFECT SCORE on configured tests!")
        print(f"     Ready for production / Angel One demo!{Style.RESET_ALL}")
    elif score >= 90:
        print(f"\n  {Fore.GREEN}🎉 EXCELLENT! Score: {score:.1f}%{Style.RESET_ALL}")
    elif score >= 70:
        print(f"\n  {Fore.YELLOW}⚠️ GOOD but fix failing tests before demo{Style.RESET_ALL}")
    else:
        print(f"\n  {Fore.RED}❌ Several issues found. Check test_report.html{Style.RESET_ALL}")

    print()
    sys.exit(0 if total_failed == 0 else 1)


if __name__ == "__main__":
    main()
