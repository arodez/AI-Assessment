# Delivery Plan

> This is the plan/context you'd hand to an AI (or a teammate) to actually build the MVP. Be concrete — a build session should be able to start from this alone, with no further clarification needed.

## 1. Architecture & Stack

**Stack:** (languages, frameworks, libraries)

**Persistence:** (in-memory / file / SQLite / other) — **limitations of this choice:**

**Why this stack:** (1–2 sentences — fit for the time box and requirements)

## 2. Data Model

Describe the shape of the core entities and how constraints are represented (e.g., capacity, per-event email uniqueness).

```
Event {
  ...
}

Signup {
  ...
}
```

## 3. Flows

For each functional requirement, describe how it gets implemented (screen/endpoint, inputs, outputs, key logic):

**Create event:**

**Sign-up (RSVP):**

**Public list:**

**Organizer view:**

## 4. Edge Cases

| Case | Expected behavior |
|---|---|
| Malformed email | |
| Negative/zero capacity | |
| Empty title | |
| Event at full capacity | |
| Duplicate sign-up (same email, same event) | |

## 5. Out of Scope / Limitations

What the MVP deliberately won't do, and known trade-offs (e.g., no auth, in-memory persistence resets on restart):

-

## 6. Task Breakdown

Ordered list of build steps an AI session could follow:

1.
2.
3.
