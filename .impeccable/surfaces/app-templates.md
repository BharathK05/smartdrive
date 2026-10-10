# Surface: SmartDrive app (app/templates/*)

**Scope:** sign-in, create account, My files, Shared with me. **Mode:** Operate.

**Audience and job:** a user on a laptop uploads, finds and shares files. Examiners must read the app as a real product within seconds.

**Constraints:**
- Plain Jinja + static CSS/JS with no build step.
- Keep every route and behaviour.
- No invented quota or claims.

**Unresolved:** none.

## Direction contract

**THESIS:** A cloud drive that everyone already knows how to use, with AI tags as an ordinary column in the file list rather than a spectacle. It rejects two category defaults: the "AI product" look (dark, glow, gradients) and the bare-template look (stock framework components).

**OWN-WORLD:** The category standard at Drive/Dropbox craft.
- Colour: a cool blue-grey shell (#f3f6fb) holding a white content sheet with 16px corners. One blue accent (#1b5fd1) for primary actions, the selected navigation pill and focus rings.
- Type: Inter, 14px base, tabular numerals.
- Icons: Material Symbols Rounded. File-type icons are filled and coloured by kind.
- Controls: pill-shaped search field, an elevated white "New" button, quiet grey-blue tag chips, and dark snackbars at the bottom left.

**STORY:**
1. Sign in.
2. The visitor lands on My files.
3. They upload with New or by dropping a file anywhere.
4. An upload panel says the file is being read with AI.
5. The file appears with its tags.
6. Searching a tag finds it.
7. A Drive-style share panel adds people or turns on a public link with copy.

**FIRST VIEWPORT:**
- **Left sidebar (256px):** logo mark and wordmark, the New button (the primary action, top left), navigation with My files selected and Shared with me, and storage used at the bottom.
- **Top bar:** pill search field on the left of centre; avatar initial, email and Log out on the right.
- **Content sheet:** the title "My files" with "N files · X MB", then a list with columns Name (type icon), AI tags, Modified and Size, plus hover actions: Share, Download, Delete.
- **Signature interaction:** dropping a file anywhere shows a full-window drop target, followed by an upload panel at the bottom right reading "Reading with AI". Motion is 150–200ms ease-out and conveys state only.

**FORM:** The category standard (canon), chosen by the user over three directions: Card catalog (1), Colour-coded filing (2) and Munich '72 (3). No seed key, because the concept-seed roll was not run (the launcher was not executed this session).

**FINISH:** unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
