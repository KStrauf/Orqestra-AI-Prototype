import { useEffect, useState, type FormEvent } from "react";
import { getBrandProfile, isDemoMode, saveBrandProfile } from "../api";

interface SettingsPageProps {
  environmentLabel: string;
  provider: string;
  model: string;
}

const profileFields = [
  ["linkedin", "LinkedIn", "https://linkedin.com/in/your-profile"],
  ["lemon8", "Lemon8", "https://www.lemon8-app.com/@your-profile"],
  ["tiktok", "TikTok", "https://www.tiktok.com/@your-profile"],
  ["youtube", "YouTube", "https://youtube.com/@your-channel"],
  ["facebook", "Facebook", "https://facebook.com/your-page"],
  ["x", "X", "https://x.com/your-handle"],
  ["instagram", "Instagram", "https://instagram.com/your-profile"],
  ["snapchat", "Snapchat", "https://www.snapchat.com/add/your-profile"],
  ["spotify", "Spotify", "https://open.spotify.com/show/your-show"],
  ["amazon-podcasts", "Amazon Podcasts", "https://music.amazon.com/podcasts/your-show"],
  ["apple-podcasts", "Apple Podcasts", "https://podcasts.apple.com/podcast/your-show"],
  ["wondery", "Wondery", "https://wondery.com/shows/your-show"],
] as const;

type ProfileKey = (typeof profileFields)[number][0];
type ProfileLinks = Record<ProfileKey, string>;

const emptyProfileLinks = profileFields.reduce((links, [key]) => {
  links[key] = "";
  return links;
}, {} as ProfileLinks);

const profileStorageKey = "orqestra-studio-social-profiles";
const contextStorageKey = "orqestra-studio-brand-context";

interface CreatorContext {
  audience: string;
  voice: string;
  primaryCta: string;
  strongOpinion: string;
  story: string;
  profiles: ProfileLinks;
}

function loadProfileLinks(): ProfileLinks {
  if (typeof window === "undefined") return { ...emptyProfileLinks };
  try {
    const stored = JSON.parse(window.localStorage.getItem(profileStorageKey) || "{}");
    return profileFields.reduce((links, [key]) => {
      links[key] = typeof stored[key] === "string" ? stored[key] : "";
      return links;
    }, { ...emptyProfileLinks });
  } catch {
    return { ...emptyProfileLinks };
  }
}

function loadCreatorContext(): CreatorContext {
  const links = loadProfileLinks();
  if (typeof window === "undefined") return { audience: "", voice: "", primaryCta: "", strongOpinion: "", story: "", profiles: links };
  try {
    const stored = JSON.parse(window.localStorage.getItem(contextStorageKey) || "{}");
    return {
      audience: typeof stored.audience === "string" ? stored.audience : "",
      voice: typeof stored.voice === "string" ? stored.voice : "",
      primaryCta: typeof stored.primaryCta === "string" ? stored.primaryCta : "",
      strongOpinion: typeof stored.strongOpinion === "string" ? stored.strongOpinion : "",
      story: typeof stored.story === "string" ? stored.story : "",
      profiles: links,
    };
  } catch {
    return { audience: "", voice: "", primaryCta: "", strongOpinion: "", story: "", profiles: links };
  }
}

export function SettingsPage({ environmentLabel, provider, model }: SettingsPageProps) {
  const [context, setContext] = useState<CreatorContext>(loadCreatorContext);
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);
  const [socialOpen, setSocialOpen] = useState(() => Object.values(loadCreatorContext().profiles).some(Boolean));

  useEffect(() => {
    if (isDemoMode) return;
    getBrandProfile()
      .then((profile) => {
        if (!profile) return;
        setContext((current) => ({
          audience: profile.audience,
          voice: profile.voice_traits.join(", "),
          primaryCta: profile.primary_cta,
          strongOpinion: profile.strong_opinions[0] || "",
          story: profile.story_vault[0] || "",
          profiles: profileFields.reduce((links, [key]) => {
            links[key] = profile.social_links[key] || current.profiles[key];
            return links;
          }, { ...emptyProfileLinks }),
        }));
      })
      .catch(() => {
        // The settings form remains usable if an older backend has no profile resource.
      });
  }, []);

  function updateProfile(key: ProfileKey, value: string) {
    setContext((current) => ({ ...current, profiles: { ...current.profiles, [key]: value } }));
    setSaved(false);
  }

  function updateContext(key: keyof Omit<CreatorContext, "profiles">, value: string) {
    setContext((current) => ({ ...current, [key]: value }));
    setSaved(false);
  }

  async function saveProfiles(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    try {
      if (isDemoMode) {
        window.localStorage.setItem(profileStorageKey, JSON.stringify(context.profiles));
        window.localStorage.setItem(contextStorageKey, JSON.stringify(context));
      } else {
        await saveBrandProfile({
          profile_id: "default",
          name: "",
          audience: context.audience,
          voice_traits: context.voice.split(",").map((item) => item.trim()).filter(Boolean),
          primary_cta: context.primaryCta,
          strong_opinions: context.strongOpinion ? [context.strongOpinion] : [],
          story_vault: context.story ? [context.story] : [],
          social_links: context.profiles,
          version: 1,
          updated_at: "",
        });
      }
      setSaved(true);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="page-stack">
      <header className="page-header"><div><span className="eyebrow">SETTINGS</span><h1>Studio environment.</h1><p>Understand the active runtime and keep your publishing context ready for review.</p></div></header>
      <div className="settings-grid">
        <section className="settings-card"><span className="eyebrow">ENVIRONMENT</span><h2>{environmentLabel}</h2><div className="settings-fact"><span>Provider</span><strong>{provider}</strong></div><div className="settings-fact"><span>Model</span><strong>{model}</strong></div><p className="settings-note">Provider selection is owned by the backend service. The frontend reports the active run metadata.</p></section>
        <section className="settings-card safety-card"><span className="eyebrow">SAFETY</span><h2>Human gate enabled</h2><p>Orqestra creates reviewable content. Nothing publishes automatically, and every draft decision is recorded with the run.</p><div className="safety-badge">⌑ Human approval required</div></section>
        <section className="settings-card settings-social-card" aria-labelledby="creator-profile-title">
          <div className="settings-social-heading"><div><span className="eyebrow">CREATOR CONTEXT</span><h2 id="creator-profile-title">Teach the team how to help you.</h2></div><span className="settings-note">Optional</span></div>
          <p className="settings-note">Give Orqestra a little context about your audience, voice, and point of view. The team uses it to make drafts more specific and more like you.</p>
          <form className="social-profile-form" onSubmit={saveProfiles}>
            <div className="brand-context-grid">
              <label className="brand-context-primary"><span>Who do you create for?</span><input value={context.audience} onChange={(event) => updateContext("audience", event.target.value)} placeholder="e.g. early-stage builders" /></label>
              <label className="brand-context-primary"><span>Voice traits</span><input value={context.voice} onChange={(event) => updateContext("voice", event.target.value)} placeholder="e.g. warm, direct, practical" /></label>
              <label className="brand-context-primary"><span>Primary call to action</span><input value={context.primaryCta} onChange={(event) => updateContext("primaryCta", event.target.value)} placeholder="e.g. Invite people to try the idea" /></label>
              <label className="brand-context-wide"><span>Point of view</span><textarea value={context.strongOpinion} onChange={(event) => updateContext("strongOpinion", event.target.value)} rows={2} placeholder="What do you believe about your topic?" /></label>
              <label className="brand-context-wide"><span>Story or example to remember</span><textarea value={context.story} onChange={(event) => updateContext("story", event.target.value)} rows={2} placeholder="A personal moment, result, or example the team may reference" /></label>
            </div>
            <details className="settings-social-disclosure" open={socialOpen} onToggle={(event) => setSocialOpen(event.currentTarget.open)}>
              <summary><span><strong>Social channels</strong><small>Optional links help the team format content for the places you publish.</small></span><em>{Object.values(context.profiles).filter(Boolean).length} connected</em></summary>
              <div className="settings-social-disclosure-body">
                <p className="settings-note">These links are creator context, not publishing credentials. Add only the channels you want Orqestra to consider.</p>
                <div className="social-profile-grid">
                  {profileFields.map(([key, label, placeholder]) => (
                    <label className="social-profile-field" key={key}>
                      <span>{label}</span>
                      <input type="url" value={context.profiles[key]} onChange={(event) => updateProfile(key, event.target.value)} placeholder={placeholder} aria-label={`${label} profile link`} />
                    </label>
                  ))}
                </div>
              </div>
            </details>
            <div className="settings-save-row"><span className={`settings-save-status ${saved ? "saved" : ""}`} role="status">{saved ? (isDemoMode ? "Saved in this browser." : "Saved to Studio.") : "Changes apply to your next run."}</span><button className="primary-button" disabled={saving} type="submit">{saving ? "Saving…" : "Save creator context"}</button></div>
          </form>
        </section>
      </div>
    </div>
  );
}
