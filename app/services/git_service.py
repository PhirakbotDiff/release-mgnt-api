from git import Repo, Actor # type: ignore
import urllib.parse
import base64
from app.config import settings
import os
import logging

logger = logging.getLogger("api")

author = Actor(
    name=settings.GIT_AUTHOR_NAME,
    email=settings.GIT_AUTHOR_EMAIL
)

class GitService:
    
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.encoded_token = urllib.parse.quote(settings.GIT_TOKEN, safe='')
        self.repo_url = f"https://{settings.GIT_USERNAME}:{self.encoded_token}@gitscm-uat.vattanacbrewery.com/devops/manifest_repo"

    def clone_or_pull(self):
        custom_env = {
            "GIT_ASKPASS": "echo",
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_HTTP_USER_AGENT": "git-python",
        }
            
        if not os.path.exists(self.repo_path):
            return Repo.clone_from(
                self.repo_url,
                self.repo_path,
                branch=settings.MANIFEST_REPO_BRANCH,
                env=custom_env
            )

        repo = Repo(self.repo_path)
        repo.remotes.origin.set_url(self.repo_path)
        repo.remotes.origin.pull()
        
        return repo

    def commit_and_push(self, message: str):
        repo = Repo(self.repo_path)
        # Stage all changes (including untracked)
        repo.index.add(repo.untracked_files)
        repo.git.add(update=True)
        commit = repo.index.commit(
            message,
            author=author
        )

        repo.remotes.origin.set_url(self.repo_url)

        try:
            push_info = repo.remotes.origin.push()
            for info in push_info:
                if info.flags & info.ERROR:
                    logger.exception(f"Push failed: {info.summary}")
                    raise Exception(f"Push failed: {info.summary}")
        except Exception as e:
            logger.exception(f"Push error: {str(e)}")
            print(f"Push error: {e}")
        
        return commit.hexsha
