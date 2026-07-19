# Orqestra Studio component style spec

This is the Phase 3 component contract for the light-theme Studio workspace. The implementation lives in `components.css` and `layout.css`; all visual values should resolve through `tokens.css` wherever a token exists.

## Shared rules

- Use `--bg-surface` cards on the `--bg-app` canvas with `--border-subtle`, `--radius-lg`, and `--shadow-sm`.
- Use `--space-4` or `--space-5` for compact control spacing and `--space-6` for card padding.
- Body copy uses `--text-md` or `--text-sm`; metadata uses `--text-xs` or `--text-sm` and stays visually quiet.
- Interactive controls are at least `--btn-height-md` high, expose a visible `:focus-visible` ring, and never communicate state through color alone.
- Indigo is reserved for primary actions, active navigation, selected drafts, and key product badges. Semantic colors describe workflow and decision states.
- Motion uses `--motion-fast`, `--motion-base`, and `--ease-standard`; reduced-motion users receive minimal transitions.

## Buttons

Selectors: `.primary-button`, `.topbar-action`, `.approve-button`, `.edit-button`, `.reject-button`, `.quiet-button`.

- Default height is `--btn-height-md`; compact actions may use `--btn-height-sm`.
- Primary actions use `--brand-600` with inverse text and `--brand-700` on hover.
- Approve uses `--success-600`, edit uses the warning surface/text pair, and reject uses `--danger-600`.
- Secondary actions use a surface background, `--border-default`, and `--text-default`.
- Buttons remain full-width in narrow decision/composer layouts.

## Cards

Selectors: `.composer-card`, `.helper-card`, `.history-page-card`, `.trace-page-card`, `.settings-card`, `.review-card`, `.decision-panel`, `.history-panel`.

- Use a white surface, subtle border, `--radius-lg`, `--shadow-sm`, and `--space-6` padding.
- Hover/elevated states use `--shadow-md` sparingly; selected states use a stronger brand border and a light brand tint.
- Cards provide grouping and hierarchy, not decorative color blocks.

## Side navigation

Selectors: `.sidebar`, `.nav-item`, `.sidebar-footer`.

- The rail is `--sidebar-width` on desktop and uses `--bg-subtle` for orientation.
- Navigation rows use `--btn-height-sm`, `--radius-md`, and muted text by default.
- Active and hover rows use `--brand-50` and `--brand-700`; the active state includes both text and icon treatment.
- The human-gate footer is separated by the subtle border and remains quieter than the primary workspace.
- The rail is hidden below the mobile breakpoint in favor of `.mobile-nav`.

## Pipeline stepper

Selectors: `.agent-pipeline`, `.pipeline-step`, `.pipeline-number`, `.pipeline-line`.

- The stepper is a bordered surface with `--radius-lg`, `--space-4` padding, and horizontal stage flow.
- Stage numbers are pill-shaped and use the brand fill for the active/current stage; inactive stages use the subtle surface treatment.
- Connector lines use `--border-default` and do not compete with stage labels.
- On small screens the stepper remains readable through horizontal scrolling rather than collapsing stage meaning.

## Draft cards

Selectors: `.draft-list`, `.draft-card`, `.draft-card.selected`, `.decision-tag`.

- Drafts are selectable buttons with consistent minimum height, readable excerpts, and a quiet character-count footer.
- Hover uses the surface-hover tint and `--shadow-md`; selected uses `--brand-600` border plus `--brand-50` tint.
- Decision tags map approve to success, edit to warning, and reject to danger.
- The selected draft must be distinguishable by border, tint, and selection context—not color alone.

## Decision bar

Selectors: `.decision-panel`, `.decision-actions`, `.decision-form`, `.decision-recorded`.

- The decision bar is a review-first card directly below the selected draft.
- Approve, edit, and reject remain visually distinct and use the semantic mappings above.
- Edit preserves the draft in a textarea; reject requires a rationale before submission.
- A recorded decision becomes a success notice and the controls no longer imply that the same decision is pending.
- On mobile, actions stack full-width for safe touch targets.

## Responsive and accessibility contract

- Desktop uses the shell’s left rail, center workspace, and right context panel.
- Tablet reduces the rail/context widths; mobile uses one pane and the fixed bottom navigation.
- Do not rely on color alone for status or selection; labels and copy remain present.
- Preserve readable draft line length and keep important actions in a consistent location.
