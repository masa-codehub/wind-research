import sys
import os
import pytest
import importlib.util

# argument_parser.py の絶対パス
argument_parser_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "/app/src/adapters/cui/argument_parser.py"))
spec = importlib.util.spec_from_file_location(
    "argument_parser", argument_parser_path)
argument_parser = importlib.util.module_from_spec(spec)
sys.modules["argument_parser"] = argument_parser
spec.loader.exec_module(argument_parser)
parse_args = argument_parser.parse_args


def test_parse_args_with_no_arguments():
    """
    引数なしで呼び出された場合、SystemExit(2)となることを確認する。
    """
    with pytest.raises(SystemExit) as e:
        parse_args([])
    assert e.type == SystemExit
    assert e.value.code == 2


def test_parse_args_with_unknown_argument_raises_error():
    """
    不明な引数が指定された場合に、SystemExit例外が発生することを確認する。
    （受け入れ基準: 存在しないオプション指定時の標準エラー出力）
    """
    # Assert
    with pytest.raises(SystemExit) as e:
        # Act
        parse_args(['--unknown-argument'])
    # argparseはエラー時に終了コード2で終了する
    assert e.type == SystemExit
    assert e.value.code == 2


def test_parse_args_with_help_option_exits():
    """
    --help オプションが指定された場合に、正常終了することを確認する。
    （ヘルプ機能の基本動作確認）
    """
    # Assert
    with pytest.raises(SystemExit) as e:
        # Act
        parse_args(['--help'])
    # --help の場合は正常終了(コード0)
    assert e.type == SystemExit
    assert e.value.code == 0
