'''
This approach is a improve version of baseline model, oc-ver2:
- updated prompt scripting
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
OUTPUT_PATH = ROOT / "summaries" / "oc-ver2.jsonl"

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
    """Build the Version 2 prompt using the complete company record."""

    company_json = json.dumps(
        company,
        ensure_ascii=False,
        indent=2,
    )

    return f"""
Write a factual company summary for an internal team vetting
potential suppliers or project partners.

Write approximately 140 to 180 words in readable Markdown.

Format:
- Begin with one or two sentences describing the company, its status,
  industry, listed state and business activity.
- Follow with up to four bullet points using relevant bold labels such
  as **Ownership**, **Financials**, **Audit**, and **Litigation**.
- Each bullet may contain up to three concise sentences.
- Do not use a title or table.
- Ensure the final response ends with a complete sentence.

Coverage:
- Include revenue, profit after tax and operating cash-flow trends when
  financial information is available.
- Compare the earliest and latest available years, adding an
  intermediate year only when it reveals an important change.
- Mention latest liquidity, leverage, borrowings or cash when materially
  relevant.
- Always mention a non-standard audit opinion.
- Mention majority or corporate ownership, but do not list every
  shareholder unless necessary.
- If litigation exists, state the number of cases and distinguish the
  company's plaintiff and defendant roles.
- For multiple litigation cases, prioritise pending cases, judgments
  entered and the largest claim amount.
- Do not omit the case with the largest claim amount.
- Clearly state when financial information is unavailable.

Grounding:
- Use only facts contained in the supplied company record.
- Treat `profile.state` only as the listed state. Never describe it as
  the place of incorporation, headquarters or operating location.
- Do not transfer a shareholder's `incorporatedIn` value to the company.
- Keep separate location fields separate, even if they appear
  inconsistent.
- Do not infer that shareholders act together. Only describe a
  shareholder as having majority control when that shareholder
  individually owns more than 50%.
- An empty list means no records are provided for that section.
- Do not describe an empty former-names list as unavailable information.
- Prefix every monetary amount with RM.
- A litigation claim amount is not confirmed debt or loss.
- Report a case status exactly as provided. Do not infer the terms or
  outcome of a settlement.
- Do not assess management quality, predict future performance, or
  issue an approve/reject recommendation.

- Always include the company's stated nature of business in the opening.
- Refer to `profile.state` only using the wording "listed in".
- Never replace "listed in" with "based in", "located in" or
  "incorporated in".
- If one shareholder owns more than 50%, mention only that controlling
  shareholder and percentage unless another ownership relationship is
  materially important.
- Prioritise financial-risk indicators over minority shareholder details.
- If the latest quick ratio or debt-service coverage ratio is below 1,
  mention the most relevant ratio.
- If leverage has materially increased across the available years,
  mention that trend when space permits.
- Format RM amounts with comma separators and no unnecessary decimal
  places, for example `RM22,500` rather than `RM22500.0`.
  
Return only the completed summary.

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
            max_output_tokens=700,
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
    """Generate summaries for the development sample."""

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
    print(f"oc-ver2 output: {OUTPUT_PATH}")
    print("Generation complete.")


if __name__ == "__main__":
    main()