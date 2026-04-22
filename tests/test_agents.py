import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.rag_agent import run_rag_agent
from agents.sql_agent import run_sql_agent

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


def run_test(name, query, agent_fn, keywords, use_or=False):
    print(f"\n--- [{name}] ---")
    print(f"Query:   {query}")
    t0 = time.time()
    try:
        result = agent_fn(query)
        latency = time.time() - t0
        lower = result.lower()
        if use_or:
            passed = any(kw in lower for kw in keywords)
        else:
            passed = all(kw in lower for kw in keywords)
        answer_preview = result[:200] + "..." if len(result) > 200 else result
        print(f"Answer:  {answer_preview}")
        print(f"Latency: {latency:.2f}s")
        status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
        print(f"Result:  {status}")
        return {"name": name, "passed": passed, "latency": latency}
    except Exception as e:
        latency = time.time() - t0
        print(f"Answer:  <ERROR: {e}>")
        print(f"Latency: {latency:.2f}s")
        print(f"Result:  {RED}ERROR{RESET}")
        return {"name": name, "passed": False, "latency": latency}


def run_rag_suite():
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}RAG AGENT TESTS  (Policy Documents){RESET}")
    print(f"{BOLD}{'='*60}{RESET}")

    cases = [
        ("rag_return_policy",
         "What is the return policy?",
         ["return", "day"],
         False),
        ("rag_shipping_timeframe",
         "How long does shipping take?",
         ["day", "ship"],
         False),
        ("rag_privacy_data_collection",
         "What personal data do you collect?",
         ["data", "collect"],
         False),
        # OR logic — LLM may answer from general knowledge; this test is inherently flaky
        ("rag_out_of_scope",
         "What is the capital of France?",
         ["don't know", "not"],
         True),
    ]

    results = []
    for name, query, keywords, use_or in cases:
        results.append(run_test(name, query, run_rag_agent, keywords, use_or))
    return results


def run_sql_suite():
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}SQL AGENT TESTS  (Customer Database){RESET}")
    print(f"{BOLD}{'='*60}{RESET}")

    cases = [
        ("sql_customer_count",
         "How many customers are there?",
         ["4"],
         False),
        ("sql_alice_email",
         "What is Alice's email address?",
         ["alice@example.com"],
         False),
        ("sql_youngest_customer",
         "Who is the youngest customer?",
         ["bob"],
         False),
        ("sql_average_age",
         "What is the average age of all customers?",
         ["27", "28"],
         True),  # OR: (30+25+28+32)/4 = 28.75 — LLM may say "28" or "28.75"
        ("sql_ema_profile_and_tickets",
         "Give me a quick overview of customer Ema's profile and past support ticket details.",
         ["ema", "shipping", "damaged"],
         False),
    ]

    results = []
    for name, query, keywords, use_or in cases:
        results.append(run_test(name, query, run_sql_agent, keywords, use_or))
    return results


def print_summary(rag_results, sql_results):
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}SUMMARY{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")

    header = f"{'Agent':<8}  {'Tests':<6}  {'Passed':<7}  {'Failed':<7}  {'Pass Rate':<10}  {'Avg Latency'}"
    print(header)
    print("-" * 60)

    all_results = []
    for label, results in [("RAG", rag_results), ("SQL", sql_results)]:
        total = len(results)
        passed = sum(1 for r in results if r["passed"])
        failed = total - passed
        rate = f"{passed/total*100:.1f}%" if total else "n/a"
        avg_lat = f"{sum(r['latency'] for r in results)/total:.2f}s" if total else "n/a"
        print(f"{label:<8}  {total:<6}  {passed:<7}  {failed:<7}  {rate:<10}  {avg_lat}")
        all_results.extend(results)

    print("-" * 60)
    total = len(all_results)
    passed = sum(1 for r in all_results if r["passed"])
    failed = total - passed
    rate = f"{passed/total*100:.1f}%" if total else "n/a"
    avg_lat = f"{sum(r['latency'] for r in all_results)/total:.2f}s" if total else "n/a"
    print(f"{'Total':<8}  {total:<6}  {passed:<7}  {failed:<7}  {rate:<10}  {avg_lat}")
    print(f"{BOLD}{'='*60}{RESET}")

    return passed == total


if __name__ == "__main__":
    rag_results = run_rag_suite()
    sql_results = run_sql_suite()
    all_passed = print_summary(rag_results, sql_results)
    sys.exit(0 if all_passed else 1)
