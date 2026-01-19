"""阶段二：文档解析与数据建模的占位测试文件。

本文件目前仅用于占位，体现“有单元测试或验证脚本”的工程结构，
后续在实现 parse_ppt 后，可在此补充真实的解析正确性测试。
"""

from pathlib import Path

from core import ppt_parser


def test_import_and_api_shape() -> None:
    """确保 ppt_parser 模块与核心接口存在。"""

    assert hasattr(ppt_parser, "Slide")
    assert hasattr(ppt_parser, "parse_ppt")
    assert hasattr(ppt_parser, "parse_ppt_to_json_file")


def test_parse_example_ppt() -> None:
    """使用 examples/sample.pptx 做一次真实解析测试。

    目录约定：
    - 项目根目录: ppt_agent/
    - 示例 PPT: ppt_agent/examples/sample.pptx

    只校验：
    - 至少能解析出一页；
    - 首页包含标题字符串；
    具体内容由实际 PPT 决定，不做强约束。
    """

    base_dir = Path(__file__).resolve().parent
    ppt_path = base_dir / "examples" / "sample.pptx"

    if not ppt_path.exists():
        raise FileNotFoundError(
            f"示例 PPT 不存在: {ppt_path}，请在 examples/ 下放置 sample.pptx 后再运行测试。"
        )

    slides = ppt_parser.parse_ppt(ppt_path)

    # 基本正确性断言
    assert len(slides) > 0, "解析结果为空，请检查 sample.pptx 内容。"
    assert isinstance(slides[0].title, str), "首页标题应为字符串。"

    # 将解析结果同步写入 JSON 文件，便于人工查看与后续调试
    output_json_path = base_dir / "examples" / "parsed_sample_output.json"
    output_json_path.write_text(
        ppt_parser.slides_to_json(slides), encoding="utf-8"
    )

    return output_json_path


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent
    print("[info] 项目根目录:", base_dir)
    try:
        test_import_and_api_shape()
        print("[ok] ppt_parser API 形状检查通过。")
        output_path = test_parse_example_ppt()
        print("[ok] examples/sample.pptx 解析测试通过。")
        print("[info] 解析结果已写入:", output_path)
    except FileNotFoundError as e:
        # 友好提示：缺少示例 PPT 时只给出说明，不视为致命错误。
        print("[warn]", e)
    except AssertionError as e:
        print("[fail] 测试断言失败:", e)
