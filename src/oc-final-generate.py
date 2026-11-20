'''
This version is the final version which will:
- Read experiments/oc-final-facts.jsonl
- Generate summaries for all 50 companies
- Ask Gemini only to write and translate—not calculate
- Bold every company name consistently
- Save each result immediately
- Retry temporary Gemini errors
- Resume safely if rerun
'''

"""
Generate the final company summaries.

The deterministic facts are prepared by build_facts.py.
Gemini is used only to select, translate and present those facts.
"""

import json
import os
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types


ROOT = Path(__file__).resolve().parent.parent

FACTS_PATH = (
    ROOT / "experiments" / "oc-final-facts.jsonl"
)

OUTPUT_PATH = (
    ROOT / "summaries" / "oc-final.jsonl"
)

MODEL_NAME = "gemini-3.5-flash-lite"

MAX_ATTEMPTS = 3


def load_fact_sheets() -> list[dict[str, Any]]:
    """Load the deterministic company fact sheets."""

    fact_sheets = []

    with FACTS_PATH.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSON in {FACTS_PATH} "
                    f"on line {line_number}"
                ) from error

            fact_sheets.append(row)

    return fact_sheets


def load_completed_ids() -> set[str]:
    """Load registration numbers already generated."""

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
                    f"Invalid JSON in {OUTPUT_PATH} "
                    f"on line {line_number}"
                ) from error

            completed_ids.add(row["registrationNumber"])

    return completed_ids


def build_prompt(facts: dict[str, Any]) -> str:
    """Build a prompt using only deterministic facts."""

    facts_json = json.dumps(
        facts,
        ensure_ascii=False,
        indent=2,
    )

    return f"""
Write a factual company summary for an internal team vetting
a potential supplier or project partner.

Use only the supplied fact sheet. All calculations, classifications,
trends and litigation statuses have already been determined. Do not
recalculate, reinterpret or contradict them.

Length and format:
- Write approximately 120 to 180 words.
- Begin with one short introductory paragraph.
- Start the paragraph with the exact company name in bold Markdown.
- Follow it with up to four concise bullet points.
- Use relevant bold labels such as **Ownership**, **Financials**,
  **Audit**, and **Litigation**.
- Do not add a title, table, recommendation or word count.
- End with a complete sentence.

Content:
- Introduce the company status, type, industry, listed state and stated
  nature of business.
- If the nature of business contains Malay wording, translate its
  meaning into natural English.
- Never translate or alter company names, legal names, registration
  numbers, case numbers or court names.
- Mention a former company name when one is provided.
- For ownership, use the supplied majority classification exactly.
- Do not call a shareholder controlling or a majority shareholder when
  `hasSingleMajorityShareholder` is false.
- When `hasSingleMajorityShareholder` is true, always state the supplied
  majority shareholder's name and percentage.
- When financial information is available, always state the exact
  earliest and latest revenue and profit-after-tax values together with
  their financial years. Then briefly describe their supplied trends.
- Mention the latest operating cash flow value when it is negative or
  otherwise materially relevant.
- Always mention a non-standard audit opinion.
- If litigation exists, always state the exact number of cases.
- If a largest claim is provided, always state its amount, exact status,
  and the company's role in that case.
- Preserve every litigation status exactly as supplied.
- When relevant, distinguish the largest claim from pending cases and
  judgments. Do not assume the largest claim is pending.
- A claim amount is not confirmed debt, loss or liability.
- Clearly state when financial information is unavailable.

Style and grounding:
- Use concise, neutral and professional language.
- Use the supplied formatted values without changing them.
- Refer to the company state only as "listed in".
- Do not describe the state as its headquarters, operating location or
  place of incorporation.
- Do not infer management quality, business stability, future
  performance or relationships between shareholders.
- Do not recommend approval, rejection, investment or cooperation.
- Do not add facts that are absent from the fact sheet.

Return only the completed Markdown summary.

Fact sheet:

{facts_json}
""".strip()


def ensure_bold_company_name(
    summary: str,
    company_name: str,
) -> str:
    """Ensure the first company-name occurrence is bold."""

    bold_name = f"**{company_name}**"

    if bold_name in summary:
        return summary

    return summary.replace(
        company_name,
        bold_name,
        1,
    )


def generate_summary(
    client: genai.Client,
    facts: dict[str, Any],
) -> str:
    """Generate one summary, retrying temporary API failures."""

    registration_number = facts["registrationNumber"]
    company_name = facts["companyName"]
    prompt = build_prompt(facts)

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=700,
                ),
            )

            if not response.text:
                raise RuntimeError(
                    "Gemini returned an empty response"
                )

            summary = response.text.strip()

            return ensure_bold_company_name(
                summary=summary,
                company_name=company_name,
            )

        except Exception as error:
            if attempt == MAX_ATTEMPTS:
                raise RuntimeError(
                    f"Generation failed for "
                    f"{registration_number}"
                ) from error

            wait_seconds = attempt * 10

            print(
                f"Attempt {attempt} failed for "
                f"{registration_number}: {error}",
                flush=True,
            )
            print(
                f"Retrying in {wait_seconds} seconds...",
                flush=True,
            )

            time.sleep(wait_seconds)

    raise RuntimeError("Unexpected generation failure")


def save_summary(
    output_file: Any,
    registration_number: str,
    summary: str,
) -> None:
    """Append one completed summary to the JSONL output."""

    row = {
        "registrationNumber": registration_number,
        "summary": summary,
    }

    output_file.write(
        json.dumps(row, ensure_ascii=False) + "\n"
    )
    output_file.flush()


def main() -> None:
    """Generate final summaries for all companies."""

    load_dotenv(ROOT / ".env")

    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError(
            "GEMINI_API_KEY was not found in .env"
        )

    fact_sheets = load_fact_sheets()
    completed_ids = load_completed_ids()

    print(
        f"Loaded {len(fact_sheets)} fact sheets.",
        flush=True,
    )
    print(
        f"Already completed: {len(completed_ids)}",
        flush=True,
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

    with OUTPUT_PATH.open(
        "a",
        encoding="utf-8",
    ) as output_file:
        for row in fact_sheets:
            registration_number = row["registrationNumber"]
            facts = row["facts"]

            if registration_number in completed_ids:
                print(
                    f"Skipping completed: "
                    f"{registration_number}",
                    flush=True,
                )
                continue

            print(
                f"Generating: {registration_number}",
                flush=True,
            )

            summary = generate_summary(
                client=client,
                facts=facts,
            )

            save_summary(
                output_file=output_file,
                registration_number=registration_number,
                summary=summary,
            )

            word_count = len(summary.split())

            print(
                f"Saved {registration_number}: "
                f"{word_count} words",
                flush=True,
            )

            if not 100 <= word_count <= 200:
                print(
                    "  Warning: summary is outside the "
                    "preferred word-count range.",
                    flush=True,
                )

    print()
    print(f"Final output: {OUTPUT_PATH}")
    print("Generation complete.")


if __name__ == "__main__":
    main()