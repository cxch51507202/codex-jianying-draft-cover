#!/usr/bin/env python3
import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

from cover_impl import _safe_draft_directory, set_draft_cover_impl


def parse_args():
    parser = argparse.ArgumentParser(
        description="Set the dedicated editable cover of a Jianying Pro 5.9 draft."
    )
    parser.add_argument("--draft-folder", required=True, help="Root folder containing draft directories")
    parser.add_argument("--draft-id", required=True, help="Saved Jianying draft directory name")
    parser.add_argument("--cover-image", required=True, help="Local PNG/JPEG/WebP cover image")
    parser.add_argument("--cover-width", type=int, default=540)
    parser.add_argument("--cover-height", type=int, default=720)
    parser.add_argument("--backup", action="store_true", help="Back up the target draft JSON before writing")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs and print the planned operation")
    return parser.parse_args()


def main():
    args = parse_args()
    draft_dir = _safe_draft_directory(args.draft_folder, args.draft_id)
    source = Path(args.cover_image).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"cover image does not exist: {source}")

    payload_path = draft_dir / "draft_content.json"
    if not payload_path.is_file():
        payload_path = draft_dir / "draft_info.json"
    if not payload_path.is_file():
        raise FileNotFoundError(f"draft_content.json or draft_info.json does not exist: {draft_dir}")

    plan = {
        "draft_directory": str(draft_dir),
        "draft_json": str(payload_path),
        "cover_image": str(source),
        "thumbnail_size": [args.cover_width, args.cover_height],
        "writes": [
            "draft_cover.jpg",
            "draft_local_cover.jpg",
            "Resources/cover/<generated-name>",
            payload_path.name,
        ],
    }
    if args.dry_run:
        print(json.dumps({"success": True, "dry_run": True, "plan": plan}, ensure_ascii=False, indent=2))
        return 0

    backup_path = None
    if args.backup:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = payload_path.with_name(f"{payload_path.name}.{stamp}.bak")
        shutil.copy2(payload_path, backup_path)

    result = set_draft_cover_impl(
        draft_id=args.draft_id,
        draft_folder=args.draft_folder,
        cover_image=str(source),
        cover_width=args.cover_width,
        cover_height=args.cover_height,
    )
    output = {"success": True, "output": result}
    if backup_path:
        output["backup"] = str(backup_path.resolve())
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(json.dumps({"success": False, "error": str(error)}, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)
