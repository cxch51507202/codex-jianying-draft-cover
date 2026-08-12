# Codex Jianying Draft Cover

[English](README.md) | [简体中文](README.zh-CN.md)

An open-source Codex Skill that fills a specific gap in AI-assisted video automation: writing a dedicated, editable cover directly into a Jianying Pro 5.9 draft without inserting that image into the main timeline or changing the video duration.

> Unofficial community project. Jianying and CapCut are trademarks of their respective owners.

## Why This Project Exists

Generating a Jianying draft is not the same as setting its dedicated cover. Writing only 'draft_cover.jpg' produces a list thumbnail, while sending the cover through a normal image-track API creates an unwanted opening clip and shifts the video timeline.

This Skill teaches Codex how to write all parts of Jianying's separate cover model:

- 'draft_cover.jpg' for the draft-list thumbnail
- 'draft_local_cover.jpg' for the local/export preview
- The original image under 'Resources/cover/'
- An independent editable cover composition referenced by 'cover.cover_draft_id'

The main tracks, scene timing, audio timing, keyframes, and total duration remain unchanged.

## What Is Included

- 'SKILL.md': Codex workflow, trigger description, and safety rules
- 'scripts/cover_impl.py': deterministic Jianying cover writer
- 'scripts/set_draft_cover.py': CLI with dry-run and backup support
- 'references/api.md': Flask and VectCutAPI-compatible endpoint guide
- 'references/format-notes.md': draft structure, invariants, and validation notes
- 'agents/openai.yaml': Codex-facing display metadata and default prompt

## Install As A Codex Skill

Clone the repository into your personal Codex skills directory:

~~~powershell
git clone https://github.com/cxch51507202/codex-jianying-draft-cover.git "$env:USERPROFILE\.codex\skills\codex-jianying-draft-cover"
~~~

Restart Codex if the Skill is not discovered immediately. You can then invoke it explicitly:

~~~text
Use $codex-jianying-draft-cover to set a dedicated cover for this Jianying draft without changing its main timeline.
~~~

## Use The CLI Directly

Requirements:

- Windows
- Python 3.9 or newer
- Pillow
- A saved Jianying Pro draft containing 'draft_content.json' or 'draft_info.json'

~~~powershell
python -m pip install Pillow

python scripts/set_draft_cover.py --draft-folder "C:\path\to\JianyingPro Drafts" --draft-id "YOUR_DRAFT_ID" --cover-image "C:\path\to\cover.png" --backup
~~~

Add '--dry-run' to validate the target and preview planned writes without modifying the draft.

## Safety Model

The implementation:

- Restricts draft IDs to letters, digits, '.', '_', and '-'
- Rejects draft paths that escape the selected draft root
- Uses atomic JSON replacement
- Removes a newly copied resource if the JSON update fails
- Replaces the previous generated cover instead of accumulating stale sub-drafts
- Performs no network request and requires no API key or user credential
- Does not execute shell commands from draft or image content

Close Jianying, or at least close the target draft, before modifying real project files. Use '--backup' and test new Jianying versions on a disposable draft first.

## Compatibility

The current implementation targets the Jianying Pro 5.9 draft structure observed on Windows. Jianying uses a private draft format and may change it in later versions. Compatibility reports, sanitized fixtures, tests, and carefully reviewed pull requests are welcome.

## License

[MIT](LICENSE)
