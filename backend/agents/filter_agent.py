import json
from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
from backend.config import get_settings
from rich.console import Console

console = Console()
settings = get_settings()

# Keywords that indicate a senior/experienced role → hard discard
SENIOR_KEYWORDS = [
    "senior", "sr.", "lead", "principal", "director", "manager",
    "head of", "vp ", "vice president", "5+ years",
    "7+ years", "8+ years", "10+ years",
]

# Old batch years to discard
OLD_GRAD_YEARS = ["2020", "2021", "2022", "2023"]


def hard_filter(job: Dict[str, Any], grad_year: str) -> bool:
    """Returns True if job PASSES hard filters, False if it should be discarded."""
    title = job.get("title", "").lower()
    description = (job.get("raw_description") or "").lower()
    combined = title + " " + description

    # Hard filter 1: Discard senior/experienced roles
    for kw in SENIOR_KEYWORDS:
        if kw in title:
            return False

    # Hard filter 2: Discard explicitly old batch grad years
    for old_year in OLD_GRAD_YEARS:
        if f"{old_year} batch" in combined or f"batch of {old_year}" in combined:
            return False

    # Hard filter 3: If job explicitly mentions a DIFFERENT grad year
    job_grad_year = job.get("grad_year", "")
    if job_grad_year and grad_year not in job_grad_year:
        return False

    return True


async def run_filter_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Agent 2: Hard filter → LLM soft scoring → keep top jobs."""
    console.print("\n[bold blue]═══ Agent 2: Filter Agent ═══[/bold blue]")

    raw_jobs: List[Dict[str, Any]] = state.get("raw_jobs", [])
    profile = state.get("profile", {})

    grad_year = profile.get("grad_year", "2025")
    preferred_roles = profile.get("preferred_roles", "SDE")
    min_salary = profile.get("min_salary_lpa", 0)
    preferred_locations = profile.get("preferred_locations", "")
    preferred_work_mode = profile.get("preferred_work_mode", "")
    preferred_company_types = profile.get("preferred_company_types", "")
    threshold = profile.get("relevance_threshold", 5.0)

    # ── Step 1: Hard Filter ───────────────────────────────────────────────────
    passed_hard = [j for j in raw_jobs if hard_filter(j, grad_year)]
    discarded = len(raw_jobs) - len(passed_hard)
    console.print(
        f"[cyan]Hard filter: {len(raw_jobs)} → {len(passed_hard)} jobs "
        f"({discarded} discarded)[/cyan]"
    )

    if not passed_hard:
        console.print("[yellow]No jobs passed hard filter.[/yellow]")
        return {**state, "filtered_jobs": []}

    # ── Step 2: LLM Soft Scoring ──────────────────────────────────────────────
    if not settings.groq_api_key:
        console.print("[yellow]⚠️  No Groq key — skipping LLM scoring, passing all jobs[/yellow]")
        for job in passed_hard:
            job["relevance_score"] = 7.0
        return {**state, "filtered_jobs": passed_hard}

    llm = ChatGroq(
        api_key=settings.groq_api_key,
        model="llama-3.1-70b-versatile",
        temperature=0,
    )

    scored_jobs = []
    batch_size = 10

    for i in range(0, len(passed_hard), batch_size):
        batch = passed_hard[i : i + batch_size]
        jobs_text = "\n".join(
            f"{idx+1}. Title: {j['title']} | Company: {j['company']} "
            f"| Location: {j.get('location','?')} "
            f"| Work Mode: {j.get('work_mode','?')} "
            f"| Company Type: {j.get('company_type','?')}"
            for idx, j in enumerate(batch)
        )

        prompt = f"""You are scoring job listings for a college student.

Student Profile:
- Graduation Year: {grad_year}
- Preferred Roles: {preferred_roles}
- Minimum Salary: {min_salary} LPA
- Preferred Locations: {preferred_locations or 'Any'}
- Preferred Work Mode: {preferred_work_mode or 'Any'}
- Preferred Company Types: {preferred_company_types or 'Any'}

Score each job 0.0–10.0 based on:
- Role match (40%): How well does the title match preferred roles?
- Location match (20%): Does location match preference?
- Work mode match (15%): Does work mode match preference?
- Company type match (10%): Does company type match preference?
- General fit (15%): Is this entry-level/fresher-appropriate?

Jobs to score:
{jobs_text}

Respond ONLY with a JSON array of scores like: [7.5, 3.0, 8.2, ...]
No explanations, just the JSON array."""

        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            scores_raw = response.content.strip()
            start = scores_raw.find("[")
            end = scores_raw.rfind("]") + 1
            scores = json.loads(scores_raw[start:end])
            for j, score in zip(batch, scores):
                j["relevance_score"] = float(score)
                scored_jobs.append(j)
        except Exception as e:
            console.print(f"[red]LLM scoring error: {e} — defaulting to 6.0[/red]")
            for j in batch:
                j["relevance_score"] = 6.0
                scored_jobs.append(j)

    # ── Step 3: Apply Threshold ───────────────────────────────────────────────
    filtered = [j for j in scored_jobs if j.get("relevance_score", 0) >= threshold]
    filtered.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

    console.print(
        f"[green]✅ Filter Agent done: {len(filtered)} jobs scored ≥ {threshold} "
        f"(out of {len(scored_jobs)})[/green]"
    )

    return {**state, "filtered_jobs": filtered}
