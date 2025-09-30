import os

GIT_REPO_PATH = os.getenv("GIT_REPO_PATH", ".")

def read_git_file(filepath: str) -> str:
    """
    指定されたGitリポジトリ内のファイルを読み出す関数
    :param filepath: GIT_REPO_PATHからの相対パス
    :return: ファイル内容（文字列）
    """
    full_path = os.path.join(GIT_REPO_PATH, filepath)

    if not os.path.isfile(full_path):
        raise FileNotFoundError(f"指定されたファイルが存在しません: {full_path}")

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        raise ValueError(f"テキストファイルとして読み込めません: {full_path}")
    except Exception as e:
        raise RuntimeError(f"ファイルの読み込み中に予期せぬエラーが発生しました: {str(e)}")
