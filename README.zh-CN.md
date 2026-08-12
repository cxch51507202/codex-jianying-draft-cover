# Codex 剪映草稿封面 Skill

[English](README.md) | [简体中文](README.zh-CN.md)

这是一个开源 Codex Skill，专门补充 AI 视频自动化中的一项关键能力：让 Codex 能够把图片直接写入剪映专业版 5.9 草稿的独立可编辑封面位置，同时不把封面插入主时间线，也不改变视频时长。

> 本项目为非官方社区项目。剪映和 CapCut 商标归各自权利人所有。

## 为什么需要这个项目

生成剪映草稿并不等于正确设置剪映的专用封面。只写入 'draft_cover.jpg'，通常只能得到草稿列表缩略图；如果把封面当作普通图片素材添加到轨道，又会产生多余的片头片段，并导致全部画面、配音和关键帧时间发生偏移。

这个 Skill 告诉 Codex 如何完整写入剪映独立封面所需的四部分数据：

- 'draft_cover.jpg'：草稿列表缩略图
- 'draft_local_cover.jpg'：本地及导出预览
- 'Resources/cover/'：封面原始图片资源
- 由 'cover.cover_draft_id' 引用的独立可编辑封面 composition

写入完成后，主草稿轨道、分镜时间、配音时间、关键帧和总时长都保持不变。

## 仓库内容

- 'SKILL.md'：Codex 触发说明、执行流程和安全规则
- 'scripts/cover_impl.py'：确定性的剪映封面写入实现
- 'scripts/set_draft_cover.py'：支持预检查和备份的命令行工具
- 'references/api.md'：Flask 与 VectCutAPI 兼容接口说明
- 'references/format-notes.md'：草稿结构、不可破坏的约束和验证方法
- 'agents/openai.yaml'：Codex 中的显示信息和默认提示词

## 作为 Codex Skill 安装

将仓库克隆到个人 Codex Skills 目录：

~~~powershell
git clone https://github.com/cxch51507202/codex-jianying-draft-cover.git "$env:USERPROFILE\.codex\skills\codex-jianying-draft-cover"
~~~

如果 Codex 没有立即发现该 Skill，请重启 Codex。之后可以显式调用：

~~~text
使用 $codex-jianying-draft-cover 为这个剪映草稿设置独立封面，并保持主时间线不变。
~~~

## 直接使用命令行工具

运行条件：

- Windows
- Python 3.9 或更高版本
- Pillow
- 已保存并包含 'draft_content.json' 或 'draft_info.json' 的剪映专业版草稿

~~~powershell
python -m pip install Pillow

python scripts/set_draft_cover.py --draft-folder "C:\剪映草稿根目录" --draft-id "草稿目录名称" --cover-image "C:\封面图片\cover.png" --backup
~~~

加入 '--dry-run' 可以只验证目标路径并查看计划写入的文件，不修改实际草稿。

## 安全设计

当前实现具备以下保护：

- 草稿 ID 只允许字母、数字、'.'、'_' 和 '-'
- 拒绝任何逃逸出指定草稿根目录的路径
- 使用原子方式替换 JSON
- JSON 更新失败时删除刚复制的封面资源
- 替换旧封面子草稿，避免不断积累失效数据
- 不发起网络请求，不需要 API Key 或用户凭证
- 不从草稿内容或图片内容执行 Shell 命令

修改真实项目之前，建议关闭剪映，或者至少关闭目标草稿。请使用 '--backup'，并在适配新版剪映时先使用一次性测试草稿验证。

## 兼容性

当前版本面向 Windows 上观察和验证过的剪映专业版 5.9 草稿结构。剪映使用私有草稿格式，后续版本可能发生变化。欢迎提交兼容性报告、脱敏草稿样本、测试以及经过谨慎安全审查的 Pull Request。

## 开源许可证

[MIT](LICENSE)
