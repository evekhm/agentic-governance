"""Tool output normalization, fail-closed Model Armor screening, and Markdown AST stripping."""

from __future__ import annotations

import base64
import re
import unicodedata
from typing import Any

ZERO_WIDTH_RE = re.compile(r"[\u200b-\u200f\u202a-\u202e\u2060-\u206f\U000e0000-\U000e007f]")
B64_RUN_RE = re.compile(r"(?:^|\s)([A-Za-z0-9+/]{24,}={0,2})(?=\s|$)")
MARKDOWN_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\((https?://[^)\s]+)\)")


def normalize_for_screening(raw_text: str) -> str:
    """Canonicalizes Unicode (NFKC), strips invisible tag chars, and appends decoded Base64 runs."""
    text = unicodedata.normalize("NFKC", raw_text)
    text = ZERO_WIDTH_RE.sub("", text)
    decoded_extras: list[str] = []
    for match in B64_RUN_RE.findall(text):
        try:
            decoded = base64.b64decode(match, validate=True).decode("utf-8", errors="ignore")
            if decoded and decoded.isprintable():
                decoded_extras.append(decoded)
        except Exception:
            pass
    return text + ("\n[DECODED_B64]: " + " ".join(decoded_extras) if decoded_extras else "")


def strip_external_markdown_images(markdown_text: str) -> tuple[str, list[str]]:
    """Removes external Markdown image links (`![alt](https://...)`) to block T6 exfiltration."""
    stripped_urls: list[str] = []

    def _replace(match: re.Match[str]) -> str:
        alt, url = match.group(1), match.group(2)
        stripped_urls.append(url)
        return f"[blocked-external-image: {alt or 'img'}]"

    return MARKDOWN_IMAGE_RE.sub(_replace, markdown_text), stripped_urls


def screen_tool_output_fail_closed(
    tool_response_json: str,
    template_name: str,
    client: Any | None = None,
) -> str:
    """Screens normalized DB tool rows via Model Armor; fails closed on ANY error or match."""
    from google.cloud import modelarmor_v1

    ma_client = client or modelarmor_v1.ModelArmorClient()
    canonical = normalize_for_screening(tool_response_json)
    resp = ma_client.sanitize_model_response(
        request=modelarmor_v1.SanitizeModelResponseRequest(
            name=template_name,
            model_response_data=modelarmor_v1.DataItem(text=canonical),
        )
    )
    res = resp.sanitization_result
    # Fail closed: require BOTH complete invocation AND zero filter matches.
    if (
        res.invocation_result != modelarmor_v1.InvocationResult.SUCCESS
        or res.filter_match_state != modelarmor_v1.FilterMatchState.NO_MATCH_FOUND
    ):
        raise ValueError("Blocked by Model Armor egress policy (fail-closed)")
    return tool_response_json
