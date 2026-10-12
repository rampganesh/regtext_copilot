# UI Design Specification — RegCopilot V1 Functional Prototype (Prompt)

## Brief

Design a clickable, desktop-web prototype for __RegCopilot__ — an internal AI research assistant for UK capital regulatory reporting analysts at a bank preparing for the Basel 3.1 transition (1 Jan 2027). The prototype has __no real backend__: all answers, sources and citations are mocked data, but must be *realistic* (use the real PRA Basel 3.1 publication timeline for mock sources: consultation CP16/22, near-final PS17/23 and PS9/24, final rules PS1/26, post-final consultation CP9/26).

__User__: an experienced regulatory reporting analyst. __Job__: answer regulatory questions with verifiable evidence in minutes instead of ~20. __Purpose of the prototype__: validate the complete V1 experience with two analysts before build.

## Core design principle

__Trust comes from evidence, never from confidence.__ No numeric confidence scores anywhere. Every screen state must let the analyst see *where the answer came from, how authoritative it is, and as of when*. The UI must never overstate authority, and the analyst is always responsible for the conclusion.

## Screens / states to design (the complete V1 experience)

__1. Title of the tool__ - __RegCopilot__

__2. Instructions for the search input__ - This will be a box of text below the title

__3. Ask a question__ — a single natural-language input box. No complex search syntax. Include an optional "as of [date]" control (default: today).

The results will have to redirect to another page with the results. The results page should have the title, question searched, and the below:

__4. Answer view__ — the heart of the product. This is a textbox section which will display the answer. 

- __Evidence-led phrasing__: "The relevant sources indicate…" — never "The applicable requirement is…" (that phrase is reserved for validated applicability, which this prototype never claims). This is the actual answer which will be synthesis of the search results. THis part will also call out the conflicts

__5. Citations__ - This is a scrollable section below the answer that will show the citations:

If there are multiple answers, each entry when clicked must expand to its contents. A citation must have the following parts:

- __Citations__ with the source, version/status, and precise location: section/paragraph for prose; for reporting questions, the specific __template / table / row/field / instruction reference__ with links to the definitions the field depends on
- Each citation expandable to a __context view__ — the surrounding passage, preserving qualifications/exceptions, so the analyst can verify without opening the source document
- __status badge__ (one of exactly five: `Final/Operative`, `Future-Effective`, `Superseded/Historical`, `Proposed/Consultation`, `Explanatory/Supporting`) plus effective date on every cited source (same five labels)
- __Conflict state__ — when mock sources appear to conflict: both sources shown __side-by-side__ with status/dates and an explicit warning. The UI never silently picks one. Offer a path to the escalation flow.


Clickable Figma-level prototype, desktop-web only (large monitor layout), single primary flow: __ask → review results → read answer with citations → verify via context view → (escalate if needed)__. Mock data sufficient to walk through all five difficult scenarios. Keep the design minimalistic. 
