import os

GIT_REPO_PATH = os.getenv("GIT_REPO_PATH", ".")

def read_git_file(filepath: str) -> str:
    """
    謖・ｮ壹＆繧後◆Git繝ｪ繝昴ず繝医Μ蜀・・繝輔ぃ繧､繝ｫ繧定ｪｭ縺ｿ蜃ｺ縺咎未謨ｰ
    :param filepath: GIT_REPO_PATH縺九ｉ縺ｮ逶ｸ蟇ｾ繝代せ
    :return: 繝輔ぃ繧､繝ｫ蜀・ｮｹ・域枚蟄怜・・・
    """
    full_path = os.path.join(GIT_REPO_PATH, filepath)

    if not os.path.isfile(full_path):
        raise FileNotFoundError(f"謖・ｮ壹＆繧後◆繝輔ぃ繧､繝ｫ縺悟ｭ伜惠縺励∪縺帙ｓ: {full_path}")

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        raise ValueError(f"繝・く繧ｹ繝医ヵ繧｡繧､繝ｫ縺ｨ縺励※隱ｭ縺ｿ霎ｼ繧√∪縺帙ｓ: {full_path}")
    except Exception as e:
        raise RuntimeError(f"繝輔ぃ繧､繝ｫ縺ｮ隱ｭ縺ｿ霎ｼ縺ｿ荳ｭ縺ｫ莠域悄縺帙〓繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆: {str(e)}")
