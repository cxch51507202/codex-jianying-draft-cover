---
name: codex-jianying-draft-cover
description: Extend Codex-generated Jianying Pro 5.9 drafts with a dedicated editable cover on Windows. Use when Codex is creating or modifying a 剪映草稿 and must directly write the separate cover slot, generate draft_cover.jpg or draft_local_cover.jpg, update draft_content.json/draft_info.json with a local cover composition, add a /set_draft_cover endpoint, or avoid incorrectly inserting the cover into the main timeline.
---

# Codex Jianying Draft Cover

Supplement Codex's Jianying draft generation workflow with direct support for the editor's dedicated cover slot. Set or replace that cover without adding the image to the main video timeline or changing the draft duration.

## Workflow

1. Confirm Jianying is closed or the target draft is not open for editing.
2. Locate the saved draft root and draft ID. The expected directory is '<draft_folder>/<draft_id>'.
3. Confirm the directory contains 'draft_content.json' or 'draft_info.json' and the source image exists.
4. Back up the target JSON before modifying a real user draft.
5. Run 'scripts/set_draft_cover.py' with the draft root, draft ID, and cover image.
6. Verify all four results:
   - 'draft_cover.jpg' is a 540 x 720 list thumbnail by default.
   - 'draft_local_cover.jpg' is a real 180 x 240 preview.
   - The original image is copied into 'Resources/cover/'.
   - The draft JSON has 'cover.cover_draft_id' pointing to one item in 'materials.drafts'.
7. Confirm the main draft's 'tracks', main 'materials.videos', and 'duration' were not changed by the cover operation.

## Run The Script

Install Pillow if it is unavailable:

~~~powershell
python -m pip install Pillow
~~~

Set a cover:

~~~powershell
python scripts/set_draft_cover.py --draft-folder "C:\path\to\JianyingPro Drafts" --draft-id "YOUR_DRAFT_ID" --cover-image "C:\path\to\cover.png"
~~~

Use '--dry-run' to validate paths and inspect the planned files without writing anything. Use '--backup' to create a timestamped JSON backup immediately before the write.

## Integration Rules

- Call the dedicated cover operation only after the draft has been saved and its JSON exists.
- Do not send the cover image through the normal '/add_image' flow unless the user explicitly wants a visible opening image in the exported video.
- Treat a dedicated cover and a timeline image as separate product features.
- Preserve the fixed Jianying draft-path placeholder used by the bundled implementation. Replacing it with the local draft path can make Jianying fail to resolve the cover resource.
- Use atomic JSON replacement. If JSON writing fails, remove the newly copied cover resource.
- Replace the previous generated cover material instead of accumulating stale cover sub-drafts.
- Restrict 'draft_id' to letters, digits, '.', '_', and '-'; reject paths that escape 'draft_folder'.

## HTTP Service

For a Flask service or VectCutAPI-compatible integration, read [references/api.md](references/api.md). Keep the response envelope compatible with the host service and pass all errors back as explicit failures.

## Verification And Troubleshooting

Read [references/format-notes.md](references/format-notes.md) before changing the generated JSON structure or debugging Jianying behavior. Pay special attention to the difference between the list thumbnail, export preview, dedicated editable cover, and main timeline.

The implementation targets the Jianying Pro 5.9 draft shape observed on Windows. It is an unofficial Codex capability supplement, not an official Jianying or CapCut integration. Always test changes against a disposable draft before applying them to important projects.
