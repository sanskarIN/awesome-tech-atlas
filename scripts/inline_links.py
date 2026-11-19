"""Parse single-line Markdown link/image destinations with balanced punctuation.

Supports nested brackets in labels, balanced parentheses in URLs, escaped
punctuation, optional titles and angle-delimited destinations. This is not a
complete CommonMark parser and deliberately excludes multiline inline links.
"""

from __future__ import annotations

import string
from typing import NamedTuple


class InlineLink(NamedTuple):
    destination: str
    column: int


def _escaped(value: str, position: int) -> bool:
    count = 0
    position -= 1
    while position >= 0 and value[position] == "\\":
        count += 1
        position -= 1
    return bool(count % 2)


def _closing_bracket(value: str, start: int) -> int | None:
    depth = 1
    for index in range(start + 1, len(value)):
        if _escaped(value, index):
            continue
        if value[index] == "[":
            depth += 1
        elif value[index] == "]":
            depth -= 1
            if depth == 0:
                return index
    return None


def _unescape(text: str) -> str:
    result: list[str] = []
    index = 0
    while index < len(text):
        if (
            text[index] == "\\"
            and index + 1 < len(text)
            and text[index + 1] in string.punctuation
        ):
            result.append(text[index + 1])
            index += 2
        else:
            result.append(text[index])
            index += 1
    return "".join(result)


def _after_title(line: str, index: int) -> int | None:
    """Read optional space + title and return index after the closing parenthesis."""
    before_whitespace = index
    while index < len(line) and line[index] in " \t":
        index += 1
    if index >= len(line):
        return None
    if line[index] == ")":
        return index + 1
    if index == before_whitespace:
        return None

    opener = line[index]
    if opener not in ('"', "'", "("):
        return None
    closing = ")" if opener == "(" else opener
    index += 1
    depth = 1
    while index < len(line):
        if _escaped(line, index):
            index += 1
            continue
        char = line[index]
        if opener == "(" and char == "(":
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                index += 1
                while index < len(line) and line[index] in " \t":
                    index += 1
                return index + 1 if index < len(line) and line[index] == ")" else None
        index += 1
    return None


def _destination(line: str, opening: int) -> tuple[str, int] | None:
    index = opening + 1
    while index < len(line) and line[index] in " \t":
        index += 1
    if index >= len(line):
        return None
    if line[index] == ")":
        return "", index + 1

    if line[index] == "<":
        start = index + 1
        index = start
        while index < len(line):
            if line[index] == ">" and not _escaped(line, index):
                after = _after_title(line, index + 1)
                return (_unescape(line[start:index]), after) if after is not None else None
            if line[index] == "<" and not _escaped(line, index):
                return None
            index += 1
        return None

    start = index
    depth = 0
    while index < len(line):
        if _escaped(line, index):
            index += 1
            continue
        char = line[index]
        if char in " \t":
            if depth:
                return None
            after = _after_title(line, index)
            return (_unescape(line[start:index]), after) if after is not None else None
        if char == "(":
            depth += 1
        elif char == ")":
            if depth:
                depth -= 1
            else:
                return _unescape(line[start:index]), index + 1
        elif char == "<":
            return None
        index += 1
    return None


def scan_inline_links(line: str) -> list[InlineLink]:
    """Return recognized links and images, with unescaped destinations.

    An ambiguous or malformed apparent link is ignored rather than producing
    false validation errors for prose that resembles markup.
    """
    links: list[InlineLink] = []
    index = 0
    while index < len(line):
        if line[index] != "[" or _escaped(line, index):
            index += 1
            continue
        closing = _closing_bracket(line, index)
        if closing is None or closing + 1 >= len(line) or line[closing + 1] != "(":
            index += 1
            continue
        result = _destination(line, closing + 1)
        if result is None:
            index += 1
            continue
        destination, after = result
        links.append(InlineLink(destination, index + 1))
        index = after
    return links
