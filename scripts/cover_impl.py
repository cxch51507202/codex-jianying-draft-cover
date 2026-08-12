import json
import os
import re
import shutil
import uuid
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional

from PIL import Image, ImageDraw, ImageFont, ImageOps


_DRAFT_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")
_DRAFT_PATH_PLACEHOLDER = "0E685133-18CE-45ED-8CB8-2904A212EC80"
_CAPTION_PUNCTUATION = re.compile(
    r"""[\s，。！？；：、,.!?;:'"“”‘’（）()《》【】\[\]…—-]+"""
)


@lru_cache(maxsize=8)
def _resolve_font(font_path: Optional[str] = None) -> Path:
    candidates = []
    if font_path:
        candidates.append(Path(os.path.abspath(os.path.expanduser(font_path))))

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        font_cache = (
            Path(local_app_data)
            / "JianyingPro"
            / "User Data"
            / "Cache"
            / "effect"
        )
        if font_cache.is_dir():
            candidates.append(
                font_cache
                / "20373113"
                / "d3c284bf1c58e72c2ccd5c0c22bfa5e5"
                / "站酷快乐体2016修订版.ttf"
            )
            candidates.extend(font_cache.rglob("*快乐体*.ttf"))
            candidates.extend(font_cache.rglob("*快乐*.ttf"))

    candidates.extend(
        [
            Path(r"C:\Windows\Fonts\simkai.ttf"),
            Path(r"C:\Windows\Fonts\STKAITI.TTF"),
        ]
    )

    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()

    raise FileNotFoundError(
        "No usable Chinese font was found. Open Jianying and use 快乐体 once "
        "so its font resource is downloaded."
    )


def _clean_caption(text: str) -> str:
    raw = str(text or "").replace("\\r\\n", "\n").replace("\\n", "\n")
    lines = []
    for line in re.split(r"[\r\n]+", raw):
        cleaned = _CAPTION_PUNCTUATION.sub("", line).strip()
        if cleaned:
            lines.append(cleaned)

    if not 2 <= len(lines) <= 4:
        raise ValueError(
            f"cover caption must contain 2 to 4 non-empty lines, got {len(lines)}"
        )

    for index, line in enumerate(lines, start=1):
        if len(line) > 12:
            raise ValueError(
                f"cover caption line {index} exceeds 12 characters: {line}"
            )

    return "\n".join(lines)


def _safe_draft_directory(draft_folder: str, draft_id: str) -> Path:
    if not draft_folder:
        raise ValueError("draft_folder is required")
    if not draft_id or not _DRAFT_ID_PATTERN.fullmatch(str(draft_id)):
        raise ValueError("draft_id contains unsupported characters")

    draft_root = Path(
        os.path.abspath(os.path.normpath(os.path.expanduser(draft_folder)))
    ).resolve()
    draft_dir = (draft_root / str(draft_id)).resolve()

    try:
        draft_dir.relative_to(draft_root)
    except ValueError as exc:
        raise ValueError("draft_id resolves outside draft_folder") from exc

    if not draft_dir.is_dir():
        raise FileNotFoundError(f"saved draft directory does not exist: {draft_dir}")
    return draft_dir


def _jianying_id() -> str:
    return str(uuid.uuid4()).upper()


def _atomic_write_json(path: Path, payload: Dict[str, object]) -> None:
    temporary = path.with_name(f"{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _empty_cover_materials(
    *,
    canvas_id: str,
    speed_id: str,
    channel_id: str,
    separation_id: str,
    video: Dict[str, object],
) -> Dict[str, object]:
    names = (
        "ai_translates", "audio_balances", "audio_effects",
        "audio_fades", "audio_track_indexes", "audios", "beats",
        "chromas", "color_curves", "digital_humans", "drafts",
        "effects", "flowers", "green_screens", "handwrites", "hsl",
        "images", "log_color_wheels", "loudnesses",
        "manual_deformations", "masks", "material_animations",
        "material_colors", "multi_language_refs", "placeholders",
        "plugin_effects", "primary_color_wheels", "realtime_denoises",
        "shapes", "smart_crops", "smart_relights", "stickers",
        "tail_leaders", "text_templates", "texts", "time_marks",
        "transitions", "video_effects", "video_trackings",
        "vocal_beautifys",
    )
    materials: Dict[str, object] = {name: [] for name in names}
    materials.update(
        {
            "canvases": [
                {
                    "album_image": "", "blur": 0.0, "color": "",
                    "id": canvas_id, "image": "", "image_id": "",
                    "image_name": "", "source_platform": 0,
                    "team_id": "", "type": "canvas_color",
                }
            ],
            "sound_channel_mappings": [
                {
                    "audio_channel_mapping": 0, "id": channel_id,
                    "is_config_open": False, "type": "",
                }
            ],
            "speeds": [
                {
                    "curve_speed": None, "id": speed_id, "mode": 0,
                    "speed": 1.0, "type": "speed",
                }
            ],
            "videos": [video],
            "vocal_separations": [
                {
                    "choice": 0, "id": separation_id,
                    "production_path": "", "time_range": None,
                    "type": "vocal_separation",
                }
            ],
        }
    )
    return materials


def _build_cover_composition(
    *,
    resource_name: str,
    width: int,
    height: int,
    target_start: int,
) -> Dict[str, object]:
    draft_uuid = _jianying_id()
    material_id = f"{draft_uuid}_material"
    video_id = _jianying_id()
    canvas_id = _jianying_id()
    speed_id = _jianying_id()
    channel_id = _jianying_id()
    separation_id = _jianying_id()
    segment_id = _jianying_id()
    track_id = _jianying_id()
    resource_path = (
        f"##_draftpath_placeholder_{_DRAFT_PATH_PLACEHOLDER}_##"
        f"/Resources/cover/{resource_name}"
    )
    video = {
        "aigc_type": "none", "audio_fade": None, "cartoon_path": "",
        "category_id": "", "category_name": "", "check_flag": 63487,
        "crop": {
            "lower_left_x": 0.0, "lower_left_y": 1.0,
            "lower_right_x": 1.0, "lower_right_y": 1.0,
            "upper_left_x": 0.0, "upper_left_y": 0.0,
            "upper_right_x": 1.0, "upper_right_y": 0.0,
        },
        "crop_ratio": "free", "crop_scale": 1.0,
        "duration": 10800000000, "extra_type_option": 0, "formula_id": "",
        "freeze": None, "has_audio": False, "height": height, "id": video_id,
        "intensifies_audio_path": "", "intensifies_path": "",
        "is_ai_generate_content": False, "is_copyright": False,
        "is_text_edit_overdub": False, "is_unified_beauty_mode": False,
        "local_id": "", "local_material_id": "", "material_id": "",
        "material_name": "", "material_url": "",
        "matting": {
            "flag": 0, "has_use_quick_brush": False,
            "has_use_quick_eraser": False, "interactiveTime": [],
            "path": "", "strokes": [],
        },
        "media_path": "", "object_locked": None, "origin_material_id": "",
        "path": resource_path, "picture_from": "none",
        "picture_set_category_id": "", "picture_set_category_name": "",
        "request_id": "", "reverse_intensifies_path": "",
        "reverse_path": "", "smart_motion": None, "source": 0,
        "source_platform": 0,
        "stable": {
            "matrix_path": "", "stable_level": 0,
            "time_range": {"duration": 0, "start": 0},
        },
        "team_id": "", "type": "photo",
        "video_algorithm": {
            "algorithms": [], "complement_frame_config": None,
            "deflicker": None, "gameplay_configs": [],
            "motion_blur_config": None, "noise_reduction": None,
            "path": "", "quality_enhance": None, "time_range": None,
        },
        "width": width,
    }
    platform = {
        "app_id": 0, "app_source": "", "app_version": "",
        "device_id": "", "hard_disk_id": "", "mac_address": "",
        "os": "", "os_version": "",
    }
    config = {
        "adjust_max_index": 1, "attachment_info": [],
        "combination_max_index": 1, "export_range": None,
        "extract_audio_last_index": 1, "lyrics_recognition_id": "",
        "lyrics_sync": True, "lyrics_taskinfo": [], "maintrack_adsorb": True,
        "material_save_mode": 0, "multi_language_current": "none",
        "multi_language_list": [], "multi_language_main": "none",
        "multi_language_mode": "none", "original_sound_last_index": 1,
        "record_audio_last_index": 1, "sticker_max_index": 14000,
        "subtitle_keywords_config": None, "subtitle_recognition_id": "",
        "subtitle_sync": True, "subtitle_taskinfo": [],
        "system_font_list": [], "video_mute": False,
        "zoom_info_params": None,
    }
    keyframes = {
        "adjusts": [], "audios": [], "effects": [], "filters": [],
        "handwrites": [], "stickers": [], "texts": [], "videos": [],
    }
    segment = {
        "caption_info": None, "cartoon": False,
        "clip": {
            "alpha": 1.0, "flip": {"horizontal": False, "vertical": False},
            "rotation": 0.0, "scale": {"x": 1.0, "y": 1.0},
            "transform": {"x": 0.0, "y": 0.0},
        },
        "common_keyframes": [], "enable_adjust": True,
        "enable_color_correct_adjust": False, "enable_color_curves": True,
        "enable_color_match_adjust": False, "enable_color_wheels": True,
        "enable_lut": True, "enable_smart_color_adjust": False,
        "extra_material_refs": [speed_id, canvas_id, channel_id, separation_id],
        "group_id": "", "hdr_settings": None, "id": segment_id,
        "intensifies_audio": False, "is_placeholder": False,
        "is_tone_modify": False, "keyframe_refs": [],
        "last_nonzero_volume": 1.0, "material_id": video_id,
        "render_index": 101,
        "responsive_layout": {
            "enable": False, "horizontal_pos_layout": 0, "size_layout": 0,
            "target_follow": "", "vertical_pos_layout": 0,
        },
        "reverse": False, "source_timerange": {"duration": 3000000, "start": 0},
        "speed": 1.0,
        "target_timerange": {"duration": 3000000, "start": target_start},
        "template_id": "", "template_scene": "default",
        "track_attribute": 0, "track_render_index": 101,
        "uniform_scale": {"on": True, "value": 1.0},
        "visible": True, "volume": 1.0,
    }
    draft = {
        "canvas_config": {"height": 0, "ratio": "original", "width": 0},
        "color_space": -1, "config": config, "cover": None,
        "create_time": 0, "duration": 0, "extra_info": None, "fps": 30.0,
        "free_render_index_mode_on": False, "group_container": None,
        "id": draft_uuid, "keyframe_graph_list": [], "keyframes": keyframes,
        "last_modified_platform": platform,
        "materials": _empty_cover_materials(
            canvas_id=canvas_id, speed_id=speed_id, channel_id=channel_id,
            separation_id=separation_id, video=video,
        ),
        "mutable_config": None, "name": "", "new_version": "110.0.0",
        "platform": platform.copy(), "relationships": [],
        "render_index_track_mode_on": False, "retouch_cover": None,
        "source": "default", "static_cover_image_path": "",
        "time_marks": None,
        "tracks": [
            {
                "attribute": 0, "flag": 0, "id": track_id,
                "is_default_name": True, "name": "",
                "segments": [segment], "type": "video",
            }
        ],
        "update_time": 0, "version": 360000,
    }
    return {
        "cover": {
            "cover_draft_id": material_id, "cover_template": None,
            "sub_type": "local", "type": "image", "web_cover_info": None,
        },
        "material": {
            "category_id": "", "category_name": "", "combination_id": "",
            "draft": draft, "formula_id": "", "id": material_id,
            "name": "", "precompile_combination": False,
            "type": "composition",
        },
    }


def _cover_resource_names(payload: Dict[str, object], cover_id: str) -> set[str]:
    names: set[str] = set()
    drafts = payload.get("materials", {}).get("drafts", [])
    for item in drafts if isinstance(drafts, list) else []:
        if not isinstance(item, dict) or item.get("id") != cover_id:
            continue
        videos = item.get("draft", {}).get("materials", {}).get("videos", [])
        for video in videos if isinstance(videos, list) else []:
            path = str(video.get("path", "")).replace("\\", "/")
            marker = "/Resources/cover/"
            if marker in path:
                names.add(path.rsplit(marker, 1)[1])
    return names


def _install_editable_cover(
    *,
    draft_dir: Path,
    payload_path: Path,
    source: Path,
    width: int,
    height: int,
) -> Dict[str, object]:
    payload = json.loads(payload_path.read_text(encoding="utf-8-sig"))
    materials = payload.setdefault("materials", {})
    drafts = materials.setdefault("drafts", [])
    if not isinstance(drafts, list):
        raise ValueError(f"materials.drafts must be an array: {payload_path}")

    old_cover = payload.get("cover")
    old_cover_id = old_cover.get("cover_draft_id", "") if isinstance(old_cover, dict) else ""
    old_resources = _cover_resource_names(payload, str(old_cover_id))

    extension = source.suffix.lower() or ".png"
    resource_name = f"{_jianying_id()}{extension}"
    resource_dir = draft_dir / "Resources" / "cover"
    resource_dir.mkdir(parents=True, exist_ok=True)
    resource_path = resource_dir / resource_name
    shutil.copy2(source, resource_path)

    target_start = max(0, int(payload.get("duration") or 0)) + 1000000
    composition = _build_cover_composition(
        resource_name=resource_name, width=width, height=height,
        target_start=target_start,
    )
    materials["drafts"] = [
        item for item in drafts
        if not (isinstance(item, dict) and item.get("id") == old_cover_id)
    ] + [composition["material"]]
    payload["cover"] = composition["cover"]

    try:
        _atomic_write_json(payload_path, payload)
    except Exception:
        resource_path.unlink(missing_ok=True)
        raise

    for old_name in old_resources:
        if old_name != resource_name and Path(old_name).name == old_name:
            (resource_dir / old_name).unlink(missing_ok=True)

    return {
        "payload_path": str(payload_path.resolve()),
        "resource_path": str(resource_path.resolve()),
        "cover_draft_id": composition["cover"]["cover_draft_id"],
    }


def set_draft_cover_impl(
    *,
    draft_id: str,
    draft_folder: str,
    cover_image: str,
    cover_width: int = 540,
    cover_height: int = 720,
) -> Dict[str, object]:
    """Write both Jianying's list thumbnail and editable cover composition."""
    if not cover_image:
        raise ValueError("cover_image is required")
    if cover_width <= 0 or cover_height <= 0:
        raise ValueError("cover_width and cover_height must be positive")

    source = Path(os.path.abspath(os.path.expanduser(cover_image))).resolve()
    if not source.is_file():
        raise FileNotFoundError(f"cover_image does not exist: {source}")

    draft_dir = _safe_draft_directory(draft_folder, draft_id)
    with Image.open(source) as image:
        source_width, source_height = image.size
        cover = ImageOps.fit(
            image.convert("RGB"),
            (cover_width, cover_height),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )

    cover_path = draft_dir / "draft_cover.jpg"
    cover.save(
        cover_path,
        format="JPEG",
        quality=95,
        subsampling=0,
        optimize=True,
    )
    local_cover_path = draft_dir / "draft_local_cover.jpg"
    with Image.open(source) as image:
        local_cover = ImageOps.fit(
            image.convert("RGB"),
            (180, 240),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )
    local_cover.save(
        local_cover_path,
        format="JPEG",
        quality=95,
        subsampling=0,
        optimize=True,
    )

    payload_path = draft_dir / "draft_content.json"
    if not payload_path.is_file():
        payload_path = draft_dir / "draft_info.json"
    if not payload_path.is_file():
        raise FileNotFoundError(
            f"draft_content.json or draft_info.json does not exist: {draft_dir}"
        )
    editable_cover = _install_editable_cover(
        draft_dir=draft_dir, payload_path=payload_path, source=source,
        width=source_width, height=source_height,
    )

    return {
        "draft_id": str(draft_id),
        "cover_image": str(cover_path.resolve()),
        "local_cover_image": str(local_cover_path.resolve()),
        "source_image": str(source),
        "width": cover_width,
        "height": cover_height,
        "editable_cover": editable_cover,
    }


def set_handdraw_cover_impl(
    *,
    draft_id: str,
    draft_folder: str,
    line_image: str,
    text: str,
    cover_width: int = 540,
    cover_height: int = 720,
    font_size: int = 20,
    text_x_ratio: float = 0.05,
    text_y_ratio: float = 0.055,
    line_spacing: int = 5,
    font_path: Optional[str] = None,
    font_color: str = "#333333",
) -> Dict[str, object]:
    if not line_image:
        raise ValueError("line_image is required")
    if not text:
        raise ValueError("text or caption_text is required")
    if cover_width <= 0 or cover_height <= 0:
        raise ValueError("cover_width and cover_height must be positive")
    if font_size <= 0:
        raise ValueError("font_size must be positive")
    if not 0 <= text_x_ratio <= 1 or not 0 <= text_y_ratio <= 1:
        raise ValueError("text ratios must be between 0 and 1")

    source = Path(os.path.abspath(os.path.expanduser(line_image))).resolve()
    if not source.is_file():
        raise FileNotFoundError(f"line_image does not exist: {source}")

    caption = _clean_caption(text)
    draft_dir = _safe_draft_directory(draft_folder, draft_id)
    resolved_font = _resolve_font(font_path)

    with Image.open(source) as image:
        cover = ImageOps.fit(
            image.convert("RGB"),
            (cover_width, cover_height),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )

    draw = ImageDraw.Draw(cover)
    font = ImageFont.truetype(str(resolved_font), font_size)
    text_x = round(cover_width * text_x_ratio)
    text_y = round(cover_height * text_y_ratio)
    draw.multiline_text(
        (text_x, text_y),
        caption,
        font=font,
        fill=font_color,
        spacing=line_spacing,
        align="left",
    )

    cover_path = draft_dir / "draft_cover.jpg"
    cover.save(
        cover_path,
        format="JPEG",
        quality=95,
        subsampling=0,
        optimize=True,
    )

    grayscale = cover.convert("L")
    dark_pixels = sum(1 for value in grayscale.getdata() if value < 235)
    dark_pixel_ratio = dark_pixels / float(cover_width * cover_height)
    if dark_pixel_ratio < 0.002:
        raise ValueError("generated cover is unexpectedly blank")

    return {
        "draft_id": str(draft_id),
        "cover_image": str(cover_path.resolve()),
        "line_image": str(source),
        "font_path": str(resolved_font),
        "caption_text": caption,
        "width": cover_width,
        "height": cover_height,
        "dark_pixel_ratio": round(dark_pixel_ratio, 6),
    }
