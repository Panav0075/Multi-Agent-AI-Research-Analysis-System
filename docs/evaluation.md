# Evaluation

Agent systems should be evaluated at more than the final-answer level.

This repository uses four lightweight metrics.

## Source recall

Measures whether expected evidence documents were retrieved.

## Required fact coverage

Measures whether scenario-specific facts appear in the final response.

## Workflow completion

Checks that the state machine reaches a completed state.

## Critic approval

Checks whether the critic considered the evidence sufficient.

These tests are useful as regression checks. They do not replace human
evaluation or model-based evaluation for reasoning quality, hallucinations,
faithfulness, safety, and usefulness.
