# Production Notes

The repository intentionally keeps execution local and deterministic.

A production multi-agent service would require additional controls.

## Tool security

Each agent should receive only the tools required for its role. Write actions
should use stronger authorization than read-only retrieval.

## Human approval

High-impact actions such as deleting data, sending messages, changing account
permissions, or executing financial operations should support explicit human
approval.

## Observability

Record:

- workflow ID
- agent name
- model/version
- tool call
- latency
- token usage
- cost
- retry count
- errors
- final outcome

## Persistence

Long workflows should use durable checkpoints so execution can resume after
worker failures.

## Loop control

Every retry path needs a limit. Agents should not be allowed to repeatedly call
one another without a workflow-level budget.

## Evaluation

Maintain versioned scenario sets and compare changes before promoting new
prompts, models, tools, or orchestration logic.
