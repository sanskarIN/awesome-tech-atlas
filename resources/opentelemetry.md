# OpenTelemetry documentation

**Official source:** https://opentelemetry.io/docs/  
**Type:** official docs  
**Category:** [Networking & distributed systems](../categories/networking-distributed-systems.md) · Application observability  
**Last official-page inspection:** 2026-11-14

## Why it matters

OpenTelemetry defines open, vendor-neutral approaches to application observability. Its documentation explains the relationship between traces, metrics and logs, along with instrumentation libraries and the Collector used to receive and export telemetry. It complements packet-level analysis with application-level evidence about requests and service behavior.

## Good fit

- Developers tracing an operation across components of an application they maintain.
- Engineers learning the difference between a metric measurement, a log event and a distributed trace.
- Teams designing a telemetry pipeline without tying instrumentation concepts to one backend vendor.

## Strength and trade-off

- **Strength:** The documentation organizes signals, instrumentation, propagation and export concepts across multiple language ecosystems.
- **Limitation:** Instrumentation introduces operational work and can expose sensitive values if attributes and exporters are poorly configured. Signal support and SDK maturity vary by language and version; check the relevant language-specific documentation.

These notes do not imply that OpenTelemetry by itself provides a complete dashboards/storage service or guarantees observability quality.

## Try it

Begin with the [signals overview](https://opentelemetry.io/docs/concepts/signals/). Sketch a request moving through two fictional services. Annotate one span per service, a duration metric, and one diagnostic log message; then ask which signal would answer a latency question versus an error-context question. If moving to code, follow the upstream getting-started page for your **specific language and installed version**, and choose a local console exporter first. Use synthetic input only; review privacy and retention before exporting real application data. This conceptual exercise was not run as a deployed telemetry system.

## Where to go next

- Read the [upstream documentation](https://opentelemetry.io/docs/) sections for instrumentation, Collector and language SDKs.
- **Alternative:** [Wireshark documentation](wireshark.md) is useful when investigating packet-level behavior on authorized traffic; it does not replace application instrumentation.

**Verification scope:** The OpenTelemetry documentation landing page and signals overview were inspected on 2026-11-14. The installation, specific SDK stability, third-party backends and data-handling behavior were not independently tested.
