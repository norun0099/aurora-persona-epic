import os

GIT_REPO_PATH = os.getenv("GIT_REPO_PATH", ".")

def read_git_file(filepath: str) -> str:
    """
    持E��されたGitリポジトリ冁E�Eファイルを読み出す関数
    :param filepath: GIT_REPO_PATHからの相対パス
    :return: ファイル冁E���E�文字�E�E�E
    """
    full_path = os.path.join(GIT_REPO_PATH, filepath)

    if not os.path.isfile(full_path):
        raise FileNotFoundError(f"持E��されたファイルが存在しません: {full_path}")

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        raise ValueError(f"チE��ストファイルとして読み込めません: {full_path}")
    except Exception as e:
        raise RuntimeError(f"ファイルの読み込み中に予期せぬエラーが発生しました: {str(e)}")
