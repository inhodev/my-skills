# Factory State Machine

## Phases

| Phase | Meaning | Maker slot |
|---|---|---|
| `QUEUED` | normalized idea, no worker progress | no |
| `DISCOVERY` | market enhancement and product research | no |
| `DESIGN` | product spec, interaction contract and ten-screen packet | no, unless generation pressure is equivalent |
| `BUILD_READY` | contracts exist and job is waiting FIFO | no |
| `BUILD` | real implementation and resource-heavy verification | yes |
| `HEADLESS_QA` | analysis, tests, smoke and deterministic capture | yes |
| `VISUAL_QA` | reference/KO/EN direct inspection and fixes | yes |
| `CORRECTION_READY` | failed active round released and fairly requeued | no |
| `CORRECTION` | bounded correction round | yes |
| `USER_QA` | permitted gates passed; explicit device/user checks remain | no |
| `COMPLETE` | every requested surface has verified evidence | no |
| `ATTENTION` | user authority or unavailable external state is required | no |

Only `BUILD`, `HEADLESS_QA`, `VISUAL_QA`, and `CORRECTION` may hold a reservation. A reservation belongs to one app and its recorded owning session.

## Valid Flow

`QUEUED -> DISCOVERY -> DESIGN -> BUILD_READY -> BUILD -> HEADLESS_QA -> VISUAL_QA`

An active round settles to:

- `USER_QA` when local/headless/visual work is done;
- `COMPLETE` only when no requested verification remains;
- `CORRECTION_READY` when another maker round is needed;
- `ATTENTION` when new authority is required.

`CORRECTION_READY -> CORRECTION -> HEADLESS_QA -> VISUAL_QA` rejoins the same path. A user correction from `USER_QA` may return to `CORRECTION_READY`.

## Fairness

Every transition into `BUILD_READY` or `CORRECTION_READY` receives a monotonically increasing ready sequence. Reservation is allowed only for the oldest eligible ready sequence. A repeatedly failing app therefore cannot permanently jump ahead of untouched ready apps.

## Restart Recovery

`factory-state.json` is authoritative for intent, not proof of runtime. After restart:

1. read active reservations and recorded session IDs;
2. inspect those sessions and their terminal/process state;
3. inspect expected artifacts and logs;
4. heartbeat genuinely active work;
5. advance or settle completed work;
6. move an abandoned job to correction or attention only with evidence.

Age alone cannot prove abandonment. User read state never participates.
