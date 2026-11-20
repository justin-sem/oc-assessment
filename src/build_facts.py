import json
from collections import Counter
from pathlib import Path
from typing import Any
from itertools import pairwise

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "companies.jsonl"
FACTS_PATH = ROOT / "experiments" / "oc-final-facts.jsonl"



def format_rm(value: int | float) -> str:
    """Format a monetary value consistently in Malaysian ringgit."""

    if float(value).is_integer():
        return f"RM{value:,.0f}"

    return f"RM{value:,.2f}"


def format_percentage(value: float) -> str:
    """Format a percentage without unnecessary trailing zeros."""

    return f"{value:g}%"


def format_ratio(value: float | None) -> float | None:
    """Round a ratio while preserving missing values."""

    if value is None:
        return None

    return round(value, 4)


def describe_trend(values: list[int | float]) -> str:
    """Describe whether a sequence rises, falls, stays flat or fluctuates."""

    if len(values) < 2:
        return "single_year_only"

    differences = [
        current - previous
        for previous, current in pairwise(values)
    ]

    if all(change > 0 for change in differences):
        return "increased_each_available_year"

    if all(change < 0 for change in differences):
        return "decreased_each_available_year"

    if all(change == 0 for change in differences):
        return "unchanged"

    return "fluctuated"


def describe_profit_change(
    earliest: int | float,
    latest: int | float,
) -> str:
    """Describe profit movement without confusing negative values."""

    if earliest < 0 and latest < 0:
        if latest < earliest:
            return "loss_widened"
        if latest > earliest:
            return "loss_narrowed"
        return "loss_unchanged"

    if earliest >= 0 and latest < 0:
        return "moved_from_profit_to_loss"

    if earliest < 0 and latest >= 0:
        return "moved_from_loss_to_profit"

    if latest > earliest:
        return "profit_increased"

    if latest < earliest:
        return "profit_decreased"

    return "profit_unchanged"


def load_companies() -> list[dict[str, Any]]:
    """Load all company records from the source JSONL file."""

    companies = []

    with DATA_PATH.open(encoding="utf-8") as file:
        for line in file:
            if line.strip():
                companies.append(json.loads(line))

    return companies


def normalise_shareholder(
    shareholder: dict[str, Any],
    director_names: set[str],
) -> dict[str, Any]:
    """Create a concise shareholder record."""

    result = {
        "name": shareholder["name"],
        "type": shareholder["type"],
        "percentage": format_percentage(
            shareholder["percentage"]
        ),
        "percentageValue": shareholder["percentage"],
        "isAlsoDirector": shareholder["name"] in director_names,
    }

    if shareholder["type"] == "company":
        result["registrationNumber"] = shareholder.get(
            "registrationNumber"
        )
        result["incorporatedIn"] = shareholder.get(
            "incorporatedIn"
        )

    return result


def build_ownership_facts(
    company: dict[str, Any],
) -> dict[str, Any]:
    """Calculate ownership facts without asking the LLM to compare values."""

    directors = company["relationships"]["directors"]
    shareholders = company["relationships"]["shareholders"]

    director_names = {
        director["name"]
        for director in directors
    }

    normalised = [
        normalise_shareholder(
            shareholder,
            director_names,
        )
        for shareholder in shareholders
    ]

    sorted_shareholders = sorted(
        normalised,
        key=lambda shareholder: shareholder["percentageValue"],
        reverse=True,
    )

    majority_shareholders = [
        shareholder
        for shareholder in sorted_shareholders
        if shareholder["percentageValue"] > 50
    ]

    corporate_shareholders = [
        shareholder
        for shareholder in sorted_shareholders
        if shareholder["type"] == "company"
    ]

    return {
        "directorCount": len(directors),
        "shareholderCount": len(shareholders),
        "hasSingleMajorityShareholder": bool(
            majority_shareholders
        ),
        "majorityShareholder": (
            majority_shareholders[0]
            if majority_shareholders
            else None
        ),
        "largestShareholders": sorted_shareholders[:2],
        "corporateShareholders": corporate_shareholders,
    }


def summarise_financial_year(
    year: dict[str, Any],
) -> dict[str, Any]:
    """Extract relevant financial facts for one year."""

    statements = year["statements"]
    ratios = year["ratiosAndMetrics"]

    profitability = ratios["profitability"]
    liquidity = ratios["liquidityAndCashFlow"]
    capital = ratios["capitalStructure"]

    net_margin = profitability["netProfitMargin"]

    return {
        "financialYear": year["financialYear"],
        "financialYearEnd": year["financialYearEnd"],
        "revenue": format_rm(statements["revenue"]),
        "revenueValue": statements["revenue"],
        "profitAfterTax": format_rm(
            statements["profitAfterTax"]
        ),
        "profitAfterTaxValue": statements["profitAfterTax"],
        "operatingCashFlow": format_rm(
            statements["operatingCashFlow"]
        ),
        "operatingCashFlowValue": (
            statements["operatingCashFlow"]
        ),
        "cash": format_rm(statements["cash"]),
        "borrowings": format_rm(statements["borrowings"]),
        "totalAssets": format_rm(statements["totalAssets"]),
        "totalLiabilities": format_rm(
            statements["totalLiabilities"]
        ),
        "totalEquity": format_rm(statements["totalEquity"]),
        "netProfitMargin": (
            f"{net_margin:.1%}"
            if net_margin is not None
            else None
        ),
        "quickRatio": format_ratio(
            liquidity["quickRatio"]
        ),
        "freeCashFlow": format_rm(
            liquidity["freeCashFlow"]
        ),
        "leverageRatio": format_ratio(
            capital["leverageRatio"]
        ),
        "debtServiceCoverageRatio": format_ratio(
            capital["debtServiceCoverageRatio"]
        ),
        "auditFirm": year["audit"]["firm"],
        "auditOpinion": year["audit"]["opinion"],
    }


def build_financial_facts(
    company: dict[str, Any],
) -> dict[str, Any]:
    """Calculate financial trends and risk indicators."""

    raw_years = sorted(
        company["financials"]["years"],
        key=lambda year: year["financialYear"],
    )

    if not raw_years:
        return {
            "available": False,
            "reason": "No financial years are provided.",
        }

    years = [
        summarise_financial_year(year)
        for year in raw_years
    ]

    earliest = years[0]
    latest = years[-1]

    revenue_values = [
        year["revenueValue"]
        for year in years
    ]
    profit_values = [
        year["profitAfterTaxValue"]
        for year in years
    ]
    cash_flow_values = [
        year["operatingCashFlowValue"]
        for year in years
    ]
    leverage_values = [
        year["leverageRatio"]
        for year in years
        if year["leverageRatio"] is not None
    ]

    audits = [
        {
            "financialYear": year["financialYear"],
            "firm": year["auditFirm"],
            "opinion": year["auditOpinion"],
        }
        for year in years
    ]

    non_standard_audits = [
        audit
        for audit in audits
        if audit["opinion"] != "Unqualified"
    ]

    return {
        "available": True,
        "yearCount": len(years),
        "earliestYear": earliest,
        "latestYear": latest,
        "trends": {
            "revenue": describe_trend(revenue_values),
            "profitAfterTax": describe_trend(
                profit_values
            ),
            "profitInterpretation": describe_profit_change(
                profit_values[0],
                profit_values[-1],
            ),
            "operatingCashFlow": describe_trend(
                cash_flow_values
            ),
            "leverage": describe_trend(
                leverage_values
            ),
        },
        "latestRiskIndicators": {
            "latestYearLoss": (
                latest["profitAfterTaxValue"] < 0
            ),
            "latestNegativeOperatingCashFlow": (
                latest["operatingCashFlowValue"] < 0
            ),
            "quickRatioBelowOne": (
                latest["quickRatio"] is not None
                and latest["quickRatio"] < 1
            ),
            "debtServiceCoverageBelowOne": (
                latest["debtServiceCoverageRatio"] is not None
                and latest["debtServiceCoverageRatio"] < 1
            ),
            "negativeEquity": (
                raw_years[-1]["statements"]["totalEquity"] < 0
            ),
        },
        "audits": audits,
        "nonStandardAudits": non_standard_audits,
    }


def normalise_case(case: dict[str, Any]) -> dict[str, Any]:
    """Create a concise litigation record with exact values."""

    return {
        "caseNumber": case["caseNumber"],
        "role": case["role"],
        "caseType": case["caseType"],
        "court": case["court"],
        "filedOn": case["filedOn"],
        "status": case["status"],
        "claimAmount": format_rm(case["claimAmount"]),
        "claimAmountValue": case["claimAmount"],
    }


def build_litigation_facts(
    company: dict[str, Any],
) -> dict[str, Any]:
    """Calculate exact litigation counts and select material cases."""

    cases = [
        normalise_case(case)
        for case in company["litigation"]["cases"]
    ]

    if not cases:
        return {
            "caseCount": 0,
            "roleCounts": {},
            "statusCounts": {},
            "largestClaimCase": None,
            "pendingCases": [],
            "judgmentCases": [],
            "allCases": [],
        }

    largest_claim_case = max(
        cases,
        key=lambda case: case["claimAmountValue"],
    )

    return {
        "caseCount": len(cases),
        "roleCounts": dict(
            Counter(case["role"] for case in cases)
        ),
        "statusCounts": dict(
            Counter(case["status"] for case in cases)
        ),
        "largestClaimCase": largest_claim_case,
        "pendingCases": [
            case
            for case in cases
            if case["status"] == "Pending"
        ],
        "judgmentCases": [
            case
            for case in cases
            if case["status"] == "Judgment entered"
        ],
        "allCases": cases,
    }


def build_fact_sheet(
    company: dict[str, Any],
) -> dict[str, Any]:
    """Build a verified fact sheet for one company."""

    profile = company["profile"]


    return {
        "registrationNumber": company["registrationNumber"],
        "companyName": profile["companyName"],
        "status": profile["status"],
        "companyType": profile["companyType"],
        "incorporationDate": profile["incorporationDate"],
        "industry": profile["industry"],
        "listedState": profile["state"],
        "natureOfBusiness": profile["natureOfBusiness"],
        "shareCapital": format_rm(profile["shareCapital"]),
        "formerNames": profile["formerNames"],
        "ownership": build_ownership_facts(company),
        "financials": build_financial_facts(company),
        "litigation": build_litigation_facts(company),
    }


def main() -> None:
    """Build deterministic fact sheets for all companies."""

    companies = load_companies()

    FACTS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with FACTS_PATH.open("w", encoding="utf-8") as file:
        for company in companies:
            row = {
                "registrationNumber": (
                    company["registrationNumber"]
                ),
                "facts": build_fact_sheet(company),
            }

            file.write(
                json.dumps(
                    row,
                    ensure_ascii=False,
                )
                + "\n"
            )

    print(
        f"Created {len(companies)} fact sheets at "
        f"{FACTS_PATH}"
    )


if __name__ == "__main__":
    main()