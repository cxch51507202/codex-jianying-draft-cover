# Jianying Cover Format Notes

## Four Distinct Artifacts

1. 'draft_cover.jpg': 540 x 720 by default. Used for the draft-list thumbnail.
2. 'draft_local_cover.jpg': 180 x 240. Used as a local/export preview cache.
3. 'Resources/cover/<generated-name>': Original cover source copied into the draft.
4. Dedicated editable cover: 'draft_content.json.cover' points through 'cover_draft_id' to an independent composition in 'materials.drafts'.

Writing only 'draft_cover.jpg' is insufficient for Jianying's editor-side dedicated cover slot. Adding the image to a normal video track is a different operation and changes the exported timeline.

## Invariants

The dedicated cover operation must not change the main draft's:

- 'tracks'
- main 'materials.videos'
- 'duration'
- scene, audio, subtitle, or keyframe start times

The independent cover composition contains its own photo material and video track. That internal track belongs to the cover sub-draft, not the main program timeline.

## Replacement Behavior

When replacing an existing generated cover:

- Read the old 'cover.cover_draft_id'.
- Remove the matching old item from 'materials.drafts'.
- Add the new cover composition and update 'cover'.
- Remove the old generated resource after the JSON replacement succeeds.
- Keep unrelated 'materials.drafts' entries intact.

## Validation Checklist

- Open JSON as UTF-8 with optional BOM support.
- Confirm 'cover.cover_draft_id' matches exactly one 'materials.drafts[].id'.
- Confirm the referenced photo path ends in '/Resources/cover/<filename>'.
- Confirm the copied resource exists.
- Confirm both JPEG previews are non-empty and have the expected dimensions.
- Compare main 'tracks', main 'materials.videos', and 'duration' before and after.
- Open a disposable draft in Jianying and verify the cover appears in the separate cover entry.

## Compatibility

The bundled structure targets Jianying Pro 5.9 drafts observed on Windows. Jianying may revise private draft schemas in later releases. Preserve a backup and re-diff a manually created cover when supporting a new major format.
