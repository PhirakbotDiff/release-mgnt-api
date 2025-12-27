from git import Repo
from app.config import settings
import os

class GitService:
    def __init__(self):
        self.repo_path = settings.MANIFEST_LOCAL_PATH

    def clone_or_pull(self):
        if not os.path.exists(self.repo_path):
            return Repo.clone_from(
                settings.MANIFEST_REPO_URL,
                self.repo_path,
                branch=settings.MANIFEST_REPO_BRANCH
            )
        repo = Repo(self.repo_path)
        repo.remotes.origin.pull()
        return repo

    def commit_and_push(self, message: str):
        repo = Repo(self.repo_path)
        repo.index.add(["."])
        commit = repo.index.commit(
            message,
            author=settings.GIT_AUTHOR_NAME
        )
        repo.remotes.origin.push()
        return commit.hexsha
