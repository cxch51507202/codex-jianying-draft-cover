# HTTP API Integration

## Endpoint

Expose 'POST /set_draft_cover' after importing 'set_draft_cover_impl' from the bundled script module.

Request body:

~~~json
{
  "draft_id": "saved-draft-directory-name",
  "draft_folder": "C:\\path\\to\\JianyingPro Drafts",
  "cover_image": "C:\\path\\to\\cover.png",
  "cover_width": 540,
  "cover_height": 720
}
~~~

'cover_path' may be accepted as a compatibility alias for 'cover_image'.

Flask route:

~~~python
@app.post("/set_draft_cover")
def set_draft_cover_service():
    data = request.get_json(silent=True) or {}
    try:
        output = set_draft_cover_impl(
            draft_id=data.get("draft_id"),
            draft_folder=data.get("draft_folder"),
            cover_image=data.get("cover_image") or data.get("cover_path"),
            cover_width=int(data.get("cover_width", 540)),
            cover_height=int(data.get("cover_height", 720)),
        )
        return jsonify({"success": True, "output": output, "error": ""})
    except Exception as error:
        return jsonify({"success": False, "output": "", "error": str(error)})
~~~

Call this endpoint only after the host service has saved the draft. A newly created but unsaved draft may not yet contain 'draft_content.json' or 'draft_info.json'.

## Success Output

The output reports the generated thumbnails, original source, dimensions, copied resource, JSON path, and new 'cover_draft_id'. Treat returned paths as local Windows paths.

## Failure Handling

- Fail if the image is missing or dimensions are non-positive.
- Fail if the draft ID contains unsupported characters or escapes the draft root.
- Fail if the saved draft JSON is absent.
- Do not silently fall back to adding the cover to the main timeline.
- Surface the failure to the caller so it can preserve a previously successful cover or ask the user to retry.
