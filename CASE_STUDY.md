# OneCredit Company Summaries Generation Case Study

## 1. What a good summary is for this team, and why

The summary is mainly for readers conducting an initial review of companies that may become suppliers or project partners.
Since the full company records contain a lot of information, the goal is to help the reader quickly understand the company, identify potential risks and 
decide which areas need further review.

Therefore, a good summary should be clear, factual and concise, ideally something that can be read within a minute. 
It should include basic company information, such as its business activities, current status, industry and listed state. 
In addition, it should then focus on the more important details, including ownership, financial performance over the years, audit opinions and litigation records.

For financial information, I would focus on key trends and warning signs, such as declining profits, negative operating cash flow or weak liquidity. 
Financial figures should also include the relevant years and units for easier comparison. For litigation, it is important to mention the company's role, 
case status and claim amount where available, without assuming that a claim represents a confirmed liability. 
Moreover, any missing information should also be clearly stated rather than making assumptions.

Lastly, the summary should only serve as a starting point for further review, not as a final decision on whether a company is suitable. 
It should not make unsupported assumptions, predict future performance or recommend approving or rejecting a company. 
The main purpose is to highlight the key information and potential concerns so the reader knows what to look into next.

## 2. What you built

I built a Python pipeline that reads the 50 synthetic company records,
prepares the information needed for each summary, sends it to a large
language model and saves the generated summaries as JSONL files for the
provided viewer.

### Model used
The system uses Google's Gemini API through the `google-genai` Python
library. The final model utilised was `gemini-3.5-flash-lite`, with a low
temperature of 0.1 to reduce unnecessary variation. API credentials are
loaded from a local `.env` file and are not committed to the repository.
Each response is saved immediately, which also allows an interrupted run to
continue without generating completed companies again. I also added
retry handling and a delay between requests because the free API tier from Google Gemini
has a requests-per-minute limit.


### Data exploration
Before building the generation pipeline, the dataset was explored in
`notebook/data_explore.ipynb`. The company profiles,
ownership structures, financial histories, audit opinions and litigation
records were studied and analysed. Finally, six development companies representing different
conditions, including ordinary financial performance, losses, missing
financial information, non-standard audit opinions, litigation and
winding-up status were selected.

### Evaluation rubric
Before evaluating the generated summaries, a manual evaluation rubric was created
in `notebook/evaluation_rubric.md`. This was intended to make the
comparison between versions more consistent rather than changing the
definition of a good summary after seeing each result.

The rubric scores five criteria from 0 to 2: factual accuracy, material
coverage, relevance, clarity and conciseness, and calibrated language.
Each summary can therefore receive a maximum score of 10.
The rubric also includes a material factual error rule. Under this rule, a summary is considered
unsuccessful if it contains an important error—such as an incorrect
financial trend, ownership classification, litigation role, case status
or audit opinion—even when its total numerical score is relatively
high. The detailed evaluation method and results are discussed in the
next section.

### `oc-ver1`
The first version, named `oc-ver1`, was a baseline that sent the complete raw records of the selected
six development companies to the Gemini model with relatively general summary instructions.
It produced readable summaries, but some outputs confused fields from
different parts of the nested record and omitted important information.

### `oc-ver2`
The second version, called `oc-ver2`, used a more detailed prompt with explicit
grounding rules, coverage priorities and Markdown formatting. It
improved performance on the six development companies. However, testing
the frozen prompt on a separate six-company held-out sample exposed
material errors. These included incorrectly classifying a 38%
shareholder as a majority shareholder, describing a fluctuating
financial ratio as increasing, changing exact litigation statuses and
selecting the wrong case as the largest claim.

### `oc-final`

In `oc-final`, `src/build_facts.py` deterministically calculates and selects
important facts, including ownership classification, financial trends,
risk indicators, audit opinions and litigation details. Gemini receives
this structured fact sheet instead of the original nested company
record, allowing it to focus on writing, formatting and translating
Malay business descriptions. This approach reduces the risk of incorrect
calculations or interpretations.

Based on these results, the final version, `oc-final`, separates factual processing
from language generation:

```text
Company JSONL
    → deterministic Python fact builder
    → structured company fact sheet
    → Gemini for writing and translation
    → final summary JSONL
    → provided FastAPI viewer
```


### `build_facts.py`
The file performs the calculations and record selection that
the held-out evaluation showed were unreliable when delegated directly
to the language model. It determines majority ownership, selects the
largest shareholders, compares financial years, labels financial
trends, identifies risk indicators, preserves audit opinions and counts
litigation cases by role and exact status. It also selects the largest
claim and keeps pending and judgment-entered cases separate.

### `oc-final-generate.py`
This is the final Python generation script that sends these prepared fact sheets to Gemini.
The fact sheet preserves the original business description, while the model is mainly responsible
for presenting the supplied facts in clear Markdown and translating Malay business descriptions
into natural English during summary generation.
The final prompt instructs it not to recalculate facts, alter
legal names or statuses, make recommendations, or treat litigation
claims as confirmed losses. The final system generated summaries for
all 50 companies in `summaries/oc-final.jsonl`.

## 3. How you know whether it's good

I evaluated the summaries manually against the original company records
using the rubric in `notebook/evaluation_rubric.md`. Each summary was
scored from 0 to 2 across five criteria:

1. Factual accuracy
2. Material coverage
3. Relevance
4. Clarity and conciseness
5. Calibrated language

The maximum score was 10, and a material factual error rule was used,
because a high total score could hide an important mistake. For example,
an incorrect financial trend, majority classification, audit opinion,
litigation role or case status would cause the summary to be considered
unsuccessful regardless of its numerical score.

### Development-sample evaluation

Initially, six companies were selected for development. The sample covered
different conditions, including an ordinary active company, financial
losses, missing financial information, a non-standard audit opinion,
litigation and winding-up status.

The baseline `oc-ver1` achieved an average score of 8.17, but two of its
six summaries contained material factual errors. The errors involved
combining separate location fields and incorrectly transferring a
corporate shareholder's country of incorporation to the company being
summarised.

After adding more explicit grounding, formatting and coverage
instructions, `oc-ver2` improved the development-sample average to 9.50
and produced no material factual errors on those six companies. However,
because the same sample was used to improve the prompt, this result could
overstate how well the prompt would perform on different companies.

### Held-out evaluation

Therefore, another six companies that had not been used during
prompt development were selected. I froze the `oc-ver2` prompt before generating their
summaries.

Performance dropped substantially on this held-out sample. The average
score was 7.17, and four of the six summaries contained material factual
errors. The model incorrectly classified a 38% shareholder as a majority
shareholder, described a fluctuating leverage ratio as increasing,
changed exact litigation statuses and selected the wrong case as the
largest claim.

These results showed that good development-sample performance was not
enough. They also showed that detailed prompt instructions alone could
not reliably handle numerical comparisons and categorical record
selection.

### Final-system evaluation

The held-out failures were utilised to design `oc-final`. The final approach
calculates and selects important facts deterministically in Python before
asking Gemini to write the summary.

Final summaries were then evaluated against the same six difficult companies
as a regression check. The average score increased to 9.17, and none of
the six summaries contained a material factual error. The previous
errors involving majority ownership, financial trends, case statuses and
largest claim selection were corrected.

| Version | Evaluation sample | Total score | Average | Material errors | Error rate |
|---|---|---:|---:|---:|---:|
| `oc-ver1` | Development sample | 49/60 | 8.17 | 2/6 | 33.3% |
| `oc-ver2` | Development sample | 57/60 | 9.50 | 0/6 | 0% |
| `oc-ver2` | Held-out sample | 43/60 | 7.17 | 4/6 | 66.7% |
| `oc-final` | Regression check | 55/60 | 9.17 | 0/6 | 0% |

The remaining weaknesses were mainly related to coverage rather than
incorrect facts. Some final summaries omitted useful secondary details,
such as weak financial ratios, a judgment-entered case or pending
winding-up petitions.


### Evaluation limitations

The evaluation was completed manually by one reviewer, so the rubric scores
contain some subjective judgement. A second reviewer would make the scores
more reliable.

The final evaluation using six companies is mainly to check whether the 
system still performs consistently after the changes. Since the failures from these
companies were used to design the final system, the results should not be considered a
fully independent evaluation. Those companies' failures had already influenced
the design of `oc-final`. Therefore, the 9.17 score shows that the known failure
modes were corrected, but it is not an unbiased estimate of performance on 
completely unseen records. A future evaluation should use a new untouched sample 
or additional reviewers.

## 4. What you'd do next, and how you'd keep improving it

The first improvement would be to check whether each summary includes the
most important information before saving it. For example, a majority
shareholder's name and percentage should both be included. Companies with
litigation should include the largest claim and any important pending or
judgment-entered cases. If something important is missing, only that
summary needs to be generated again instead of rerunning all 50.

More automated tests could also be added for `src/build_facts.py`. The
tests should cover important cases such as exactly 50% ownership, missing
financial information, negative equity, a single financial year and
different litigation statuses. This would help ensure that future code
changes do not affect the accuracy of the prepared facts.

Finally, the evaluation could be improved by using a new sample that was
not involved in developing `oc-final`. Having another person score the
same summaries would also help reduce the subjectivity of the current
manual evaluation. With more time and API quota, the same evaluation
process could be used to compare other models.
