# MDN Learn web development

**Official source:** https://developer.mozilla.org/en-US/docs/Learn_web_development  
**Type:** learning guide  
**Category:** [Web development](../categories/web-development.md) · Web fundamentals  
**Last official-page inspection:** 2026-11-08

## Why it matters

MDN's structured curriculum for HTML, CSS, accessibility, JavaScript, and web fundamentals.

## Good fit

Learning the web platform before a frontend framework.

## Strength and trade-off

- **Strength:** Progressive modules make standards and accessibility approachable.
- **Limitation:** It is not a framework-specific deployment or backend operations manual.

These are contextual selection notes, **not** independent speed, reliability, or security benchmarks.

## Try it

Complete the introductory HTML module and publish a simple static page locally.

## Worked example: validate an email-shaped field without submitting

### Prerequisites

- A modern browser and a text editor. Save this original demonstration as `email-check.html` and open it locally.
- Use **made-up sample input only**, such as `demo@example.invalid`. This page does not contain a form submission or make network requests.

### Steps

This page pairs a visible label with a required email field and a button that explicitly checks the browser's built-in constraints:

~~~html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Practice email format check</title>
</head>
<body>
  <label for="email">Practice email (format only)</label>
  <input id="email" type="email" required>
  <button id="check" type="button">Check locally</button>
  <p id="status" role="status"></p>
  <script>
    const email = document.querySelector("#email");
    const status = document.querySelector("#status");
    document.querySelector("#check").addEventListener("click", () => {
      status.textContent = email.reportValidity()
        ? "Format accepted; nothing was sent."
        : "Please correct the field.";
    });
  </script>
</body>
</html>
~~~

Enter an invalid value, choose **Check locally**, then try a syntactically valid sample address. The page never sends the input to a server.

### Expected result

For an empty or malformed email field, the browser reports a constraint error and the status paragraph asks for a correction. For `demo@example.invalid`, the status text says `Format accepted; nothing was sent.` Exact native validation prompts vary by browser and language.

### Troubleshooting

- If nothing happens when the button is selected, ensure JavaScript is enabled and check the developer console for typing errors.
- `type="email"` checks syntax, **not** whether an address exists, belongs to someone, or is safe to store.
- Client-side validation is for user feedback. A real server must independently validate submitted data, and this demonstration is not a signup or authentication flow.

### Evidence and execution status

- **Primary references:** [MDN: client-side form validation](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Form_validation) and [HTMLInputElement.reportValidity](https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/reportValidity).
- **Reviewed:** 2026-11-13 (example-specific documentation). **Not runtime-tested here:** interactive browser and assistive-technology behavior requires a manual browser pass.
- The expected behavior is based on the documented browser APIs. This does not replace the outstanding real-browser accessibility QA in issue #10 or refresh the catalog's original upstream inspection date.

## Where to go next

- Read the [upstream documentation](https://developer.mozilla.org/en-US/docs/Learn_web_development) for setup, compatible versions, and API details.
- **Alternative:** [React Learn](react.md). React is a later option once HTML, CSS, and JavaScript basics are clear.

**Verification scope:** The linked upstream documentation was inspected on 2026-11-08. Runtime behavior, licensing details for specific distributions, and installation on every platform were not independently tested. Check the project's official terms and release information before reuse or deployment.
