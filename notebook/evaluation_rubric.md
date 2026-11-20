# Company Summary Evaluation Rubric

## Purpose

This rubric evaluates whether a generated company summary is factual, relevant, concise and useful to a team vetting potential suppliers or project partners.

Each criterion is scored from 0 to 2, giving a maximum score of 10.

## Evaluation Criteria

| Criterion | 0 — Poor | 1 — Acceptable | 2 — Strong |
|---|---|---|---|
| Factual accuracy | Contains a material contradiction, incorrect figure or unsupported claim | Mostly accurate but contains a minor factual or interpretation issue | All claims and figures are supported by the company record |
| Material coverage | Omits multiple important facts or risks | Covers most important information but misses one useful point | Covers the most decision-relevant information for that company |
| Relevance | Generic, overly detailed or focused on information that does not support company vetting | Mostly relevant but contains some unnecessary information | Prioritises information useful for deciding whether closer review is required |
| Clarity and conciseness | Difficult to understand, poorly structured or excessively long | Understandable but could be clearer or shorter | Clear, well organised and understandable within approximately one minute |
| Calibrated language | Presents uncertainty, allegations or indicators as confirmed conclusions | Generally careful but uses slightly strong or ambiguous wording | Clearly distinguishes facts, indicators, missing information and uncertain outcomes |

## Material Factual Error Rule

A summary containing a material factual error is considered unsuccessful regardless of its total score.

Material errors include:

- Using the wrong company name or registration number
- Describing a winding-up company as active
- Claiming that financial information exists when it is unavailable
- Describing a profitable company as loss-making, or vice versa
- Reporting an incorrect financial amount or trend
- Describing a plaintiff as a defendant, or vice versa
- Presenting a litigation claim amount as confirmed debt or loss
- Reporting an incorrect audit opinion
- Inventing facts, risks or conclusions that are not supported by the record

## Material Coverage Guidance

The following information is generally relevant:

- Company name and registration number
- Business activity or industry
- Company status
- Latest financial performance
- Multi-year financial trend, when available

The following should be included when noteworthy:

- Missing financial information
- Losses or declining profitability
- Negative operating cash flow
- Material liquidity or leverage concerns
- Non-standard audit opinions
- Winding-up status
- Material or ongoing litigation
- Majority ownership or significant director-shareholder relationships

Not every available field needs to appear. The summary should prioritise information that helps the reader decide whether closer review is required.

## Format Checks

Each generated summary should:

- Match a registration number in the source dataset
- Contain approximately 100–180 words
- Use valid and readable Markdown
- Avoid incomplete sentences and placeholders
- Avoid issuing an approve or reject recommendation
- Clearly state when important information is unavailable
- Avoid predicting future company performance
- Avoid assessing management quality without supporting evidence

## Score Interpretation

| Total score | Interpretation |
|---:|---|
| 9–10 | Strong summary |
| 7–8 | Good summary with minor improvements needed |
| 5–6 | Weak summary requiring meaningful improvement |
| 0–4 | Poor summary |

A material factual error overrides the total score and results in an unsuccessful summary.

## Evaluation Process

For each company:

1. Read the company record.
2. Identify the most material facts and risks.
3. Read the generated summary.
4. Complete the format checks.
5. Score each criterion from 0 to 2.
6. Record any factual errors, omissions or unnecessary details.
7. Explain briefly what should be improved.

## Scoring Sheet

| Registration number | Version | Accuracy | Coverage | Relevance | Clarity | Calibration | Total | Material error? | Notes |
| SYN-001102 | oc-ver1 | 2 | 1 | 1 | 2 | 2 | 8 | No | Financial figures and trends are correct. However, monetary values lack RM, ownership details use substantial space, and cash-flow or liquidity information is omitted. |
| SYN-000217 | oc-ver1 | 0 | 2 | 2 | 2 | 1 | 7 | Yes | Correctly identifies the 2023 disclaimer of opinion, but incorrectly combines Johor Bahru and Selangor into one location. It also treats an empty former-name list as unavailable information. |
| SYN-000148 | oc-ver1 | 2 | 2 | 2 | 1 | 2 | 9 | No | Correctly identifies declining revenue, worsening losses and negative operating cash flow. Financial values are accurate, although the RM currency label is missing. |
| SYN-001070 | oc-ver1 | 1 | 2 | 2 | 2 | 2 | 9 | No | Financial and litigation information is accurate. However, incorporation in Malaysia is not explicitly stated in the company record. Omission of claim amounts is acceptable because both cases were withdrawn. |
| SYN-001203 | oc-ver1 | 0 | 2 | 2 | 2 | 1 | 7 | Yes | Correctly identifies missing financial data, majority corporate ownership and the settled plaintiff case. However, it attributes incorporation in Malaysia to the company when that field belongs to the corporate shareholder. The claim amount also lacks RM. |
| SYN-001212 | oc-ver1 | 2 | 1 | 2 | 2 | 2 | 9 | No | Correctly highlights winding-up status, declining performance and extensive litigation. However, it omits material claim amounts, including a winding-up petition of approximately RM9.47 million. |
| SYN-001102 | oc-ver2 | 2 | 2 | 2 | 2 | 2 | 10 | No | Correctly describes the absence of a single majority shareholder and clearly covers revenue, profit, operating cash flow, cash, borrowings, leverage, audit opinions and litigation status. |
| SYN-000217 | oc-ver2 | 2 | 2 | 2 | 1 | 2 | 9 | No | Correctly separates Selangor from the Johor Bahru business description and highlights financial growth, increasing leverage and the 2023 disclaimer of opinion. The untranslated Malay business description slightly reduces readability. |
| SYN-000148 | oc-ver2 | 1 | 2 | 2 | 1 | 2 | 8 | No | Correctly highlights falling revenue, worsening losses, negative operating cash flow, weak liquidity and increasing leverage. However, the quick-ratio and leverage sentence is grammatically ambiguous, and the ownership percentage is awkwardly formatted. |
| SYN-001070 | oc-ver2 | 2 | 2 | 2 | 2 | 2 | 10 | No | Accurately and clearly covers financial growth, operating cash flow, majority ownership, audit opinions and both withdrawn litigation cases with their roles and largest claim amount. |
| SYN-001203 | oc-ver2 | 2 | 2 | 2 | 2 | 2 | 10 | No | Correctly states that financial and audit information is unavailable, identifies the corporate majority shareholder and accurately describes the settled plaintiff case without making unsupported conclusions. |
| SYN-001212 | oc-ver2 | 2 | 2 | 2 | 2 | 2 | 10 | No | Clearly highlights winding-up status, declining financial performance, weak debt-service coverage, litigation roles and the largest RM9.47 million winding-up claim with judgment entered. |
| SYN-001085 | oc-ver2-heldout | 2 | 2 | 2 | 2 | 2 | 10 | No | Accurately covers the company profile, ownership structure, financial growth, cash, borrowings, audit opinions and absence of litigation. |
| SYN-000333 | oc-ver2-heldout | 2 | 1 | 2 | 2 | 2 | 9 | No | Correctly states that financial, audit and litigation information is unavailable, but omits the company’s recent former name. |
| SYN-001569 | oc-ver2-heldout | 0 | 2 | 2 | 2 | 1 | 7 | Yes | Incorrectly describes a 38% shareholder as holding a majority stake. Financial performance, weak debt-service coverage and the historical audit disclaimer are otherwise covered correctly. |
| SYN-000451 | oc-ver2-heldout | 0 | 1 | 2 | 2 | 0 | 5 | Yes | Incorrectly describes the leverage trend and reports a dismissed case as pending or dismissed. It also omits the recent former name. |
| SYN-001894 | oc-ver2-heldout | 0 | 2 | 2 | 2 | 0 | 6 | Yes | Financial and ownership information is correct, but a dismissed litigation case is incorrectly described as pending or active. |
| SYN-001389 | oc-ver2-heldout | 0 | 1 | 2 | 2 | 1 | 6 | Yes | Correctly identifies eight defendant cases, but incorrectly calls the RM559,500 pending claim the largest. The actual largest claim is RM1,234,500. |

## oc-ver1 Evaluation Results

- Number of summaries: 6
- Total score: 49 out of 60
- Average score: 8.17 out of 10
- Summaries with material factual errors: 2
- Material error rate: 33.3%

- Average score = 49 ÷ 6 = 8.17
- Material error rate = 2 ÷ 6 × 100 = 33.3%

- The oc-ver1, the baseline produced readable summaries within the target word range and generally identified important company, financial and litigation information. However, two of the six summaries contained material factual errors, resulting in a material error rate of 33.3%.
- The errors involved combining separate location fields and attributing a corporate shareholder's country of incorporation to the company being summarised. Other recurring weaknesses included missing RM currency labels, treating empty lists as unavailable information, providing excessive ownership detail and omitting material litigation amounts.
- The relatively high average score should therefore not be interpreted alone. The material factual error rate shows that the oc-ver1 requires improvement before it can be considered reliable.

## oc-ver2 Evaluation Results
- Number of summaries: 6
- Total score: 57 out of 60
- Average score: 9.50 out of 10
- Summaries with material factual errors: 0
- Material error rate: 0%
- Incomplete summaries: 0
- Summaries outside the 100–180-word range: 0

## oc-ver1 vs oc-ver2 Comparison

| Metric | oc-ver1 | oc-ver2 | Change |
|---|---:|---:|---:|
| Total score | 49/60 | 57/60 | +8 |
| Average score | 8.17 | 9.50 | +1.33 |
| Material factual errors | 2 | 0 | -2 |
| Material error rate | 33.3% | 0% | -33.3 percentage points |
| Incomplete summaries | 0 | 0 | No change |
| Outside 100–180 words | 0 | 0 | No change |

## Development-Sample Interpretation

On the six-company development sample, `oc-ver2` improved the average rubric score from 8.17 to 9.50 and reduced the observed material factual error rate from 33.3% to 0%.
The revised prompt improved grounding by keeping company, shareholder and location fields separate. It also improved RM formatting, cash-flow coverage, ownership prioritisation and selection of material litigation information.
Minor presentation issues remain. One Malay business description was not translated, company-name bolding was inconsistent, and one financial-ratio sentence was ambiguous. These issues were recorded for a later final prompt rather than used to continue tuning against the same development companies.
These results show improvement on the development sample only. Because the same companies were used to design the prompt, the results may overstate performance. A separate held-out sample is required before drawing broader conclusions.


## Held-Out Evaluation 

- Six companies that were not used during prompt development were selected for held-out evaluation. The sample includes an ordinary active company, a company without financial history, a historical non-standard audit opinion, financial distress, corporate ownership and companies with different litigation profiles.
- The `oc-ver2` prompt was frozen before generating these summaries. The held-out results were not used to revise Version 2, reducing the risk of evaluating only on companies used during prompt development.
- Number of summaries: 6
- Total score: 43 out of 60
- Average score: 7.17 out of 10
- Summaries with material factual errors: 4
- Material error rate: 66.7%
- Incomplete summaries: 0
- Summaries outside the 100–180-word range: 0

The held-out results were substantially weaker than the development results. The average score fell from 9.50 to 7.17, while the material factual error rate increased from 0% to 66.7%.
The errors primarily involved numerical comparisons and categorical interpretation: identifying majority ownership, describing a non-monotonic leverage trend, preserving exact litigation statuses and selecting the largest claim amount.
These results indicate that additional prompt instructions alone are unlikely to provide sufficient reliability. The final system should calculate and select important facts deterministically in Python before sending a structured fact sheet to the LLM. The LLM can then focus on clear language and presentation instead of performing numerical comparisons and record selection.

## Final held-out evaluation — oc-final

| Company ID | Accuracy | Material coverage | Relevance | Clarity | Calibrated language | Total / 10 | Material error? | Notes |
| SYN-001085 | 2 | 2 | 2 | 2 | 2 | 10 | No | Accurately covers the company profile, absence of a single majority shareholder, earliest and latest financial performance, financial trends, unqualified audit opinions and absence of litigation. |
| SYN-000333 | 2 | 2 | 2 | 2 | 2 | 10 | Correctly translates the business activity, includes the former name and clearly states that financial and audit information is unavailable. The slightly shorter length is reasonable because the record contains no financial or litigation history. |
| SYN-001569 | 2 | 1 | 2 | 2 | 2 | 9 | Correctly avoids treating the 38% shareholder as a majority and accurately reports the financial trends and historical disclaimer of opinion. However, it omits the latest debt-service coverage ratio below one. |
| SYN-000451 | 2 | 1 | 2 | 2 | 2 | 9 | Correctly reports declining revenue, widening losses, negative operating cash flow, the former name and the largest settled plaintiff claim. It omits negative equity, weak liquidity and details of the dismissed defendant case. |
| SYN-001894 | 2 | 1 | 2 | 2 | 2 | 9 | Accurately reports corporate majority ownership, financial trends and the largest dismissed plaintiff claim. However, it omits the below-one quick ratio and the separate RM275,600 case with judgment entered. |
| SYN-001389 | 2 | 0 | 2 | 2 | 2 | 8 | Correctly identifies eight defendant cases and the RM1,234,500 settled case as the largest claim. However, it omits three pending cases, including two winding-up petitions, which are material for closer review. |

### Final results

- Number of summaries: 6
- Total score: 55 out of 60
- Average score: 9.17 out of 10
- Summaries with material factual errors: 0
- Material error rate: 0%
- Incomplete summaries: 0

The final fact-sheet approach improved the held-out average score from
7.17 to 9.17 and reduced the material factual error rate from 66.7% to
0%. Deterministic preprocessing corrected the previous errors involving
majority ownership, financial trends, litigation statuses and largest
claim selection.

The remaining weaknesses relate mainly to coverage rather than factual
accuracy. Some summaries omitted secondary but useful risk indicators,
including weak financial ratios, a judgment-entered case and pending
winding-up petitions. Future development should introduce automated
coverage checks and targeted regeneration for summaries missing required
ownership, financial or litigation facts.