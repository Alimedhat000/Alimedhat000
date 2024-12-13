import json
import os
import datetime
from typing import Dict, Any


class CommitsCacheManager:
    def __init__(self, cache_file: str = 'commits_cache.json'):
        """
        Initialize the commits cache manager.
        """
        self.cache_file = cache_file
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        """
        Load existing cache from file or create a new one.
        """
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            return {}
        except (json.JSONDecodeError, IOError):
            return {}

    def update_commits(self, username: str, year_commits: Dict[str, int]) -> None:
        """
        Update commits cache for a specific user.
        """
        # Create user entry if not exists
        if username not in self.cache:
            self.cache[username] = {}

        # Update commits for each year
        self.cache[username].update(year_commits)

        # Save updated cache
        self._save_cache()

    def get_cached_commits(self, username: str) -> Dict[str, int]:
        """
        Retrieve cached commits for a user.
        """
        return self.cache.get(username, {})

    def _save_cache(self) -> None:
        """
        Save cache to JSON file.
        """
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=4)
        except IOError as e:
            print(f"Error saving commits cache: {e}")

    def clean_outdated_cache(self, max_age_years: int = 10) -> None:
        """
        Remove commit data older than specified years.
        """
        current_year = datetime.datetime.now().year

        for username in list(self.cache.keys()):
            # Filter out years older than max_age_years
            filtered_commits = {
                str(year): commits
                for year, commits in self.cache[username].items()
                if current_year - int(year) <= max_age_years
            }

            # Update cache for this user
            self.cache[username] = filtered_commits

        # Save updated cache
        self._save_cache()

    def get_total_commits(self) -> int:
        """
        Get the total number of commits across all users and years.
        """
        total_commits = 0
        for user_commits in self.cache.values():
            total_commits += sum(user_commits.values())
        return total_commits
