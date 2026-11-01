"""读取 data/sample_docs.jsonl 入库（幂等：先清表再导入）"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import store


def main():
    reset = "--reset" in sys.argv

    if reset:
        print("正在重置数据库（DROP + CREATE）…")
        store.reset()
    else:
        print("正在确保表结构存在…")
        store.ensure_schema()

    jsonl_path = Path(__file__).parent.parent / "data" / "sample_docs.jsonl"
    if not jsonl_path.exists():
        print(f"错误：找不到 {jsonl_path}")
        sys.exit(1)

    documents = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                documents.append(json.loads(line))

    print(f"读取到 {len(documents)} 条文档，正在生成向量并入库…")
    total_chunks = store.bulk_add(documents)
    print(f"入库完成：{len(documents)} 条文档 → {total_chunks} 个片段")

    s = store.stats()
    print(f"数据库统计：总量 {s['total']}，by_source={s['by_source']}，by_topic={s['by_topic']}")


if __name__ == "__main__":
    main()
