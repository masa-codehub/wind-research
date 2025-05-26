import logging
import sys
from logging import FileHandler, Formatter, StreamHandler

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
DEFAULT_LOG_LEVEL = "INFO"


def setup_logging(log_level: str = DEFAULT_LOG_LEVEL, log_file_path: str = "wind-research.log"):
    """
    アプリケーションのロギングを設定する。

    :param log_level: 設定するログレベル（文字列）。
    :param log_file_path: ログファイルの出力パス。
    """
    if log_level.upper() not in LOG_LEVELS:
        log_level = DEFAULT_LOG_LEVEL

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level.upper())

    # 既存のハンドラをクリア
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    log_format = Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # コンソールハンドラ
    console_handler = StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)

    # ファイルハンドラ
    log_dir = os.path.dirname(log_file_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    file_handler = FileHandler(log_file_path, mode='a', encoding='utf-8')
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)

    # 例外発生時のスタックトレースもログに出力（exc_info=Trueで呼び出し側が制御）
