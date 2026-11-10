# NumPy documentation

**Official source:** https://numpy.org/doc/stable/  
**Type:** official docs  
**Category:** [Scientific computing](../categories/scientific-computing.md) · Numerical arrays  
**Last official-page inspection:** 2026-11-08

## Why it matters

Official reference for N-dimensional arrays and numerical operations in Python.

## Good fit

Vectorized numerical calculations and the foundation of scientific Python workflows.

## Strength and trade-off

- **Strength:** Array broadcasting, indexing, and math routines simplify many numerical tasks.
- **Limitation:** Shape semantics, dtype choice, and floating-point precision can surprise beginners.

These are contextual selection notes, **not** independent speed, reliability, or security benchmarks.

## Try it

In a Python environment with NumPy installed, evaluate `np.arange(6).reshape(2, 3)`.

## Worked example: center sensor readings by column

### Prerequisites

- Python 3.10+ with a compatible NumPy installation; follow the [official NumPy install instructions](https://numpy.org/install/).
- Save the original example as `center_readings.py`. It contains its own small dataset and requires no downloads.

### Steps

Run `python center_readings.py` (or `python3` if appropriate):

~~~python
import numpy as np

readings = np.array([[10.0, 20.0, 30.0], [12.0, 18.0, 33.0]])
column_means = readings.mean(axis=0)
centered = readings - column_means

print("means:", column_means.tolist())
print("centered:", centered.tolist())
~~~

`axis=0` computes one mean per column. NumPy broadcasting then subtracts that three-element vector from each row of the two-dimensional array.

### Expected result

~~~text
means: [11.0, 19.0, 31.5]
centered: [[-1.0, 1.0, -1.5], [1.0, -1.0, 1.5]]
~~~

### Troubleshooting

- If `import numpy` fails, install NumPy into the same Python environment running the script.
- A `ValueError` about broadcasting usually means the operands' trailing dimensions are not compatible.
- Check `axis` and `shape` before using this pattern on other datasets. Missing values, integer overflow, floating-point precision, and inconsistent units need separate handling in real measurements.

### Evidence and execution status

- **Primary references:** [NumPy's `mean` reference](https://numpy.org/doc/stable/reference/generated/numpy.mean.html) and [broadcasting rules](https://numpy.org/doc/stable/user/basics.broadcasting.html).
- **Reviewed:** 2026-11-10 (example-specific documentation). **Executed locally:** Python 3.13.5 and NumPy 2.3.5; the output matched the example.
- This is a correctness demonstration with a tiny synthetic array, not a performance or data-science benchmark. The catalog's original official-page inspection date remains unchanged.

## Where to go next

- Read the [upstream documentation](https://numpy.org/doc/stable/) for setup, compatible versions, and API details.
- **Alternative:** [SciPy documentation](scipy.md). SciPy builds on NumPy arrays for higher-level scientific algorithms.

**Verification scope:** The linked upstream documentation was inspected on 2026-11-08. Runtime behavior, licensing details for specific distributions, and installation on every platform were not independently tested. Check the project's official terms and release information before reuse or deployment.
