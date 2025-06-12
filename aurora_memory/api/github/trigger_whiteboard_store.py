import logging
import sys

# カスタムロガー設定
logger = logging.getLogger("WhiteboardLogger")
logger.setLevel(logging.INFO)

# 既存のHandlerを除去（再読み込み対応）
logger.handlers.clear()

# コンソール出力用のHandler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# 出力フォーマット設定（色付きログにも拡張可能）
formatter = logging.Formatter("[%(asctime)s] 🧭 %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

# 外部から利用するラッパー関数
def log(message: str, level: str = "info"):
    """
    ログを出力するユーティリティ関数

    Args:
        message (str): 出力するログメッセージ
        level (str): ログレベル（info, warning, error, debug）
    """
    level = level.lower()
    if level == "debug":
        logger.debug(message)
    elif level == "warning":
        logger.warning(message)
    elif level == "error":
        logger.error(message)
    else:
        logger.info(message)
