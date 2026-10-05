# Multi-Agent AI Research & Analysis System

A practical multi-agent AI project that breaks a user request into smaller tasks and assigns those tasks to specialized agents.

Instead of asking one large agent to research, analyze, verify, and write everything in a single step, this project uses a small team of agents with clearly separated responsibilities:

- **Planner Agent** — decides what work needs to be done
- **Research Agent** — searches the local knowledge base for evidence
- **Analysis Agent** — turns evidence into structured findings
- **Critic Agent** — checks whether important claims are supported
- **Writer Agent** — creates the final response with source references

A central orchestrator manages the workflow, shared state, execution order, retries, and trace logging.

The repository runs locally without an LLM API key. The agent interfaces are intentionally separated from the local reasoning implementation so an external LLM can be added later without redesigning the workflow.

> The knowledge base and evaluation scenarios included here are synthetic portfolio data. They do not contain customer information, proprietary company documents, or private production data.

---

## Why build this as multiple agents?

A single prompt can perform several tasks at once, but it becomes harder to understand where a failure came from.

For example:

```text
User asks a question
        |
        v
One agent researches + reasons + verifies + writes
        |
        v
Something is wrong
```

Was the source wrong? Was evidence missing? Did the reasoning fail? Did the final answer overstate the evidence?

This project separates those responsibilities.

```text
User Request
     |
     v
+-------------+
|   Planner   |
+------+------+
       |
       v
+-------------+
|  Researcher |
+------+------+
       |
       v
+-------------+
|   Analyst   |
+------+------+
       |
       v
+-------------+
|   Critic    |
+------+------+
       |
   pass|  |revise
       |  +------------------+
       |                     |
       v                     |
+-------------+              |
|   Writer    |              |
+------+------+              |
       |                     |
       v                     |
 Final Answer                |
                             |
                  Research / Analysis
                       retry loop
```

The result is easier to inspect because every stage leaves an execution trace.

---

## Example use case

Suppose a product manager asks:

```text
Should our support team prioritize reducing first-response time or
increasing self-service documentation coverage?
```

The system can:

1. identify the decision being requested;
2. retrieve relevant support metrics and documentation;
3. compare the available evidence;
4. check whether the recommendation is actually supported;
5. return a concise recommendation with the sources used.

Example output:

```text
Recommendation

Prioritize self-service documentation coverage first.

The available support data shows that documented issue categories have
lower repeat-contact rates, while the response-time report shows the team
is already within its current SLA target.

Evidence
- support-metrics.md
- knowledge-base-study.md
- sla-policy.md
```

The included evaluation suite checks whether the workflow chooses the expected evidence and produces the required facts.

---

# System Architecture

```text
                           User Request
                                |
                                v
                     +---------------------+
                     |    Orchestrator     |
                     | workflow + state    |
                     +----------+----------+
                                |
                                v
                     +---------------------+
                     |    Planner Agent    |
                     | intent + task plan  |
                     +----------+----------+
                                |
                                v
                     +---------------------+
                     |   Research Agent    |
                     | retrieve evidence   |
                     +----------+----------+
                                |
                                v
                     +---------------------+
                     |   Analysis Agent    |
                     | findings + decision |
                     +----------+----------+
                                |
                                v
                     +---------------------+
                     |    Critic Agent     |
                     | evidence validation |
                     +----------+----------+
                                |
                     +----------+----------+
                     |                     |
                  approved              revise
                     |                     |
                     v                     |
              +--------------+             |
              | Writer Agent |             |
              +------+-------+             |
                     |                     |
                     v                     |
                Final Answer               |
                                           |
                           +---------------+
                           |
                    bounded retry loop

Every step
    |
    v
+---------------------+
| Execution Trace     |
| agent / input /     |
| output / status     |
+---------------------+
```

---

# Agent responsibilities

## Planner Agent

The planner interprets the request and creates a structured task plan.

Example:

```json
{
  "objective": "Compare support improvement options",
  "steps": [
    "find evidence about first-response performance",
    "find evidence about self-service documentation",
    "compare expected operational impact",
    "produce a supported recommendation"
  ]
}
```

The planner does not search documents or write the final response.

---

## Research Agent

The research agent searches the project knowledge base.

It uses TF-IDF retrieval and returns ranked evidence with:

- source file
- title
- relevance score
- matching passage

Example:

```json
{
  "source": "support-metrics.md",
  "title": "Support Operations Metrics",
  "score": 0.61,
  "passage": "Median first-response time..."
}
```

Keeping retrieval separate makes it possible to inspect exactly what evidence the downstream agents received.

---

## Analysis Agent

The analyst converts retrieved passages into structured findings.

It identifies:

- facts
- numeric evidence
- trade-offs
- evidence gaps
- candidate recommendation

The output remains structured rather than immediately becoming polished prose.

---

## Critic Agent

The critic acts as a verification layer.

It checks:

- whether evidence was retrieved;
- whether the recommendation has supporting facts;
- whether sources are available;
- whether the workflow has enough information to answer;
- whether another research pass is needed.

The critic can return:

```text
APPROVED
```

or request another bounded research/analysis pass.

The orchestrator limits retries so agents cannot loop indefinitely.

---

## Writer Agent

The writer receives only the verified state.

It creates a readable final response containing:

- recommendation or answer;
- key findings;
- evidence;
- source names.

The writer does not independently invent new facts.

---

# Shared state

Agents communicate through a structured `WorkflowState`.

```text
WorkflowState
├── request
├── plan
├── evidence
├── findings
├── recommendation
├── critique
├── final_answer
├── retry_count
└── trace
```

This avoids passing an uncontrolled conversation transcript between every agent.

It also makes debugging easier because the complete state can be serialized as JSON.

---

# Agent workflow

```text
START
  |
  v
PLAN
  |
  v
RESEARCH
  |
  v
ANALYZE
  |
  v
CRITIQUE
  |
  +------ approved ------> WRITE ------> END
  |
  +------ revise --------> RESEARCH
                               |
                               v
                            ANALYZE
                               |
                               v
                            CRITIQUE
```

Retries are bounded by `max_retries` in `config.yaml`.

---

# Tools

Agents do not directly access arbitrary system resources.

The project exposes explicit tools.

### KnowledgeSearchTool

Searches the local documentation index.

### CalculatorTool

Evaluates basic arithmetic expressions using a restricted AST evaluator rather than Python `eval`.

This demonstrates the same pattern that can later be used for:

- APIs
- SQL tools
- vector databases
- web search
- ticketing systems
- CRM systems
- internal services

---

# Execution traces

Every agent action is recorded.

Example:

```json
{
  "agent": "researcher",
  "status": "completed",
  "summary": "Retrieved 4 evidence passages"
}
```

A complete run can be saved to:

```text
reports/latest_trace.json
```

This is useful for debugging agent systems because the final answer alone does not explain how the workflow reached its result.

---

# Evaluation

The repository includes scenario-based evaluation in:

```text
data/evaluation/scenarios.json
```

Each scenario defines:

- user request
- expected source documents
- required facts
- expected workflow behavior

The evaluation script measures:

### Source Recall

How many expected evidence sources were retrieved.

### Required Fact Coverage

Whether important expected facts appear in the final response.

### Workflow Completion

Whether the workflow reached a successful final state.

### Critic Approval Rate

Whether the critic accepted the final evidence and analysis.

Run:

```bash
python -m src.evaluate
```

The generated report is saved to:

```text
reports/agent_evaluation.md
```

Current included evaluation run:

| Metric | Score |
|---|---:|
| Source Recall | 1.000 |
| Required Fact Coverage | 0.542 |
| Workflow Completion | 1.000 |
| Critic Approval | 1.000 |

These values come from the included scenario suite and are regenerated by `python -m src.evaluate`.

---

# Repository structure

```text
multi-agent-ai-system/
├── README.md
├── requirements.txt
├── config.yaml
├── .gitignore
├── Makefile
│
├── src/
│   ├── __init__.py
│   ├── schemas.py
│   ├── memory.py
│   ├── orchestrator.py
│   ├── evaluate.py
│   ├── demo.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── planner.py
│   │   ├── researcher.py
│   │   ├── analyst.py
│   │   ├── critic.py
│   │   └── writer.py
│   │
│   └── tools/
│       ├── __init__.py
│       ├── knowledge_search.py
│       └── calculator.py
│
├── data/
│   ├── knowledge/
│   │   ├── support-metrics.md
│   │   ├── knowledge-base-study.md
│   │   ├── sla-policy.md
│   │   ├── onboarding-analysis.md
│   │   ├── automation-study.md
│   │   └── customer-feedback.md
│   │
│   └── evaluation/
│       └── scenarios.json
│
├── tests/
│   ├── test_calculator.py
│   ├── test_search.py
│   ├── test_orchestrator.py
│   └── test_memory.py
│
├── reports/
│   ├── agent_evaluation.md
│   ├── evaluation_results.json
│   └── example_trace.json
│
├── docs/
│   ├── architecture.md
│   ├── agent-design.md
│   ├── evaluation.md
│   └── production-notes.md
│
└── .github/
    └── workflows/
        └── tests.yml
```

---

# Run locally

## 1. Create an environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Run the demo

```bash
python -m src.demo "Should we prioritize reducing first-response time or improving self-service documentation?"
```

The command prints:

- final answer
- agent execution trace
- sources used

---

## 4. Save a trace

```bash
python -m src.demo \
  "Should we prioritize reducing first-response time or improving self-service documentation?" \
  --trace reports/latest_trace.json
```

---

## 5. Run evaluation

```bash
python -m src.evaluate
```

---

## 6. Run tests

```bash
pytest -q
```

---

# Programmatic usage

```python
from src.orchestrator import MultiAgentOrchestrator

system = MultiAgentOrchestrator.from_config("config.yaml")

result = system.run(
    "Should we prioritize reducing first-response time "
    "or improving self-service documentation?"
)

print(result.final_answer)

for event in result.trace:
    print(event.agent, event.status)
```

---

# Failure handling

Multi-agent systems need explicit failure behavior.

This project includes:

- bounded retry count;
- empty-retrieval detection;
- critic approval/revision decisions;
- structured state instead of free-form agent messages;
- restricted calculator execution;
- source-aware writing;
- trace logging.

If the system cannot find enough evidence, the final response should say that evidence is insufficient rather than pretending the answer is known.

---

# Why no external LLM is required

The purpose of this repository is to demonstrate the **agent architecture and workflow**, not require reviewers to configure a paid model before they can run it.

The included agents use deterministic local logic.

The interfaces are separated so a production version can replace an agent implementation with:

```text
OpenAI
Anthropic
Gemini
local LLM
LangChain
LangGraph
Semantic Kernel
AutoGen
```

without changing the overall orchestration design.

---

# Production version

A production implementation could replace the local components as follows:

```text
Local planner
    -> LLM structured-output planner

TF-IDF search
    -> vector DB + hybrid retrieval

Local analyst
    -> reasoning model

Rule-based critic
    -> LLM evaluator + policy checks

Local writer
    -> production LLM

JSON state
    -> Redis / database / workflow store

Local orchestration
    -> LangGraph / Temporal / distributed worker system
```

Additional production requirements would include:

- authentication and authorization;
- tenant-aware tool permissions;
- secrets management;
- prompt-injection defenses;
- human approval for sensitive actions;
- token and cost limits;
- agent timeouts;
- model fallbacks;
- distributed tracing;
- tool-call auditing;
- persistent checkpoints;
- evaluation datasets;
- latency monitoring;
- model/version tracking.

---

# Tech stack

**Python · scikit-learn · NumPy · PyYAML · Pytest**

Concepts demonstrated:

**Multi-Agent Systems · Agent Orchestration · Tool Use · Shared State · Agent Memory · Retrieval · Planning · Verification · Guardrails · Execution Tracing · Agent Evaluation**

---

# Future improvements

- integrate LangGraph for state-machine orchestration;
- add real LLM-backed agents;
- add MCP tools;
- add vector database retrieval;
- implement persistent conversation memory;
- add human-in-the-loop approval;
- support parallel research agents;
- add FastAPI endpoints;
- containerize with Docker;
- add OpenTelemetry traces;
- add token/cost accounting;
- add agent-level latency metrics;
- evaluate model-based critic scoring.
