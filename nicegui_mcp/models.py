from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class TopicInfo(BaseModel):
    name: str
    summary: str
    tags: list[str] = Field(default_factory=list)


class SearchHit(BaseModel):
    topic: str
    heading: str | None = None
    snippet: str
    score: float | None = None


class Finding(BaseModel):
    rule_id: str
    severity: Literal["error", "warning", "info"]
    title: str
    message: str
    suggestion: str | None = None
    span_hint: str | None = None
    confidence: Literal["high", "medium", "low"] = "medium"
    auto_fixability: Literal["safe", "partial", "guidance_only"] = "guidance_only"


class AnalysisResult(BaseModel):
    findings: list[Finding] = Field(default_factory=list)
    summary: str
    focus_applied: list[str] | None = None


class AppliedFix(BaseModel):
    rule_id: str
    description: str


class FixResult(BaseModel):
    updated_code: str
    applied_fixes: list[AppliedFix] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    recommend_reanalysis: bool


class GenerationResult(BaseModel):
    kind: str
    mode: str
    code: str
    notes: list[str] = Field(default_factory=list)


class ReviewIssue(BaseModel):
    rule_id: str
    severity: Literal["error", "warning", "info"]
    title: str
    message: str
    suggestion: str | None = None
    confidence: Literal["high", "medium", "low"] = "medium"
    auto_fixable: bool = False
    fixed: bool = False


class ReviewResult(BaseModel):
    issues: list[ReviewIssue] = Field(default_factory=list)
    fixed_code: str | None = None
    applied_fixes: list[AppliedFix] = Field(default_factory=list)
    improvement: str | None = None
    summary: str


class PatternResult(BaseModel):
    pattern_name: str
    title: str
    snippet: str
    explanation: str
    pitfalls: list[str] = Field(default_factory=list)
    version_notes: str | None = None
