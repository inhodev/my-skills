---
name: reference-first-mobile-app
description: Use when building one real SwiftUI or Flutter app from an app description and a unified packet of ten reference-screen images, with Korean-first localization, working interactions, recapture, and visual QA.
---

# Reference-First Mobile App

## Outcome

Turn one app description plus ten coherent mockups into a working app. Treat the images as a visual contract, never as the UI implementation.

The stop condition is not “build passed.” It is:

- all ten mapped states exist in the real app tree;
- visible controls cause observable state or navigation changes;
- Korean is the default and English is complete unless the user explicitly changes localization scope;
- fresh Korean and English capture sets render the same real roots;
- direct visual comparison finds no blocking mismatch, clipping, fake UI, or debug surface;
- framework tests and the allowed QA surfaces pass.

## Required Inputs

Require one app, its product description, and ten reference images sharing one design concept. Also use any provided screen order, interaction notes, assets, framework choice, and project instructions.

If screen order is absent, infer it from filenames and product flow. Record the mapping before implementation. Ask only when two interpretations would materially change the product. Missing decorative assets are not a reason to stop: use a coherent bounded placeholder and record it. Never invent live-provider data, prices, permissions, or purchase success.

Run `scripts/inspect_reference_packet.py` before design work. It must report exactly ten readable, non-duplicate images.

## Execution Contract

### 1. Inspect, Do Not Guess

Open every reference at full detail. Read the existing project, project instructions, dirty-tree status, and current behavior. Check disk capacity before Flutter/iOS build or capture.

Create durable artifacts inside the app project:

- `reference-map.md`: reference file -> screen/state -> route -> locale -> capture filename;
- `interaction-contract.md`: every visible control -> expected effect -> verification surface;
- `design-system.md`: semantic color, typography, spacing, radius, elevation, icon, imagery, and motion decisions;
- `design-qa.md`: comparison rounds, defects, fixes, evidence, and remaining device-only boundaries.

Read [references/visual-contract.md](references/visual-contract.md) before implementation.

### 2. Extract One Design System

Use **REQUIRED SUB-SKILL:** `product-design:image-to-code` for reference analysis and implementation guidance.

Extract tokens and reusable primitives before composing screens. Preserve the reference's signature hierarchy, density, imagery, decorative layers, and state-specific composition. Do not reduce a rich mockup to generic cards and system defaults.

Reference pixels define the target viewport and proportions. Implement adaptive layout with semantic tokens; do not scatter one-off geometry values or force literal pixels that break localization and accessibility.

### 3. Build Real Product Behavior

Choose SwiftUI or Flutter from the request or existing project. Follow [references/frameworks.md](references/frameworks.md).

- Use real views/widgets, navigation, model state, persistence seams, loading, empty, error, populated, and edge states where relevant.
- Bind every visible primary and secondary action. No no-op buttons, invisible hotspots, screenshot backgrounds, capture-only mock trees, or product screenshots with QA selectors.
- Keep content photos and illustrations bounded to their intended asset slots. Never crop UI fragments from a reference and present them as controls, cards, maps, charts, or text.
- Implement the product rules, not only the pictured sample state. Derive displayed results from models and test the important rule boundaries.
- Use honest local fixtures when providers, permissions, billing, or secrets are unavailable. Label unavailable behavior and leave a production seam; do not claim live integration.

One session owns implementation for the whole app. A coordinator may use at most two active agents total, or a lower user limit. Additional agents should own bounded read-only reference analysis or independent QA; do not split overlapping screen files across writers.

### 4. Localize From the Start

Default locale is `ko-KR`; provide complete natural `en` localization unless the user explicitly says otherwise.

Localize visible copy, dynamic model content, errors, empty states, accessibility labels, dates, numbers, units, notifications, and permission rationale. Do not translate product names or proper nouns blindly. Test key parity and inspect both rendered languages for truncation and unnatural wrapping.

### 5. Verify Headlessly First

Run project-specific commands first. Otherwise run, sequentially:

1. static analysis or warnings-as-errors build;
2. unit and component/widget tests;
3. bounded headless smoke through the actual app root;
4. deterministic ten-screen capture in Korean and English;
5. capture-set validation and freshness checks.

Use `scripts/verify_capture_set.py` for each locale. A valid image file is not proof of a valid screen: directly open every capture.

Use **REQUIRED SUB-SKILL:** `app-qa-gate` for the non-disruptive QA decision. Do not boot a simulator unless the user explicitly requests it or project instructions require it. When iOS simulator QA is authorized, use `ios-simulator-skill` and only an existing, unoccupied iPhone 17 Pro.

### 6. Run the Three-Way Visual Loop

Use **REQUIRED SUB-SKILL:** `omo:visual-qa` after fresh captures exist.

For each mapped screen, compare:

| Surface | What to inspect |
|---|---|
| Reference | visual intent, hierarchy, signature layers, target density |
| Korean capture | fidelity, natural Korean, clipping, live state, selected navigation |
| English capture | parity, expansion, truncation, localized dynamic content |

Generate a review board with `scripts/make_comparison_board.py`, but still open all thirty images individually. Fix the highest-impact mismatch, recapture every affected state, and repeat until no blocking defect remains.

Blocking defects include screenshot substitution, missing screen hierarchy, wrong selected tab, absent or fake primary action, missing reference-specific layer, unexplained blank region, clipped content, untranslated copy, stale capture, or a capture tree different from the shipping root.

The gate improves the app; it must not silently abandon the job. When an issue cannot be fixed without unavailable authority or external state, preserve the working local path, mark only that boundary `USER QA REQUIRED` or `ATTENTION`, and finish all other in-scope work.

## Handoff

Deliver exact paths to:

- source and app entry point;
- reference map and design system;
- ten Korean and ten English captures;
- comparison board and `design-qa.md`;
- build, test, smoke, and capture logs.

Report separately: verified headless behavior, verified visual behavior, provider/permission/billing status, simulator/device status, and remaining user QA. Never inflate one surface into another.

## Red Flags

- “Close enough” after inspecting only one hero screen
- Full-screen reference image or UI fragment used as implementation
- Ten capture files rendered from a separate showcase tree
- English keys present but rendered English clipped
- Build success presented as interaction or visual proof
- Generic design tokens that omit screen-specific hierarchy
- Pausing overnight for a harmless asset or copy assumption
- Multiple writing agents editing the same app
