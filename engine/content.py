"""Provider-neutral content intelligence primitives.

These structures are the runtime equivalent of the adapted content skills. They
keep brand context, platform guidance, hook options, and editorial checks
structured so the workflow can pass them between agents and persist them with a
run. They deliberately avoid engagement or virality guarantees.
"""

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
import re
from typing import Any


@dataclass(frozen=True)
class PlatformProfile:
    """Conservative, human-readable guidance for one content destination."""

    key: str
    label: str
    format: str
    max_chars: int | None = None
    guidance: str = ""


PLATFORM_PROFILES: dict[str, PlatformProfile] = {
    "linkedin": PlatformProfile(
        "linkedin", "LinkedIn", "professional post", 3000,
        "Lead with the useful idea, use readable paragraphs, and make the next step clear.",
    ),
    "x": PlatformProfile(
        "x", "X", "short post", 280,
        "Keep the opening concrete and the body compact. Avoid relying on hashtags.",
    ),
    "threads": PlatformProfile(
        "threads", "Threads", "short post", 500,
        "Use a conversational opening and one focused idea.",
    ),
    "bluesky": PlatformProfile(
        "bluesky", "Bluesky", "short post", 300,
        "Keep the post concise and self-contained.",
    ),
    "instagram": PlatformProfile(
        "instagram", "Instagram", "caption", 2200,
        "Make the first line useful on its own and treat media as a separate artifact.",
    ),
    "facebook": PlatformProfile(
        "facebook", "Facebook", "post", 63206,
        "Use plain language and a clear reason for the audience to care.",
    ),
    "tiktok": PlatformProfile(
        "tiktok", "TikTok", "caption or short-form script", 4000,
        "Separate the spoken hook, visual direction, and caption when creating video content.",
    ),
    "youtube": PlatformProfile(
        "youtube", "YouTube", "title, description, or script", None,
        "Clarify whether the output is a title, description, outline, or spoken script.",
    ),
    "lemon8": PlatformProfile(
        "lemon8", "Lemon8", "caption or guide", None,
        "Use a practical, visually scannable structure with a clear takeaway.",
    ),
    "snapchat": PlatformProfile(
        "snapchat", "Snapchat", "short caption or script", None,
        "Keep the idea immediate and specify any visual or spoken context.",
    ),
    "spotify": PlatformProfile(
        "spotify", "Spotify", "show or episode description", None,
        "State what listeners will learn or experience and identify the episode context.",
    ),
    "amazon podcasts": PlatformProfile(
        "amazon podcasts", "Amazon Podcasts", "show or episode description", None,
        "State what listeners will learn or experience and identify the episode context.",
    ),
    "apple podcasts": PlatformProfile(
        "apple podcasts", "Apple Podcasts", "show or episode description", None,
        "State what listeners will learn or experience and identify the episode context.",
    ),
    "wondery": PlatformProfile(
        "wondery", "Wondery", "show or episode description", None,
        "State what listeners will learn or experience and identify the episode context.",
    ),
    "general": PlatformProfile(
        "general", "General", "content draft", None,
        "Choose a clear audience, one useful idea, and one next step.",
    ),
}


def platform_profile(platform: str) -> PlatformProfile:
    """Return normalized guidance without rejecting new platform labels."""
    normalized = platform.strip().lower()
    return PLATFORM_PROFILES.get(
        normalized,
        PlatformProfile(normalized or "general", platform or "General", "content draft", None),
    )


@dataclass
class BrandProfile:
    """Optional creator context captured as a snapshot on each run."""

    profile_id: str = "default"
    name: str = ""
    audience: str = ""
    voice_traits: list[str] = field(default_factory=list)
    primary_cta: str = ""
    strong_opinions: list[str] = field(default_factory=list)
    story_vault: list[str] = field(default_factory=list)
    social_links: dict[str, str] = field(default_factory=dict)
    version: int = 1
    updated_at: str = ""


@dataclass
class HookCandidate:
    """A reviewable opening direction, not a promise of performance."""

    hook_id: str
    pattern: str
    text: str
    rationale: str
    variant: str = ""


@dataclass
class QualityReport:
    """A transparent pre-review quality check for the Reviewer stage."""

    platform: str
    overall: int
    scores: dict[str, int] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    method: str = "Deterministic checks and supplied context; not an engagement prediction."


@dataclass
class IdeaDirection:
    """One concrete content direction proposed from an incomplete idea."""

    direction_id: str
    title: str
    format: str
    why_it_fits: str
    opening: str
    next_step: str


@dataclass
class IdeaCoachResult:
    """A useful coaching result before the Specialist writes drafts."""

    recommended_direction_id: str
    recommendation: str
    audience: str
    outcome: str
    tone: str
    directions: list[IdeaDirection] = field(default_factory=list)
    sample_post: str = ""
    starter_brief: str = ""
    assumptions: list[str] = field(default_factory=list)


def coach_idea(
    idea: str,
    platform: str,
    audience: str = "",
    outcome: str = "",
    tone: str = "",
    brand_profile: BrandProfile | None = None,
) -> IdeaCoachResult:
    """Turn a rough idea into specific, editable content directions.

    This is intentionally a deterministic coaching pass. It gives demo mode a
    useful result without a provider and gives API mode a stable contract that
    can later be backed by an Architect completion without changing the UI.
    """
    clean_idea = " ".join(idea.strip().split()).rstrip(".")
    if not clean_idea:
        raise ValueError("idea cannot be empty")
    profile_audience = brand_profile.audience.strip() if brand_profile else ""
    resolved_audience = audience.strip() or profile_audience or "people who will find the idea useful"
    resolved_outcome = outcome.strip() or "Teach the audience something useful"
    resolved_tone = tone.strip() or "Clear and practical"
    profile_opinion = (
        brand_profile.strong_opinions[0].strip()
        if brand_profile and brand_profile.strong_opinions
        else ""
    )

    number_match = re.match(r"^(\d+)\s+(.+)$", clean_idea)
    topic = number_match.group(2) if number_match else clean_idea
    number_prefix = f"{number_match.group(1)} " if number_match else ""
    directions = [
        IdeaDirection(
            direction_id="practical-breakdown",
            title=f"Make {clean_idea} practical",
            format="Step-by-step post",
            why_it_fits=f"Show {resolved_audience} what to do with the idea instead of only naming it.",
            opening=f"{number_prefix}{topic}: start with the one choice that makes the biggest difference.",
            next_step="Give the reader one action they can try today.",
        ),
        IdeaDirection(
            direction_id="beginner-guide",
            title=f"Explain {clean_idea} for a beginner",
            format="Beginner-friendly explainer",
            why_it_fits=f"Translate the idea into plain language for {resolved_audience}.",
            opening=f"If {clean_idea.lower()} feels harder than it should, begin with this simple distinction.",
            next_step="Define the first step and one common mistake to avoid.",
        ),
        IdeaDirection(
            direction_id="point-of-view",
            title=f"Take a point of view on {clean_idea}",
            format="Opinion-led post",
            why_it_fits=profile_opinion or "Give the idea a clear position so the audience understands why it matters.",
            opening=profile_opinion or f"The useful question is not whether {clean_idea.lower()} matters. It is how to use it well.",
            next_step="Support the point of view with one example and invite a specific response.",
        ),
    ]
    recommended = directions[0]
    sample_post = (
        f"{recommended.opening}\n\n"
        f"If you are exploring {clean_idea.lower()}, do not stop at the label. "
        f"Explain what it helps someone do, when it is useful, and where to begin.\n\n"
        f"Start with one concrete example for {resolved_audience}. Then give one next step. "
        f"{recommended.next_step}"
    )
    starter_brief = "\n".join([
        f"Audience: {resolved_audience}",
        f"Outcome: {resolved_outcome}",
        f"Voice: {resolved_tone}",
        f"Core idea: {clean_idea}",
        f"Recommended direction: {recommended.title}",
        f"Format: {recommended.format}",
        f"Opening: {recommended.opening}",
        f"Next step: {recommended.next_step}",
        "",
        "Assumption: Replace general statements with supplied facts, examples, or personal experience before approval.",
    ])
    return IdeaCoachResult(
        recommended_direction_id=recommended.direction_id,
        recommendation=(
            f"Start with a practical breakdown for {resolved_audience}. "
            f"It gives the idea a clear promise and a useful next step for {platform}."
        ),
        audience=resolved_audience,
        outcome=resolved_outcome,
        tone=resolved_tone,
        directions=directions,
        sample_post=sample_post,
        starter_brief=starter_brief,
        assumptions=[
            "The idea is the source of truth until the user adds supporting material.",
            "Specific claims, names, and examples should be supplied or verified before approval.",
        ],
    )


def build_hook_candidates(
    goal: str,
    platform: str,
    variants: tuple[str, ...],
    audience: str = "",
    brand_profile: BrandProfile | None = None,
) -> list[HookCandidate]:
    """Create grounded hook directions from supplied context only."""
    idea = " ".join(goal.strip().split()).rstrip(".") or "this idea"
    audience_text = audience.strip() or (brand_profile.audience.strip() if brand_profile else "the audience")
    opinion = ""
    if brand_profile and brand_profile.strong_opinions:
        opinion = brand_profile.strong_opinions[0].strip().rstrip(".")

    templates = [
        ("clear claim", f"A clear way to approach {idea}: start with the audience's next useful step.",
         "Makes the promise and next action visible without adding unsupported claims."),
        ("audience question", f"What would {audience_text} need to understand before acting on {idea}?",
         "Turns a broad idea into a question the intended audience can answer."),
        ("practical lesson", f"The useful lesson behind {idea} is easier to apply when the first step is concrete.",
         "Frames the idea as a practical takeaway instead of a generic announcement."),
    ]
    if opinion:
        templates[2] = (
            "creator point of view",
            opinion,
            "Uses the creator's supplied point of view rather than inventing a contrarian claim.",
        )

    candidates: list[HookCandidate] = []
    selected_variants = variants or ("direct", "reflective", "educational")
    for index, variant in enumerate(selected_variants[:3]):
        pattern, text, rationale = templates[index % len(templates)]
        candidates.append(HookCandidate(
            hook_id=f"hook-{index + 1}",
            pattern=pattern,
            text=text,
            rationale=rationale,
            variant=variant,
        ))
    return candidates


def grade_drafts(
    drafts: list[Any],
    platform: str,
    material_supplied: bool,
    brand_profile: BrandProfile | None = None,
) -> QualityReport:
    """Run transparent checks that help a human reviewer focus attention."""
    profile = platform_profile(platform)
    issues: list[str] = []
    recommendations: list[str] = []
    violations = 0
    # Use the actual draft text for signals that can be explained to a human.
    # Grounding remains conservative when the source cannot be inspected here.
    draft_openings = {
        " ".join(str(getattr(draft, "text", "")).split()).lower()[:120]
        for draft in drafts
    }
    for draft in drafts:
        draft.constraint_violations.clear()
        if profile.max_chars is not None and draft.chars > profile.max_chars:
            message = f"{draft.variant} exceeds the {profile.label} guidance of {profile.max_chars} characters."
            draft.constraint_violations.append(message)
            violations += 1

    if not material_supplied:
        issues.append("The run started from an idea, so factual claims still need human verification.")
        recommendations.append("Add a source, example, or personal experience before approval if the draft makes specific claims.")
    if not brand_profile or not brand_profile.voice_traits:
        issues.append("No saved voice profile was supplied.")
        recommendations.append("Add a few voice traits or approved examples to make future drafts more personal.")
    if violations:
        issues.append(f"{violations} draft(s) need platform-length revision.")
        recommendations.append(f"Edit the selected draft to fit the {profile.label} format before approval.")
    if not recommendations:
        recommendations.append("Compare the hook, audience fit, and next step before making the human decision.")

    if len(drafts) > 1 and len(draft_openings) < len(drafts):
        issues.append("Two or more variants begin with the same opening, so the comparison may be less useful.")
        recommendations.append("Choose a direction with a meaningfully different opening before approval.")

    scores = {
        "grounding": 8 if material_supplied else 5,
        "platform_fit": 8 if not violations else 4,
        "voice_fit": 7 if brand_profile and brand_profile.voice_traits else 5,
        "actionability": min(
            9,
            6 + sum(
                1
                for draft in drafts
                if re.search(r"\b(next step|start with|try|invite|reply|comment|follow)\b", str(getattr(draft, "text", "")).lower())
            ) // max(1, len(drafts)),
        ),
    }
    overall = round(sum(scores.values()) / len(scores))
    return QualityReport(
        platform=profile.label,
        overall=overall,
        scores=scores,
        issues=issues,
        recommendations=recommendations,
    )


def brand_profile_from_dict(value: dict[str, Any] | None) -> BrandProfile | None:
    """Validate a loose API payload into the durable profile type."""
    if value is None:
        return None
    allowed = {field.name for field in BrandProfile.__dataclass_fields__.values()}
    return BrandProfile(**{key: item for key, item in value.items() if key in allowed})


def write_brand_profile(data_dir: Path, profile: BrandProfile) -> Path:
    """Persist the optional creator profile outside the run-record store."""
    path = data_dir / "brand-profile.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(profile), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def read_brand_profile(data_dir: Path) -> BrandProfile | None:
    """Read a saved creator profile, returning ``None`` when not configured."""
    path = data_dir / "brand-profile.json"
    if not path.exists():
        return None
    try:
        return brand_profile_from_dict(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return None
