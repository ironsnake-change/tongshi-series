#!/usr/bin/env python3
"""Create a new article directory and queue metadata record."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
import sys
from pathlib import Path

def _configure_stdout():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

_configure_stdout()




def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold one Tongshi Series article.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--id", required=True, help="Short ASCII topic id")
    parser.add_argument("--domain", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--date", default=datetime.now().date().isoformat())
    args = parser.parse_args()

    if not args.id.replace("-", "").isalnum() or args.id != args.id.lower():
        raise SystemExit("--id must be lowercase letters, digits, or hyphens")

    root = Path(args.root).resolve()
    directory = root / f"{args.date}-{args.id}"
    if directory.exists():
        raise SystemExit(f"directory already exists: {directory}")
    directory.mkdir(parents=True)

    now = datetime.now(timezone.utc).isoformat()
    meta = {
        "id": args.id,
        "domain": args.domain,
        "title": args.title,
        "created_at": now,
        "queued_at": now,
    }
    (directory / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    skeleton = f"""# {args.title}

## 一、一个具体的切口

先写一个能在 120 字内建立画面或疑问的开头。第二段结束前说明这篇为什么值得读。

## 二、材料现场

把一手材料、后世转述和现代推断分开，写明来源。

## 三、机制

解释事情怎样发生，避免只罗列结论。

## 四、转折

写读者原以为 A、材料却指向 B 的那一步。

## 五、一个具体场景

写一个有地点、有时间、有动作的现场；不要用概述代替场景。

## 六、代价

回到具体人物、制度或器物。

## 七、一条反证

加入一个会削弱直觉解释的材料、实验或例外。

## 八、争议

写清目前更站得住的说法，以及缺哪一环证据。

## 九、本篇的确定性说明

可以确认：写有一手证据、争议较小的条目。

有共识但细节存疑：写方向明确但数值、范围或地点仍有争议的条目。

属于推测仍有争论：写清推测内容和争议焦点。

## 十、尾声

用一个具体问题或对照收束，不喊口号。

## 术语表

- 术语一：不超过四十字的解释。
- 术语二：不超过四十字的解释。
- 术语三：不超过四十字的解释。

## 延伸阅读

- 作者，《篇名》，出版信息或年份。
- 作者，《篇名》，出版信息或年份。
- 作者，《篇名》，出版信息或年份。
"""
    (directory / "article.md").write_text(skeleton, encoding="utf-8")
    print(directory)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
