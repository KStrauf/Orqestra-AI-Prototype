interface IdeaCoachProps {
  idea: string;
  platform: string;
  audience: string;
  outcome: string;
  tone: string;
  brief: string;
  onAudienceChange: (value: string) => void;
  onOutcomeChange: (value: string) => void;
  onToneChange: (value: string) => void;
  onBriefChange: (value: string) => void;
}

const audienceDefaults: Record<string, string> = {
  LinkedIn: "curious professionals",
  X: "people who follow your ideas",
  Instagram: "people who follow your work",
  Facebook: "your community",
  TikTok: "viewers who want a quick takeaway",
  YouTube: "viewers looking for a useful explanation",
  Lemon8: "people looking for practical inspiration",
  Snapchat: "friends and followers who want the quick version",
  Spotify: "listeners interested in the topic",
  "Amazon Podcasts": "listeners interested in the topic",
  "Apple Podcasts": "listeners interested in the topic",
  Wondery: "listeners interested in the topic",
};

function buildBrief({ idea, platform, audience, outcome, tone }: Omit<IdeaCoachProps, "brief" | "onAudienceChange" | "onOutcomeChange" | "onToneChange" | "onBriefChange">): string {
  const resolvedAudience = audience.trim() || audienceDefaults[platform] || "people who will find the idea useful";
  const resolvedOutcome = outcome.trim() || "Teach the audience something useful";
  const resolvedTone = tone.trim() || "Clear and practical";
  return [
    `Audience: ${resolvedAudience}`,
    `Outcome: ${resolvedOutcome}`,
    `Voice: ${resolvedTone}`,
    `Core idea: ${idea.trim()}`,
    "",
    "Draft angles:",
    "1. A clear explanation with one practical next step.",
    "2. A personal or reflective lesson connected to the idea.",
    "3. A useful how-to that makes the idea easier to apply.",
    "",
    "Assumption: The content should be useful to the selected audience without inventing facts that were not supplied.",
  ].join("\n");
}

export function IdeaCoach({
  idea,
  platform,
  audience,
  outcome,
  tone,
  brief,
  onAudienceChange,
  onOutcomeChange,
  onToneChange,
  onBriefChange,
}: IdeaCoachProps) {
  function shapeIdea() {
    if (!idea.trim()) return;
    onBriefChange(buildBrief({ idea, platform, audience, outcome, tone }));
  }

  return (
    <section className="idea-coach" aria-labelledby="idea-coach-title">
      <div className="idea-coach-heading">
        <div>
          <span className="eyebrow">IDEA COACH</span>
          <h3 id="idea-coach-title">Shape the idea before drafting</h3>
        </div>
        <span className="idea-coach-step">02 / 03</span>
      </div>
      <p className="idea-coach-intro">You do not need a finished post or a brand voice. Add a little context, or let the team make sensible assumptions.</p>
      <div className="idea-coach-fields">
        <label>
          <span>Who is this for?</span>
          <input value={audience} onChange={(event) => onAudienceChange(event.target.value)} placeholder={audienceDefaults[platform] || "Describe the audience"} />
        </label>
        <label>
          <span>What should it do?</span>
          <select value={outcome} onChange={(event) => onOutcomeChange(event.target.value)}>
            <option value="">Teach something useful</option>
            <option>Announce an update</option>
            <option>Start a conversation</option>
            <option>Build trust</option>
            <option>Drive people to take action</option>
          </select>
        </label>
        <label>
          <span>Voice</span>
          <select value={tone} onChange={(event) => onToneChange(event.target.value)}>
            <option>Clear and practical</option>
            <option>Warm and personal</option>
            <option>Bold and opinionated</option>
            <option>Educational</option>
          </select>
        </label>
      </div>
      <button className="secondary-button idea-coach-button" disabled={!idea.trim()} onClick={shapeIdea} type="button">
        {brief ? "Refresh starter brief" : "Shape my idea →"}
      </button>
      {brief && (
        <label className="brief-editor">
          <span>Starter brief <small>Edit anything before creating drafts.</small></span>
          <textarea value={brief} onChange={(event) => onBriefChange(event.target.value)} rows={8} />
        </label>
      )}
    </section>
  );
}
