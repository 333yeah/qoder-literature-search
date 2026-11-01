"""删除并重建 lit_chunks 表"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import store


def main():
    print("正在删除 lit_chunks 表…")
    store.reset()
    print("重建完成。")


if __name__ == "__main__":
    main()
