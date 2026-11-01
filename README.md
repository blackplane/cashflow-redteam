# cashflow-redteam

An educational repository demonstrating **Long-Context Indirect Prompt Injection** vulnerabilities and defensive mitigation strategies within autonomous AI agents processing financial records. 

Built using the open-source **Stirrup** agent framework, this project simulates a commercial loan credit-underwriting agent that analyzes multi-period PDF bank statements to calculate standard cash flow metrics (Operating Cash Flow, DSCR), while exposing how attackers can hide malicious payloads within raw transactional text data.

---

## 🔍 The Threat Vector: Long-Context Injection
As LLMs scale to handle 100k+ token context windows, standard alignment safety degrades inside large documents due to "lost in the middle" phenomena and formatting confusion. 

In a **cashflow-redteam** scenario, an attacker modifies a transaction description string inside a legitimate-looking multi-page PDF bank statement. When a victim feeds this document into an automated underwriting or aggregation agent, the LLM reads the hidden instruction embedded in the data ledger and hijacks the execution environment.

### Demonstrated Exploits
1. **Metric Hijacking (Data Integrity):** Overriding true ledger math to force the model to output a fabricated, high Debt Service Coverage Ratio (DSCR), tricking automated loan approval gates.
2. **Sandbox Reconnaissance (Privilege Escalation):** Inducing the agent's Python code interpreter tool to print system environment variables or file directories.
3. **Data Exfiltration (Theft):** Exploiting Markdown rendering capabilities to covertly exfiltrate extracted financial data or system prompts to an external attacker-controlled URL.

---

## 🛠️ Repository Architecture

```text
src/cashflow_redteam/
├── agent/
│   ├── app.py            # Stirrup agent build + run_spread() (LiteLLM client, metrics capture)
│   ├── prompts.py        # Task prompt, vulnerable vs. secure (spotlighting) system prompts
│   └── tools.py          # list/read statements, chart of accounts, compute_cashflow, send_email (honeypot), submit_report
├── data_gen/generate.py  # Synthetic LlamaParse-style statements + ground truth
├── attacks/
│   ├── payloads.py       # Objectives x strategies (explicit / fragmented / distributed)
│   └── inject.py         # Poison benign statements, record payload positions
├── defenses.py           # spotlight, structured_reader, detector, egress_allowlist, invariants
├── eval/
│   ├── scoring.py        # Accuracy, ASR, cash-flow math (shared with the agent tool)
│   ├── run_matrix.py     # Experiment matrix runner
│   └── report.py         # Results tables / plots
└── schemas.py            # Chart of accounts, transactions, SpreadReport
configs/experiment.yaml   # Models A/B/C, conditions, defenses, sweeps, repeats
data/
├── benign_stmts/         # Clean statements (markdown)
├── poisoned_stmts/       # <objective>/<strategy>/ poisoned copies + manifest
└── ground_truth/         # Labels (never shown to the agent)
docs/experiment-plan.md
tests/
├── test_scoring.py       # Deterministic
├── test_exploits.py      # Live (-m live)
└── test_mitigations.py   # Unit + live
```

---

## 🚀 Quickstart

### 1. Prerequisites
Ensure you have Docker running locally (required for Stirrup's secure tool sandbox environment) and Python 3.12+ (required by Stirrup).

```bash
git clone <repo-url>
cd cashflow-redteam
uv sync
```

### 2. Configure Environment
Create a `.env` file in the root directory:
Copy `.env.example` to `.env`. LiteLLM reads provider keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`,
`OPENROUTER_API_KEY`, ...). To route through a LiteLLM proxy or an OpenAI-compatible endpoint instead, set
`LITELLM_API_BASE` and `LITELLM_API_KEY`.

### 3. Run the Proof of Concepts
Execute the automated test suite to witness the exploit behaviors and defensive blocks:

```bash
uv run cfr-generate --companies 5 --months 6     # synthetic statements + ground truth
uv run cfr-poison                                # poisoned variants
uv run cfr-run --limit 4                         # smoke test, then full matrix
uv run cfr-report runs/<run_id>

uv run pytest                                    # deterministic tests
uv run pytest -m live tests/test_exploits.py -s  # live demos (cost money)
```

---

## 🛡️ Defenses Implemented

This repository showcases a multi-layered approach to securing document-processing agents:

* **Strict Instruction-Data Isolation:** Architecting system prompts with concrete operational boundaries (`[TASK]`, `[DOCUMENT_CONTEXT]`) that instruct the model to explicitly ignore instructional syntax found within data variables.
* **Tool Output Schema Validation:** Forcing structural inputs and outputs via strong schema validation (Pydantic), neutralizing the agent's capability to execute malicious, unstructured strings.
* **Secure Tool Isolation:** Utilizing Stirrup's Docker execution backend to isolate code execution tools, ensuring that environment leaks or unauthorized system read commands are entirely trapped inside disposable containers.

---

## ⚖️ Legal & Ethical Disclaimer
This project is created exclusively for security research, awareness, and defensive educational purposes. The code templates and payloads provided demonstrate abstract vulnerabilities within document processing workflows and are not targeted at any real-world banking provider or third-party enterprise application.

