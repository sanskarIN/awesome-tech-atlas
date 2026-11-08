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

## Where to go next

- Authoritative starting section
- One meaningful alternative and how to decide between them
```

Add a matching record to [data/resources.json](../data/resources.json); see [CONTRIBUTING.md](../CONTRIBUTING.md) for review and verification steps.
