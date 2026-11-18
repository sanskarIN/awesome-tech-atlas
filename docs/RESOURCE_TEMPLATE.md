# Resource profile template

This template mirrors the *actual validator contract*. Use it when creating a new resource profile; do not keep the sample values or publish an uninspected inspection date. Start by inspecting the canonical upstream documentation yourself, then write **original** descriptions and examples rather than copying upstream prose.

## Required catalog and profile relationship

Create one record in [data/resources.json](../data/resources.json) and one corresponding file in the resources directory. The profile path uses the **id** field (for example, **resources/sample-guide.md**) while the profile title must match the catalog **name** exactly.

| Catalog field | Profile requirement |
| --- | --- |
| id | Filename under resources, lowercase hyphenated slug |
| name | First heading: the same resource title |
| category | Link to the matching existing category page |
| subcategory | Exact label after the category link and middle dot |
| kind | Human-readable type in the profile: replace hyphens with spaces |
| url | Exact HTTPS source URL in the header; no query or fragment |
| summary | Original short catalog description; category-page summaries may differ |
| verified_on | Exact calendar date in the profile header and verification scope |

The source label is usually **Official source**. For an independent author-maintained resource, **Original author-published source** is also allowed. Do not call an independent educational book an official programming-language specification. A parenthetical explanation after the canonical type is allowed, but the underlying type must match the catalog.

## Copyable profile skeleton

Copy the fenced content into the new resource profile. Replace every double-braced placeholder with a truthful, specific value; remove all placeholders before opening a PR.

~~~markdown
# {{name}}

**Official source:** {{url}}
**Type:** {{kind_label}}
**Category:** [{{category_label}}](../categories/{{category_slug}}.md) · {{subcategory}}
**Last official-page inspection:** {{verified_on}}

## Why it matters

{{purpose}}

## Good fit

{{use_cases}}

## Strength and trade-off

- **Strength:** {{strength}}
- **Limitation:** {{limitation}}

These are contextual editorial selection notes, not independently measured
performance, reliability, or security claims.

## Try it

{{first_step}}

## Where to go next

- Read the [upstream documentation]({{url}}) for prerequisites, version-specific
  behavior, and details that may have changed after the inspection.
- **Alternative:** [{{alternative_name}}]({{alternative_id}}.md).
  {{alternative_decision}}

**Verification scope:** The source page was inspected on {{verified_on}}.
{{scope_note}}
~~~

**Minimum editorial substance:** write useful, specific prose in all five primary sections. The validator rejects missing, duplicated, misplaced and insubstantial sections, and requires both the strength and limitation labels. The verification scope should distinguish what was read or tested from what remains unverified. It must include the exact date from the catalog. Never claim to have installed, run, benchmarked, or security-audited software unless you really did.

## Matching catalog record

Use the complete field set shown below. The sample values are structural examples only; substitute a real, upstream-inspected resource. Set **kind_slug** to one of the supported catalog kinds (for example, official-docs, official-guide, learning-guide, learning-course, reference, specification, community-reference or community-guide). For its profile header, use the corresponding display text with spaces.

~~~json
{
  "id": "{{id}}",
  "name": "{{name}}",
  "category": "{{category_slug}}",
  "subcategory": "{{subcategory}}",
  "kind": "{{kind_slug}}",
  "url": "{{url}}",
  "summary": "{{summary}}",
  "verified_on": "{{verified_on}}"
}
~~~

A resource is not fully indexed merely because its JSON record and profile exist. **Update the maintained Markdown indexes manually** and adjust their counts:

1. Add one matching row to [resources/README.md](../resources/README.md); the resource label must equal the catalog name, the subject must equal its subcategory, and the category link must point to the catalog category.
2. Add the entry to the matching page under [categories](../categories/README.md) using the exact resource name and profile path. Its editorial one-line summary can differ from the catalog summary.
3. Adjust the displayed category count in **categories/README.md** and the overall starter-resource count in **resources/README.md**. The repository validator checks these counts and the two-way membership.

The two row shapes below are illustrations. Replace all placeholders and put each row in the correct index file rather than in the profile.

~~~text
| [{{name}}]({{id}}.md) | {{subcategory}} | [{{category_label}}](../categories/{{category_slug}}.md) |
- **[{{name}}](../resources/{{id}}.md):** {{category_summary}}
~~~

## Optional reproducible worked example

A substantial profile may include an additional section after **Try it** and before **Where to go next**. Use a descriptive heading beginning with **Worked example:** and the following subsections in order:

~~~text
## Worked example: descriptive, specific goal

### Prerequisites

### Steps

### Expected result

### Troubleshooting

### Evidence and execution status
~~~

Explain the actual tool versions, input and commands. Include a small original example, expected observations, and common problems. Clearly identify whether the example was executed locally or only reviewed against upstream documentation. Avoid copying unlicensed code, using sensitive data, or executing third-party submissions as part of documentation validation.

## Validate before creating a PR

From the repository root:

~~~sh
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
~~~

Both commands run without third-party Python packages. Fix any missing profile metadata, catalog mismatch, bad local link, stale index count or missing backlink. The validator checks structure and internal references, **not** the correctness of every statement or the health of external sites. Consult the [contribution guide](../CONTRIBUTING.md) and [editorial policy](EDITORIAL_POLICY.md) for evidence requirements.