# OWASP Cheat Sheet Series

**Official source:** https://cheatsheetseries.owasp.org/  
**Type:** community reference  
**Category:** [Cybersecurity & secure engineering](../categories/cybersecurity-secure-engineering.md) · Defensive application security  
**Last official-page inspection:** 2026-11-08

## Why it matters

OWASP's practical references for secure application design, authentication, authorization, and other defensive topics.

## Good fit

Improving security requirements and reviewing application design decisions.

## Strength and trade-off

- **Strength:** Topic-focused guidance can be applied during development and code review.
- **Limitation:** Guidance is not a substitute for project-specific threat modeling, review, and testing.

These are contextual selection notes, **not** independent speed, reliability, or security benchmarks.

## Try it

Read the Authentication and Access Control cheat sheets; compare recommendations with your application's requirements.


## Worked example: test a default-deny authorization rule

### Prerequisites

- Python 3.10+ (standard library only).
- A local editor; save this original *educational policy test* as \`test_document_policy.py\`. It makes no HTTP requests.

### Steps

Run \`python -m unittest -v test_document_policy.py\` from the containing directory:

~~~python
import unittest


def can_read_document(authenticated_user_id: str | None, owner_id: str) -> bool:
    return authenticated_user_id is not None and authenticated_user_id == owner_id


class PolicyTests(unittest.TestCase):
    def test_owner_is_allowed(self):
        self.assertTrue(can_read_document("reader-1", "reader-1"))

    def test_other_user_is_denied(self):
        self.assertFalse(can_read_document("reader-2", "reader-1"))

    def test_missing_identity_is_denied(self):
        self.assertFalse(can_read_document(None, "reader-1"))


if __name__ == "__main__":
    unittest.main()
~~~

### Expected result

The runner reports three passing tests and finishes with \`OK\`. In particular, an unrelated or missing user identity does not gain access.

### Troubleshooting

- If the test module is not found, confirm its filename and current directory.
- If an assertion fails after editing the policy, review the intended access rules rather than automatically weakening the test.
- **Security boundary:** This helper is *not* production authorization middleware. A real server must derive identity from trusted authentication/session state, resolve ownership from trusted storage, and enforce authorization on **every** relevant request. Never treat caller-supplied IDs or a UI check as proof of permission.

### Evidence and execution status

- **Primary reference:** [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html), especially deny-by-default, per-request checks, and authorization unit tests.
- **Reviewed:** 2026-11-09 (example-specific documentation). **Executed locally:** Python 3.13.5, with three passing \`unittest\` cases.
- A small passing test suite cannot establish that a deployed application is secure. The catalog's earlier official-source inspection date remains unchanged.

## Where to go next

- Read the [upstream documentation](https://cheatsheetseries.owasp.org/) for setup, compatible versions, and API details.
- **Alternative:** [GitHub Actions documentation](github-actions.md). Automated checks can complement, but cannot replace, secure architecture and review.

**Verification scope:** The linked upstream documentation was inspected on 2026-11-08. Runtime behavior, licensing details for specific distributions, and installation on every platform were not independently tested. Check the project's official terms and release information before reuse or deployment.
