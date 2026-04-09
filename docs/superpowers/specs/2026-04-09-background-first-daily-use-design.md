# Background-First Daily-Use Design

## Goal

Optimize the Windows Pomodoro app for personal daily use where the user wants to stay aware of session changes without the app getting in the way. The main change is to shift the app from window-first behavior to tray-first behavior with configurable notifications.

## Current State

The current app works well as a lightweight countdown timer, but it still behaves like a foreground application:

- Session completion restores the main window immediately.
- Session progression behavior is mostly hardcoded in the UI layer.
- The tray icon exists, but it is not yet the primary control surface.
- Notifications are present but not configurable enough for different interruption preferences.

This is acceptable for a simple timer, but it creates unnecessary attention cost for everyday background use.

## Non-Goals

- Rebuilding the application around a new GUI framework
- Adding team features, cloud sync, or task/project management
- Broad public-release polish that does not improve personal daily use
- Large analytics or reporting systems beyond lightweight personal history

## User Experience Direction

The product should behave like a background utility:

- The tray is the default interaction point during normal use.
- The main window is secondary and used mainly for setup or occasional inspection.
- Alerts should inform the user without forcing focus changes.
- Escalation should be configurable so missed transitions can be noticed without becoming noisy.

## Recommended Approach

Recommended approach: tray-first minimal UI with configurable notification escalation.

Why this approach:

- It directly addresses the stated problem of staying aware without interruption.
- It improves the app during every session instead of only at setup time.
- It fits the current architecture and can be implemented incrementally.
- It avoids over-investing in features like mini mode before the core background workflow is solid.

Alternative approaches considered:

1. Notification-first only
   This improves awareness, but without richer tray controls the user still needs to reopen the app too often.
2. Always-visible mini mode
   This reduces click cost, but it still consumes visual attention and does not fit the stated goal as well as tray-first operation.

## Product Design

### Primary Interaction Model

The app should be usable for an entire workday without reopening the main window for routine actions.

The tray icon should provide:

- Current phase via icon color
- Current status via tooltip text
- Common actions via tray menu

The window should no longer be restored automatically at the end of each session by default.

### Tray Behavior

The tray becomes the operational center for day-to-day use.

Tooltip examples:

- `Work - 12:34 left`
- `Paused - Short Break - 04:10 left`

Menu actions:

- `Start/Pause`
- `Skip`
- `Reset`
- `+1 minute`
- `Show Window`
- `Settings`
- `Quit`

Future-ready action, if reminder state is active:

- `Snooze 3 min`

### Session Completion Policy

At phase completion, the app should follow a configurable policy instead of one hardcoded sequence.

Completion flow:

1. Trigger the configured alert behavior
2. Record stats if the completed phase was a work session
3. Advance to the next phase
4. Start the next phase only if enabled
5. Restore the window only if enabled

Default behavior for personal daily use:

- Do not restore the window
- Start the next phase automatically
- Show toast notification
- Play sound only if explicitly enabled

### Notification Modes

Add a small set of modes instead of many overlapping toggles:

- `toast`
- `toast_sound`
- `toast_sound_repeat`

Repeat mode behavior:

- Schedule one follow-up reminder after a configurable delay
- Cancel the follow-up reminder if the user interacts with the app before it fires
- Do not repeat indefinitely

This keeps the feature useful without becoming irritating.

### Settings

Add these settings to the existing settings model:

- `restore_window_on_complete` default `false`
- `notification_mode` default `toast`
- `repeat_after_minutes` default `2`
- `auto_start_next_phase` default `true`
- `minimize_to_tray_on_close` default `true`
- `show_countdown_in_tray` default `true`

These settings should be persisted with safe defaults and loaded defensively.

## Architecture

### Existing Constraints

The codebase is intentionally small and currently centers orchestration inside `ui.py`. That is workable now, but the requested behavior will keep adding branching logic to session completion and tray interactions. If the implementation stays fully inline in `ui.py`, the file will continue to grow as an unstructured coordination layer.

### Proposed Module Responsibilities

`timer.py`

- Keep countdown and phase transition logic
- Add support for `add_minutes()`
- Optionally support lightweight interaction tracking if needed for reminder cancellation

`storage.py`

- Extend settings persistence for the new fields
- Continue to clamp and default invalid values safely

`settings_dialog.py`

- Add controls for notification and background behavior
- Preserve current validation style

`tray.py`

- Expand menu actions
- Support dynamic tooltip/status text updates
- Expose the richer interaction surface needed for daily use

`ui.py`

- Remain the application composition root
- Delegate session completion decisions instead of hardcoding the full sequence inline
- Own cross-thread dispatch to Tk as it does today

New helper module, likely `completion_policy.py` or `alerts.py`

- Interpret alert settings
- Coordinate toast, sound, repeat reminder scheduling, and optional window restore
- Provide a single place to cancel pending reminder state on interaction

### Data Flow

Normal tick flow:

1. Timer updates remaining time
2. UI refreshes visible labels
3. Tray tooltip text updates if enabled

Completion flow:

1. Timer completion callback reaches UI on the Tk thread
2. UI determines whether the completed phase was work
3. Stats are recorded if appropriate
4. Completion-policy helper executes configured alert behavior
5. Timer advances to the next phase
6. Next phase starts or waits based on settings
7. UI and tray are refreshed

Interaction flow:

1. User interacts through tray or window
2. Action updates timer state
3. Any pending repeat reminder is canceled
4. UI and tray are refreshed

## Error Handling

- If tray support is unavailable, the main window workflow must still function.
- If toast notifications fail, the timer must still advance normally.
- If new settings are missing or malformed, loading should fall back to defaults.
- If the user interacts before a scheduled repeat reminder fires, that reminder must be canceled safely.
- If tooltip updates are unsupported by the tray backend, the rest of tray functionality should continue.

## Testing Strategy

Add tests for the behaviors introduced by this design:

- Settings round-trip for all new fields
- Safe fallback when persisted settings are missing or invalid
- `add_minutes()` behavior
- Completion behavior for each notification mode
- No forced window restore when disabled
- Repeat reminder cancellation on interaction
- Tray status text formatting

Testing should focus on behavior boundaries and state transitions, not GUI pixel details.

## Implementation Scope

Recommended first implementation batch:

1. Disable forced window restore by default through settings
2. Expand tray menu actions
3. Add tray tooltip countdown/status text
4. Add notification mode settings
5. Add one-shot repeat reminder support

This sequence produces the highest daily-use value early while keeping the changes incremental.

## Open Decisions Resolved

The following decisions are made explicitly to avoid ambiguity:

- The app remains tkinter-based.
- The tray is the primary day-to-day interaction surface.
- Window restore on completion is optional and defaults to off.
- Auto-start next phase remains supported and defaults to on.
- Repeat alerts happen once only, not indefinitely.
- The initial scope does not include full task tagging, detailed analytics, or compact mini mode.

## Success Criteria

This design succeeds if:

- The user can leave the app hidden for most of the day.
- Session changes are still noticeable without forced focus changes.
- The most common timer actions are available from the tray.
- The code remains modular enough that completion behavior is not trapped inside a growing `ui.py` conditional block.
