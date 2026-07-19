import { useState, type FormEvent } from "react";

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

export function SettingsPage({ environmentLabel, provider, model }: SettingsPageProps) {
  const [profiles, setProfiles] = useState<ProfileLinks>(loadProfileLinks);
  const [saved, setSaved] = useState(false);

  function updateProfile(key: ProfileKey, value: string) {
    setProfiles((current) => ({ ...current, [key]: value }));
    setSaved(false);
  }

  function saveProfiles(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    window.localStorage.setItem(profileStorageKey, JSON.stringify(profiles));
    setSaved(true);
  }

  return (
    <div className="page-stack">
      <header className="page-header"><div><span className="eyebrow">SETTINGS</span><h1>Studio environment.</h1><p>Understand the active runtime and keep your publishing context ready for review.</p></div></header>
      <div className="settings-grid">
        <section className="settings-card"><span className="eyebrow">ENVIRONMENT</span><h2>{environmentLabel}</h2><div className="settings-fact"><span>Provider</span><strong>{provider}</strong></div><div className="settings-fact"><span>Model</span><strong>{model}</strong></div><p className="settings-note">Provider selection is owned by the backend service. The frontend reports the active run metadata.</p></section>
        <section className="settings-card safety-card"><span className="eyebrow">SAFETY</span><h2>Human gate enabled</h2><p>Orqestra creates reviewable content. Nothing publishes automatically, and every draft decision is recorded with the run.</p><div className="safety-badge">⌑ Human approval required</div></section>
        <section className="settings-card settings-social-card" aria-labelledby="social-profiles-title">
          <div className="settings-social-heading"><div><span className="eyebrow">CONTENT CONTEXT</span><h2 id="social-profiles-title">Social profile links</h2></div><span className="settings-note">Optional</span></div>
          <p className="settings-note">Add the profiles and channels you create for. These links are saved in this browser for the current MVP and are not sent to an inference provider.</p>
          <form className="social-profile-form" onSubmit={saveProfiles}>
            <div className="social-profile-grid">
              {profileFields.map(([key, label, placeholder]) => (
                <label className="social-profile-field" key={key}>
                  <span>{label}</span>
                  <input type="url" value={profiles[key]} onChange={(event) => updateProfile(key, event.target.value)} placeholder={placeholder} aria-label={`${label} profile link`} />
                </label>
              ))}
            </div>
            <div className="settings-save-row"><span className="settings-note">{saved ? "Profile links saved in this browser." : "You can add these later."}</span><button className="primary-button" type="submit">Save profile links</button></div>
          </form>
        </section>
      </div>
    </div>
  );
}
