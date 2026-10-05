# Agent Design

## Planner

Input: user request

Output: objective and ordered task plan

The planner is intentionally prevented from retrieving evidence. Its job is
decomposition.

## Researcher

Input: request, optional critic feedback

Output: ranked evidence

The local implementation uses TF-IDF retrieval. A production implementation can
replace the search tool with hybrid/vector retrieval without changing the agent.

## Analyst

Input: evidence

Output: structured findings and recommendation

The analyst does not control workflow transitions.

## Critic

Input: evidence, findings, recommendation

Output: approval or revision request

The critic checks basic evidence sufficiency. A model-backed implementation could
perform claim-level entailment and policy checks.

## Writer

Input: verified state

Output: final user-facing response

The writer is intentionally last so new unsupported claims are less likely to
enter the workflow after verification.
