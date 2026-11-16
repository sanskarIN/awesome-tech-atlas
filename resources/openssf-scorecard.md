# OpenSSF Scorecard

**Official source:** https://scorecard.dev/  
**Type:** official guide (Open Source Security Foundation project)  
**Category:** [Cybersecurity & secure engineering](../categories/cybersecurity-secure-engineering.md) · Open-source security practices  
**Last official-page inspection:** 2026-11-16

## Why it matters

OpenSSF Scorecard assesses observable repository security practices, including aspects of governance, dependencies and build processes. Its descriptions of individual checks can help maintainers spot gaps worth investigating, rather than relying solely on a project's popularity or a single aggregate number.

## Good fit

- Maintainers reviewing documented security policies, branch protection and CI permission practices.
- Open-source contributors gathering questions for a repository maintenance review.
- Teams triaging supply-chain concerns with manual follow-up and source evidence.

## Strength and trade-off

- **Strength:** The upstream project documents its checks and provides remediation guidance, supporting evidence-based discussions.
- **Limitation:** A score is **not a security audit, dependency approval or guarantee of safety**. Findings depend on observable signals and project circumstances, and need human interpretation. A seemingly good score does not prove that code or releases are free of vulnerabilities.

Never use Scorecard as a universal ranking or a sole trust decision.

## Try it

Read [the official Scorecard page](https://scorecard.dev/) and inspect how its **Security Policy**, **Branch Protection**, and **Token Permissions** checks are described. For a fictional or locally maintained repository, write down which observable evidence you would review and why each check matters. Do not change repository permissions just to improve a score. This documentation exercise involved **no live scan or assessment**.

## Where to go next

- Examine the check descriptions on [OpenSSF Scorecard](https://scorecard.dev/) before choosing any integration.
- **Alternative:** [OWASP Cheat Sheet Series](owasp-cheatsheets.md) offers application-design guidance; [GitHub Actions documentation](github-actions.md) explains workflow permissions, not security certification.

**Verification scope:** The OpenSSF Scorecard site and its check overview were inspected on 2026-11-16. No live scan, vulnerability audit, specific security score or project assessment was independently verified.
