# Resource profile template

Copy this structure to `resources/<id>.md`. Replace the placeholders and remove unneeded sections. Do **not** copy upstream explanatory paragraphs.

```markdown
# Resource name

**Official documentation:** https://example.org/docs
**Kind:** Official documentation / learning guide / specification / community reference
**Category:** category-id
**Last source inspection:** YYYY-MM-DD

## Why it matters

Two or three sentences describing the real capability and audience.

## Good fit

- A specific use case or goal.

## Trade-offs

- A documented strength; one practical limitation or important constraint.
- Separate editorial trade-offs from upstream factual claims.

## Try it

A concrete, low-risk first step or short original example, with prerequisites if any.

## Worked example: descriptive title (optional for substantial profiles)

### Prerequisites

Exact tool versions or minimum requirements, and where the sample runs.

### Steps

One original, self-contained snippet and the commands needed to reproduce it.

### Expected result

Concrete observable output or interaction, without unsupported performance claims.

### Troubleshooting

Likely errors, limitations, and safety caveats.

### Evidence and execution status

Link the specific official reference, give the actual review date, and distinguish "executed" from "documentation-reviewed."

## Where to go next

- Authoritative starting section
- One meaningful alternative and how to decide between them
```

Add a matching record to [data/resources.json](../data/resources.json); see [CONTRIBUTING.md](../CONTRIBUTING.md) for review and verification steps.
