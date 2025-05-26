import pytest
import re
import subprocess
import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../')))

MAIN_PATH = os.path.join(os.path.dirname(__file__), "..", "main.py")


@pytest.mark.parametrize("args, expect_code, expect_out, expect_err", [
    (["--prefecture_no", "01", "--block_no", "001", "--start_date",
     "2025-05-26", "--days", "10"], 0, r"データ収集中...", None),
    (["--block_no", "001", "--start_date", "2025-05-26",
     "--days", "10"], 2, None, r"--prefecture_no"),
    (["--prefecture_no", "01", "--block_no", "001", "--start_date",
     "2025/05/26", "--days", "10"], 1, None, r"パラメータが不正"),
    (["--prefecture_no", "01", "--block_no", "001", "--start_date",
     "2025-05-26", "--days", "0"], 1, None, r"取得期間"),
])
def test_main_e2e(args, expect_code, expect_out, expect_err):
    proc = subprocess.run([sys.executable, MAIN_PATH] +
                          args, capture_output=True, text=True)
    assert proc.returncode == expect_code
    if expect_out:
        assert re.search(expect_out, proc.stdout)
    if expect_err:
        assert re.search(expect_err, proc.stderr)
