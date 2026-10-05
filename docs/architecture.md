# Architecture

The system uses explicit orchestration rather than allowing agents to call each
other freely.

The orchestrator owns workflow transitions:

```text
planner -> researcher -> analyst -> critic -> writer
                         ^          |
                         |          |
                         +-- retry -+
```

This keeps control flow visible and makes retry limits enforceable.

## State

All agents receive and return the same typed `WorkflowState`. Agents update only
the fields relevant to their responsibility.

## Checkpoints

The orchestrator stores state checkpoints after major steps. The current
implementation keeps them in memory, but the interface could be replaced by a
database, Redis, or a durable workflow engine.

## Tools

Tools are separate from agents. This makes permissions easier to reason about:
an agent can only perform actions through tools explicitly provided to it.

## Verification

The critic does not generate the final answer. It decides whether the current
state contains enough evidence and analysis for the writer to proceed.
