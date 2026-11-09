# React Learn

**Official source:** https://react.dev/learn  
**Type:** official guide  
**Category:** [Web development](../categories/web-development.md) · UI library  
**Last official-page inspection:** 2026-11-08

## Why it matters

Upstream React guide for components, props, state, rendering, and UI interactions.

## Good fit

Building interactive, reusable interfaces in JavaScript or TypeScript.

## Strength and trade-off

- **Strength:** Teaches component composition with small focused examples.
- **Limitation:** React is a UI library, not a full deployment stack; server rendering and routing require additional choices.

These are contextual selection notes, **not** independent speed, reliability, or security benchmarks.

## Try it

Follow Quick Start and build a component that displays a list from props.


## Worked example: an accessible stateful checklist

### Prerequisites

- A working React project that supports JSX and the `useState` Hook. Start from the [official installation guidance](https://react.dev/learn/installation) if you do not already have one.
- An existing app entry point that renders `App`; in many React starter projects the component lives in `src/App.jsx`.

### Steps

Replace your project's `App` component with this original JSX (adjust the path for your starter project):

~~~jsx
import { useState } from "react";

export default function App() {
  const [items, setItems] = useState([
    { id: 1, label: "Read the guide", done: false },
  ]);

  const finished = items.filter((item) => item.done).length;

  function toggle(id) {
    setItems((current) =>
      current.map((item) =>
        item.id === id ? { ...item, done: !item.done } : item
      )
    );
  }

  return (
    <main>
      <h1>Study checklist</h1>
      <p aria-live="polite">{finished} of {items.length} complete</p>
      <ul>
        {items.map((item) => (
          <li key={item.id}>
            <label>
              <input
                type="checkbox"
                checked={item.done}
                onChange={() => toggle(item.id)}
              />
              {item.label}
            </label>
          </li>
        ))}
      </ul>
    </main>
  );
}
~~~

Start the React development server as instructed by your project's tooling, then toggle the checkbox twice.

### Expected result

The page first announces **0 of 1 complete**. Checking the task updates it to **1 of 1 complete**; unchecking returns it to **0 of 1 complete**.

### Troubleshooting

- JSX must run through a configured React build tool; pasting it into an unconfigured plain JavaScript file will not work.
- If the page never updates, confirm the app renders your `App` and the checkbox `onChange` handler is connected.
- State is in memory only; reloading the page resets the checklist. There is no storage or synchronization.

### Evidence and execution status

- **Primary references:** [React: adding interactivity](https://react.dev/learn/adding-interactivity), [updating arrays in state](https://react.dev/learn/updating-arrays-in-state), and [installation](https://react.dev/learn/installation).
- **Reviewed:** 2026-11-09 (example-specific documentation). **Not runtime-tested here:** no configured React app/browser harness was used. The stated interaction is the expected behavior.
- This illustrates local UI state, not full-app accessibility or deployment readiness. The catalog's earlier official-source inspection date remains unchanged.

## Where to go next

- Read the [upstream documentation](https://react.dev/learn) for setup, compatible versions, and API details.
- **Alternative:** [MDN Learn web development](mdn-learn.md). MDN explains the underlying browser concepts that React components rely upon.

**Verification scope:** The linked upstream documentation was inspected on 2026-11-08. Runtime behavior, licensing details for specific distributions, and installation on every platform were not independently tested. Check the project's official terms and release information before reuse or deployment.
