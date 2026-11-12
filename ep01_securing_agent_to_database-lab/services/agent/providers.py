"""Pluggable Track A vs Track B adapters for auth, screening, audit, and layer toggles."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal
import yaml

TrackName = Literal["prototype", "track-a", "track-b"]


@dataclass
class LayerPolicy:
    """Per-request toggleable layers on Track A; always enforced on Track B."""

    L2_screening: bool = True
    L3_quarantine: bool = True
    L4_tool_boundary: bool = True
    L5_token_exchange: bool = True
    L8_human_approval: bool = True


@dataclass
class RuntimeConfig:
    track: TrackName
    model: object = "gemini-3.8-flash"
    db_backend: Literal["cloudsql", "bigquery"] = "cloudsql"
    layers: LayerPolicy = field(default_factory=LayerPolicy)


def load_profile_layers(profile_name: str, profiles_path: Path | None = None) -> LayerPolicy:
    path = profiles_path or Path(__file__).resolve().parents[2] / "config" / "profiles.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    raw = data["profiles"][profile_name]["layers"]
    return LayerPolicy(**raw)


def resolve_layers_for_track(
    track: TrackName,
    requested_profile: str = "governed",
    profiles_path: Path | None = None,
) -> LayerPolicy:
    """Track B ignores per-request switches and always enforces all layers."""
    if track == "track-b":
        return LayerPolicy()
    if track == "prototype":
        return load_profile_layers("naive", profiles_path)
    return load_profile_layers(requested_profile, profiles_path)
