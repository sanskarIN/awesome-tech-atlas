"""Parse explicit Markdown reference links for local, offline validation.

This deliberately supports the explicit [text][id] and collapsed [id][]
forms; ambiguous shortcut [id] syntax is outside its scope. No HTTP calls.
"""

from __future__ import annotations

import html
import re
from typing import NamedTuple

FENCE_RE = re.compile(r"^ {0,3}(\x60{3,}|~{3,})")
INLINE_CODE_RE = re.compile(r"(\x60+)(.*?)\1")
DEFINITION_START_RE = re.compile(r"^ {0,3}\[([^\]\n]+)\]:")
DEFINITION_RE = re.compile(
    r"^ {0,3}\[(?P<label>[^\]\n]+)\]:[ \t]*"
    r"(?P<dest><[^>\n]+>|[^\s<>]+)"
    r"(?:[ \t]+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?[ \t]*$"
)
USE_RE = re.compile(r"(?<!\\)!?\[(?P<text>[^\]\n]+)\]\[(?P<label>[^\]\n]*)\]")


class Definition(NamedTuple):
    destination: str
    line: int


class Usage(NamedTuple):
    label: str
    line: int


def normalize_label(label: str) -> str:
    """CommonMark-style case and whitespace insensitivity for labels."""
    return " ".join(html.unescape(label).split()).casefold()


def _without_html_comments(line: str, in_comment: bool) -> tuple[str, bool]:
    """Omit single-line and multiline HTML comments in Markdown prose."""
    result: list[str] = []
    cursor = 0
    while cursor < len(line):
        if in_comment:
            end = line.find("-->", cursor)
            if end < 0:
                return "".join(result), True
            cursor = end + 3
            in_comment = False
        else:
            start = line.find("<!--", cursor)
            if start < 0:
                result.append(line[cursor:])
                break
            result.append(line[cursor:start])
            cursor = start + 4
            in_comment = True
    return "".join(result), in_comment


def prose_lines(markdown: str):
    """Yield numbered non-fenced, non-comment prose with inline code hidden."""
    fence_char, fence_length = "", 0
    in_comment = False
    for number, raw in enumerate(markdown.splitlines(), 1):
        marker = FENCE_RE.match(raw)
        if fence_char:
            if marker and marker.group(1)[0] == fence_char and len(marker.group(1)) >= fence_length:
                fence_char, fence_length = "", 0
            continue
        if marker:
            fence_char, fence_length = marker.group(1)[0], len(marker.group(1))
            continue
        line, in_comment = _without_html_comments(raw, in_comment)
        if line.startswith(("    ", "\t")):  # indented code block
            continue
        yield number, INLINE_CODE_RE.sub("", line)


def scan_reference_links(markdown: str) -> tuple[
    dict[str, Definition], list[Usage], list[str]
]:
    """Collect definitions and usages, plus syntax diagnostics.

    Repeated definitions are errors even if destinations match: a reader
    cannot safely tell which of two conflicting links was intended.
    Definition order does not matter; users can reference later definitions.
    """
    definitions: dict[str, Definition] = {}
    usages: list[Usage] = []
    errors: list[str] = []

    for number, line in prose_lines(markdown):
        start = DEFINITION_START_RE.match(line)
        if start:
            label = normalize_label(start.group(1))
            if label.startswith("^"):  # footnotes are not reference links
                continue
            definition = DEFINITION_RE.fullmatch(line)
            if definition is None:
                errors.append(f"malformed reference definition on line {number}")
                continue
            if not label:
                errors.append(f"empty reference label on line {number}")
                continue
            if label in definitions:
                errors.append(
                    f"duplicate reference definition [{start.group(1)}] "
                    f"on line {number} (first on line {definitions[label].line})"
                )
                continue
            destination = definition.group("dest")
            if destination.startswith("<") and destination.endswith(">"):
                destination = destination[1:-1]
            definitions[label] = Definition(destination, number)
            continue

        for match in USE_RE.finditer(line):
            label = normalize_label(match.group("label") or match.group("text"))
            if not label or label.startswith("^"):
                continue
            usages.append(Usage(label, number))
    return definitions, usages, errors
