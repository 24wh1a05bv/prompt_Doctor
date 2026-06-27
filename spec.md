# Prompt Doctor - Specification

## Overview

Prompt Doctor is a Streamlit-based learning application that teaches prompt engineering through an AI examiner.

Users write prompts for tasks in a chosen domain. An AI examiner evaluates the prompt against level-specific prompt engineering principles, provides diagnostic feedback, and unlocks progressively harder levels when requirements are met.

The focus is entirely on prompt engineering. No RAG, tools, retrieval, or fine-tuning are involved.

---

# Objective

Build an application where:

* Users select a domain (Legal, Healthcare, Customer Support, etc.).
* Users receive a task and sample input.
* Users write a prompt.
* The application executes the prompt.
* An AI examiner grades the prompt.
* Users improve their prompt based on feedback.
* Users progress through 5 increasingly difficult levels.

---

# Tech Stack

* Streamlit
* OpenRouter API
* Python

---

# Project Structure

```text
prompt_doctor/
├── app.py          # Provided Streamlit UI
├── levels.py       # Provided level definitions
├── runner.py       # Provided prompt execution logic
├── examiner.py     # Build this file
└── .env
```

---

# Core User Flow

1. Select domain.
2. Read task and sample input.
3. Write a prompt.
4. Submit prompt.
5. Run prompt against sample input.
6. Examiner grades prompt.
7. View feedback and output.
8. Revise prompt.
9. Pass level.
10. Unlock next level.

---

# Level System

## Level 1 - Basic Prompting

### Goal

Demonstrate:

* Explicit role assignment
* Clear instructions

### Pass Criteria

* Response is correct
* Response is relevant
* No missing requirements
* No unnecessary content

---

## Level 2 - Structured Output

### Goal

Add output schema requirements.

### Pass Criteria

* Output follows schema
* Valid JSON returned consistently

---

## Level 3 - Few-Shot Prompting

### Goal

Provide examples for ambiguous cases.

### Pass Criteria

* Model correctly handles previously failing cases
* Examples clearly guide behavior

---

## Level 4 - Reasoning

### Goal

Use chain-of-thought style reasoning.

### Pass Criteria

* Multi-step tasks solved correctly
* Edge cases handled properly

---

## Level 5 - Robustness

### Goal

Add defensive constraints.

### Pass Criteria

* Prompt survives noisy inputs
* Prompt resists adversarial inputs
* Output remains correct

---

# Examiner Responsibilities

The examiner is the core feature.

## Role

Act as:

> Strict but fair prompt-engineering examiner

---

## Evaluation Rules

For every submission:

1. Judge only current level principles.
2. Be specific.
3. Identify weaknesses.
4. Quote weak phrases when possible.
5. Identify missing requirements.
6. Ask exactly one guiding question per issue.
7. Never rewrite the user's prompt.
8. Never provide a corrected prompt.
9. Reason internally before grading.
10. Return JSON only.

---

# Examiner Input

```json
{
  "level": 2,
  "principles": [...],
  "student_prompt": "...",
  "sample_input": "...",
  "model_output": "..."
}
```

---

# Examiner Output Schema

```json
{
  "level": 2,
  "principles": [
    {
      "name": "output_format",
      "pass": false,
      "weakness": "No schema specified.",
      "question": "What exact fields and types should always be returned?"
    }
  ],
  "ran_ok": true,
  "verdict": "revise"
}
```

---

# Verdict Logic

## Pass

All level principles pass.

```json
{
  "verdict": "pass"
}
```

Unlock next level.

---

## Revise

At least one principle fails.

```json
{
  "verdict": "revise"
}
```

Remain on current level.

---

# UI Layout

## Left Panel

* Domain selector
* Current level
* Task description
* Sample input
* Prompt editor
* Submit button

## Right Panel

* Examiner verdict
* Pass/Fail indicators
* Weakness explanations
* Guiding questions
* Live model output

---

# Functional Requirements

## Prompt Execution

* Run user's prompt against sample input.
* Capture generated output.

## Prompt Grading

* Send prompt, level, principles, and output to examiner.
* Receive structured JSON verdict.

## Progress Tracking

* Track current level.
* Unlock next level after passing.

## Error Handling

* Handle invalid examiner responses.
* Handle API failures.
* Display user-friendly errors.

---

# Constraints

* No RAG
* No document retrieval
* No external tools
* No file uploads
* No fine-tuning
* Prompt engineering only

---

# Success Criteria

A successful submission should:

* Allow users to choose a domain.
* Evaluate prompts across 5 levels.
* Produce consistent JSON verdicts.
* Prevent examiner from rewriting prompts.
* Provide actionable diagnostic feedback.
* Unlock levels progressively.
* Demonstrate Role, Structure, Few-Shot, Reasoning, and Robustness techniques.

---

# Stretch Goals

1. Multiple judge models comparison.
2. Prompt engineering scorecard.
3. Temperature comparison (0 vs 1).
4. Leaderboard based on revisions required.
5. Historical performance tracking.

---

# Deliverables

* Functional Streamlit application.
* Implemented `examiner.py`.
* Reliable JSON grading system.
* Five-level progression workflow.
* Prompt execution and evaluation pipeline.
