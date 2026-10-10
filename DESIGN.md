---
name: SmartDrive
description: A familiar cloud drive whose files tag themselves.
colors:
  accent-blue: "#1b5fd1"
  accent-blue-deep: "#164fb1"
  accent-blue-soft: "#d8e5fb"
  accent-blue-wash: "#eef4fe"
  accent-blue-ink: "#0d3a85"
  shell: "#f3f6fb"
  surface: "#ffffff"
  hover: "#edf1f7"
  pressed: "#e1e8f2"
  line: "#e1e6ed"
  field-stroke: "#8c95a1"
  ink: "#1d232b"
  ink-secondary: "#4f5965"
  ink-tertiary: "#6b7480"
  tag: "#e9eef6"
  tag-ink: "#344256"
  danger: "#b42318"
  danger-soft: "#fdecea"
  public-green: "#146c34"
  public-green-soft: "#dcf3e3"
  snackbar: "#2b3036"
  type-image: "#d6452c"
  type-pdf: "#c62828"
typography:
  headline:
    fontFamily: "Inter, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "26px"
    fontWeight: 500
    lineHeight: 1.2
    letterSpacing: "-0.015em"
  title:
    fontFamily: "Inter, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "22px"
    fontWeight: 500
    lineHeight: 1.25
    letterSpacing: "-0.015em"
  subtitle:
    fontFamily: "Inter, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "20px"
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: "-0.01em"
  body:
    fontFamily: "Inter, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.45
  label:
    fontFamily: "Inter, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "13px"
    fontWeight: 500
    lineHeight: 1.45
  caption:
    fontFamily: "Inter, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "12px"
    fontWeight: 500
    lineHeight: 1.45
rounded:
  sm: "8px"
  lg: "16px"
  xl: "20px"
  card: "24px"
  pill: "999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
  2xl: "40px"
components:
  button-primary:
    backgroundColor: "{colors.accent-blue}"
    textColor: "{colors.surface}"
    rounded: "{rounded.pill}"
    padding: "0 20px"
    height: "40px"
  button-primary-hover:
    backgroundColor: "{colors.accent-blue-deep}"
  button-outline:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.accent-blue}"
    rounded: "{rounded.pill}"
    padding: "0 20px"
    height: "40px"
  button-outline-hover:
    backgroundColor: "{colors.accent-blue-wash}"
  button-new:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: "0 24px 0 16px"
    height: "56px"
  search-field:
    backgroundColor: "{colors.tag}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    height: "48px"
  text-field:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "0 14px"
    height: "48px"
  nav-item-active:
    backgroundColor: "{colors.accent-blue-soft}"
    textColor: "{colors.accent-blue-ink}"
    rounded: "{rounded.pill}"
    height: "36px"
  tag-chip:
    backgroundColor: "{colors.tag}"
    textColor: "{colors.tag-ink}"
    typography: "{typography.caption}"
    rounded: "{rounded.pill}"
    padding: "0 10px"
    height: "24px"
  content-sheet:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.lg}"
    padding: "4px 24px 32px"
  share-sheet:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.xl}"
    padding: "24px"
  snackbar:
    backgroundColor: "{colors.snackbar}"
    textColor: "{colors.surface}"
    rounded: "{rounded.sm}"
---

# Design System: SmartDrive

## Overview

**Creative North Star: "The Familiar Drive"**

SmartDrive looks and behaves like the cloud drives people already use every day, so nobody needs a tour. That familiarity is the point: an examiner should take it for a real product within seconds, and a classmate should be able to upload, find and share a file without asking how. The craft bar is Google Drive and Dropbox. Every control is standard, and the polish is in spacing, contrast and states.

The page is a cool blue-grey shell holding one white content sheet. A single blue accent marks what you can act on, the view you are in, and where keyboard focus is. The product's one differentiator, AI tagging, shows up as an ordinary column of quiet chips in the file list rather than as a spectacle. The interface is light because it is used on laptops in lit rooms.

**Key Characteristics:**
- Blue-grey shell, white sheet with 16px corners, one blue accent.
- Inter at a 14px base with tabular numerals for sizes and dates.
- Material Symbols Rounded icons; file-type icons are filled and coloured by kind.
- Pill shapes for search, navigation, buttons and tags.
- Shadows only on things that float.

## Colors

A restrained palette: tinted neutrals do the structure, and one blue does the pointing.

### Primary
- **Drive Blue** (accent-blue): primary buttons, the New button's plus sign, links, focus rings, the selected view's icon and the AI-tags column marker.
- **Pressed Drive Blue** (accent-blue-deep): hover state of primary buttons.
- **Selected Pill Blue** (accent-blue-soft), with **Deep Navy Ink** (accent-blue-ink) on top: the current navigation item, the indeterminate upload bar's track, and the mobile New button.
- **Blue Wash** (accent-blue-wash): hover on outline and text buttons, and the empty-state icon disc.

### Neutral
- **Cool Shell** (shell): page background behind the sidebar, top bar and content sheet.
- **Sheet White** (surface): the content sheet, auth card, share sheet and upload panel.
- **Row Hover** (hover) and **Pressed Grey** (pressed): hovered table rows, navigation and icon buttons; tag chips deepen to Pressed Grey on a hovered row.
- **Hairline** (line): table row dividers and the "+N" chip outline.
- **Field Stroke** (field-stroke): text-field and outline-button borders (3:1 against white).
- **Ink** (ink), **Secondary Ink** (ink-secondary) and **Tertiary Ink** (ink-tertiary): primary text, then metadata and placeholders on fills, then hints and placeholders on white only.
- **Tag Grey** (tag) with **Tag Ink** (tag-ink): AI tag chips and the resting search field.

### Semantic
- **Error Red** (danger) on **Error Blush** (danger-soft): form errors and the delete button's hover.
- **Public Green** (public-green) on **Public Mint** (public-green-soft): the "Anyone with the link" access icon.
- **Snackbar Charcoal** (snackbar): toasts and the upload panel header.
- **Photo Orange-Red** (type-image), **PDF Red** (type-pdf); text files use Drive Blue and anything else uses Tertiary Ink.

### Named Rules
**The One Blue Rule.** Blue only marks what is actionable, selected or focused. It is never used as decoration, never as a large field, and never in gradients.

**The Quiet Tags Rule.** AI tags are grey-blue chips. At most three show in a row, followed by a "+N" chip. Tags never take the accent colour or carry per-chip sparkles; the single sparkle lives in the column header.

## Typography

**Body Font:** Inter (falling back to system-ui, -apple-system, Segoe UI, sans-serif)

**Character:** one workhorse sans carries everything: titles, buttons, labels and data. The hierarchy comes from size and weight steps, not from a second face.

### Hierarchy
- **Headline** (500, 26px, 1.2, −0.015em): the auth card heading ("Sign in").
- **Title** (500, 22px, 1.25, −0.015em): the view title in the content sheet ("My files", "Results for …").
- **Subtitle** (500, 20px, 1.3, −0.01em): share-sheet and empty-state headings.
- **Body** (400, 14px, 1.45): everything by default; file names use weight 500.
- **Label** (500, 13px): table headers, field labels, the summary line and metadata.
- **Caption** (500, 12px): tag chips and hints.

### Named Rules
**The Tabular Numbers Rule.** Sizes, dates and counts always use `font-variant-numeric: tabular-nums`, so the columns line up.

## Layout

Desktop is a two-column grid: a 256px sidebar (logo, New, navigation, storage used) and a main column with a 64px top bar (search field up to 720px wide, plus the user area) above the content sheet. The sheet has 16px margins on the right and bottom. The file list is a fixed-layout table: Name (flexible), AI tags (34%), Uploaded or Shared by (150px, or 240px when it holds an email), Size (96px) and actions (124px).

Responsive steps:
- **≤1180px:** the date column is dropped.
- **≤1000px:** the sidebar narrows to 220px and tags take 30%.
- **≤860px:** the layout collapses to a single column. The sidebar and top bar dissolve into rows: logo plus avatar, then search, then navigation tabs. Each file row becomes a two-line grid (name with a size·date line, then tags), and New becomes a floating button at the bottom right.

Spacing works in 4px steps (4, 8, 12, 16, 24, 40), with tight groups inside components and larger gaps between them.

## Elevation & Depth

Depth is mostly tonal: a white sheet on a tinted shell. Shadows appear only on elements that float above the page, and every shadow has a vertical offset and a soft blur.

### Shadow Vocabulary
- **Resting lift** (`0 1px 2px rgb(24 39 75 / .12), 0 1px 3px 1px rgb(24 39 75 / .07)`): the New button, the auth card, the focused search field and hovered primary buttons.
- **Raised lift** (`0 2px 6px 2px rgb(24 39 75 / .1), 0 1px 2px rgb(24 39 75 / .14)`): the hovered New button, the mobile New button and snackbars.
- **Floating** (`0 12px 32px rgb(24 39 75 / .18), 0 2px 6px rgb(24 39 75 / .1)`): the share sheet, upload panel and drop message.

### Named Rules
**The Shadows-Mean-Lift Rule.** A shadow means "this floats". Rows, chips and the sheet itself stay flat.

## Shapes

Corners are soft and consistent:
- **Pills** (999px): buttons, search, navigation items, tags, avatars and the drop message.
- **16px:** the content sheet, the New button and the upload panel.
- **20px:** the share sheet.
- **24px:** the auth card.
- **8px:** text fields and snackbars.

Borders are reserved for text fields, outline buttons and table hairlines.

## Components

### Buttons
- **Shape:** pill (999px), 40px tall.
- **Primary:** Drive Blue fill with white text, 20px side padding; it deepens and lifts slightly on hover.
- **Outline:** white fill with a Field Stroke border and blue text; Blue Wash on hover.
- **Text:** no border, with Blue Wash on hover. Used for secondary actions such as "Create account" and "Turn off link".
- **New:** a white 56px button with 16px corners, the resting lift and a blue plus sign. On mobile it floats at the bottom right on Selected Pill Blue.
- **Icon buttons:** 36px circles in Secondary Ink, Pressed Grey on hover. Delete turns red on hover.
- **Busy:** submit buttons disable and change their label ("Signing in…") while the request is in flight.

### Chips
- **AI tag:** Tag Grey with Tag Ink, 24px tall and 12px/500 text. The overflow "+N" chip has a hairline outline and lists the hidden tags in its tooltip.

### Inputs / Fields
- **Text field:** 48px tall, white, 1px Field Stroke border, 8px corners. On focus it gets a blue border plus a 1px inset blue ring, with no layout shift.
- **Search:** a 48px pill in Tag Grey that turns white with the resting lift when focused. A clear button appears while a query is active.
- **Errors:** an Error Blush strip with an error icon above the form, named problem and how to recover.

### Navigation
- **Sidebar items:** 36px pills with icons. Hover is Row Hover. The current view is Selected Pill Blue with Deep Navy Ink, a filled icon and weight 600. On mobile the items become outlined tabs.

### File list
- **Rows:** 56px tall with hairline dividers; Row Hover on hover and on focus-within. Row actions (Share, Download, Delete) fade in on hover or focus, and are always visible on touch screens.
- **Type icons:** filled glyphs coloured by kind.
- **Sharing indicators:** a globe for a public link, people for a direct share, both in Tertiary Ink.

### Share sheet
A centred popover (native `popover`, closes on click outside or Esc) with a 32% dimmed backdrop. From top to bottom:
1. Title.
2. "Add people by email" field with a Share button.
3. "People with access" list with avatars and roles.
4. "General access" row (Restricted or Anyone with the link) with a text-button toggle.
5. Read-only link field with "Copy link".
6. Done.

### Upload feedback
- **Drop target:** dragging a file anywhere shows a full-window blue outline with a "Drop to upload to My files" pill.
- **Upload panel:** a bottom-right panel with a charcoal header, the file name, "Uploading and tagging with AI…" and an indeterminate blue bar.
- **Results:** shown as charcoal snackbars at the bottom left. Errors add a soft red icon.

## Do's and Don'ts

### Do:
- **Do** keep every control standard: buttons, fields, tabs and popovers that people already know how to use.
- **Do** use Drive Blue only for actions, the current selection, links and focus (The One Blue Rule).
- **Do** show AI tags as quiet chips, at most three plus "+N" (The Quiet Tags Rule).
- **Do** give every interactive element hover, focus-visible, busy and error states, and every list an empty state that explains what to do next.
- **Do** keep text at 4.5:1 or better: use Secondary Ink for any text that can sit on a fill or a hovered row.

### Don't:
- **Don't** add the "AI product" look: dark glowing themes, gradients, gradient text or neon accents. The user chose the familiar drive over novelty.
- **Don't** show numbers the system doesn't have, such as a storage quota ("of 15 GB"), usage charts or fake activity.
- **Don't** nest cards inside the content sheet or wrap files in same-size cards. Files are rows.
- **Don't** use emoji or Unicode glyphs as icons; use Material Symbols Rounded or authored SVG.
- **Don't** add shadows to flat things such as rows, chips or the sheet.
