# Editorial and verification policy

## Inclusion criteria

A resource belongs in Awesome Tech Atlas when it is relevant to a defined technology topic, technically useful, discoverable through an authoritative upstream page, and teachable with a clear "use it for" explanation and a trade-off. A curated **reference** is preferable to a vendor slogan.

Resource profiles identify the **kind** of resource and its intended audience. Community sites may be included, but must say they are third-party, not official documentation. Avoid dead projects unless historical value is the explicit reason for inclusion.

## Evidence classes

- **Verified source:** a maintainer or contributor inspected the listed official URL and its relevant content on the date in the catalog. This is *not* a fresh check of every link within that site.
- **Documented fact:** a statement supported by the named upstream documentation (e.g. language support, APIs).
- **Editorial assessment:** an explicitly contextual judgment such as "good for a small embedded database"; it is not a universal performance ranking.
- **Not checked:** runtime behavior, recent releases, installation on a given system, benchmarks, or license nuances unless specifically researched.

Do not call an entry "fully verified" solely because an HTTP request succeeded. Access to an official page does not prove code safety, long-term maintenance, benchmark performance, or downstream license compatibility.

## Resource fields

The machine-readable [catalog](../data/resources.json) provides minimal, checkable identity and navigation fields. Each human-readable [profile](../resources/README.md) holds **purpose, use cases, trade-offs, practical first step, and alternatives**. Individual pages may add platform/installation/licensing notes where useful and reliable, but never infer a license for a separate distribution from a general product name.

Use ISO dates (UTC calendar date) for `verified_on`; only update after reinspection. Avoid recording a future date.

## Maintenance

The [validation workflow](../.github/workflows/validate.yml) checks catalog shape, duplicates, required profiles, links, and local navigation. External URL checks are a separate network-dependent workflow; HTTP denials or rate limits require human assessment, not blind deletion.

A resource with an old verification date is **stale**, not necessarily broken. Prioritize checking reported failures, outdated APIs, moved documentation, and important categories. Archive or remove an entry only after understanding the cause.

## Copyright and attribution

Summaries and examples here are original. An upstream documentation link is not permission to copy its contents. The repository's CC0 dedication applies **only** to original content contributed here; upstream code/docs/graphics keep their own licenses and trademark protections.
