from unittest.mock import patch, MagicMock
import pytest
import time
from src.app.adapters.web.throttler import RequestThrottler

# テスト用のポリシー
test_policies = {"test.domain.com": 5.0}

def make_url(domain):
    return f"https://{domain}/path"

@patch('time.sleep', MagicMock())
@patch('time.monotonic')
def test_wait_if_needed_enforces_system_policy(mock_monotonic):
    """
    ユーザー指定値よりシステムポリシーが厳しい場合、システムポリシーが優先されることを確認
    (受け入れ基準: ユーザーが3秒指定でも8秒待つ)
    """
    throttler = RequestThrottler({"data.jma.go.jp": 8.0})
    url = make_url("data.jma.go.jp")
    # 1回目: 0.0, 2回目: 1.0, 2回目の更新用: 8.0, 念のため4つ
    mock_monotonic.side_effect = [0.0, 1.0, 8.0, 15.0]

    throttler.wait_if_needed(url, user_interval_sec=3.0)  # 1回目
    throttler.wait_if_needed(url, user_interval_sec=3.0)  # 2回目

    time.sleep.assert_called_once_with(pytest.approx(7.0))

@patch('time.sleep', MagicMock())
@patch('time.monotonic')
def test_wait_if_needed_uses_user_interval_if_longer(mock_monotonic):
    """
    ユーザー指定値がシステムポリシーより長い場合、ユーザー指定値が使われることを確認
    """
    throttler = RequestThrottler(test_policies)
    url = make_url("test.domain.com")
    # 1回目: 100.0, 2回目: 102.0, 2回目の更新用: 110.0, 念のため4つ
    mock_monotonic.side_effect = [100.0, 102.0, 110.0, 120.0]

    throttler.wait_if_needed(url, user_interval_sec=10.0)
    throttler.wait_if_needed(url, user_interval_sec=10.0)

    time.sleep.assert_called_once_with(pytest.approx(8.0))

@patch('time.sleep', MagicMock())
@patch('time.monotonic')
def test_wait_if_needed_does_not_wait_if_time_passed(mock_monotonic):
    """
    十分な時間が経過していれば待機しないことを確認
    """
    throttler = RequestThrottler(test_policies)
    url = make_url("test.domain.com")
    # 1回目: 200.0, 2回目: 206.0, 2回目の更新用: 212.0, 念のため4つ
    mock_monotonic.side_effect = [200.0, 206.0, 212.0, 220.0]

    throttler.wait_if_needed(url, user_interval_sec=5.0)
    throttler.wait_if_needed(url, user_interval_sec=5.0)

    time.sleep.assert_not_called()
