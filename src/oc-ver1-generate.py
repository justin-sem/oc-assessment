'''
This approach is a simple baseline, oc-ver1:
- One model
- One prompt
- The complete raw company record
- No financial calculations outside the LLM
- No example summaries
- No second model checking the result
- No automatic retries or evaluation
'''

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "companies.jsonl"
OUTPUT_PATH = ROOT / "summaries" / "oc-ver1.jsonl"

MODEL_NAME = "gemini-3.5-flash-lite"

DEVELOPMENT_IDS = [
    "SYN-001102",  # Ordinary positive company
    "SYN-000217",  # Non-standard audit opinion
    "SYN-000148",  # Loss and negative operating cash flow
    "SYN-001070",  # Plaintiff and defendant litigation
    "SYN-001203",  # No financial data
    "SYN-001212",  # Winding up and litigation
]


def load_companies() -> dict[str, dict[str, Any]]:
    """Load the source JSONL file and index companies by registration number."""

    companies = {}

    with DATA_PATH.open(encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            company = json.loads(line)
            registration_number = company["registrationNumber"]
            companies[registration_number] = company

    return companies


def load_completed_ids() -> set[str]:
    """Return registration numbers already saved in the oc-ver1 output."""

    if not OUTPUT_PATH.exists():
        return set()

    completed_ids = set()

    with OUTPUT_PATH.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSON in {OUTPUT_PATH} on line {line_number}"
                ) from error

            completed_ids.add(row["registrationNumber"])

    return completed_ids


def build_prompt(company: dict[str, Any]) -> str:
    """Build the oc-ver1 prompt using the complete company record."""

    company_json = json.dumps(
        company,
        ensure_ascii=False,
        indent=2,
    )

    return f"""
Write a concise company summary for a team vetting potential
suppliers or project partners.

Requirements:
- Use only information from the supplied company record.
- Write approximately 100 to 180 words.
- Include the company's identity, business activity and status.
- Summarise important financial performance and trends when available.
- Mention material ownership, audit or litigation information when relevant.
- Clearly state when important information is unavailable.
- Do not make an approve or reject recommendation.
- Do not predict future performance.
- Return only the summary in readable Markdown.

Company record:

{company_json}
""".strip()


def generate_summary(
    client: genai.Client,
    company: dict[str, Any],
) -> str:
    """Call Gemini and return the generated summary."""

    prompt = build_prompt(company)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=400,
        ),
    )

    if not response.text:
        raise RuntimeError(
            f"Gemini returned no text for "
            f"{company['registrationNumber']}"
        )

    return response.text.strip()


def save_summary(
    output_file: Any,
    registration_number: str,
    summary: str,
) -> None:
    """Append one summary to the output JSONL file."""

    row = {
        "registrationNumber": registration_number,
        "summary": summary,
    }

    output_file.write(
        json.dumps(row, ensure_ascii=False) + "\n"
    )

    # Save immediately so completed responses survive a later API failure.
    output_file.flush()


def main() -> None:
    """Generate oc-ver1 summaries for the development sample."""

    load_dotenv(ROOT / ".env")

    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError(
            "GEMINI_API_KEY was not found in .env"
        )

    companies = load_companies()
    completed_ids = load_completed_ids()

    missing_ids = [
        registration_number
        for registration_number in DEVELOPMENT_IDS
        if registration_number not in companies
    ]

    if missing_ids:
        raise ValueError(
            f"Registration numbers not found: {missing_ids}"
        )

    client = genai.Client(
        http_options=types.HttpOptions(
            timeout=60_000,
        )
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open("a", encoding="utf-8") as output_file:
        for registration_number in DEVELOPMENT_IDS:
            if registration_number in completed_ids:
                print(
                    f"Skipping completed: {registration_number}",
                    flush=True,
                )
                continue

            company = companies[registration_number]

            print(
                f"Generating: {registration_number}",
                flush=True,
            )

            summary = generate_summary(
                client=client,
                company=company,
            )

            save_summary(
                output_file=output_file,
                registration_number=registration_number,
                summary=summary,
            )

            print(
                f"Saved {registration_number}: "
                f"{len(summary.split())} words",
                flush=True,
            )

    print()
    print(f"oc-ver1 output: {OUTPUT_PATH}")
    print("Generation complete.")


if __name__ == "__main__":
    main()
