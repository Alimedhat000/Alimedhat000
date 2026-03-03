import datetime
from dateutil import relativedelta
import requests
import os
import time
import yaml
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from xml.dom import minidom
from src.svg_parser import SVGParser
from src.commits_cache import CommitsCacheManager


def load_config(path: str = "profile.yaml") -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class GitHubStatsTracker:
    def __init__(
        self, username: str = None, access_token: str = None, config: Dict = None
    ):
        """
        Initialize the GitHub Stats Tracker with authentication details.

        Args:
            username (str, optional): GitHub username. Defaults to environment variable.
            access_token (str, optional): GitHub personal access token. Defaults to environment variable.
            config (dict, optional): Loaded profile config. Defaults to loading profile.yaml.
        """
        load_dotenv(".env")

        self.config = config or load_config()
        self.username = username or os.getenv("USER_NAME")
        self.access_token = access_token or os.getenv("ACCESS_TOKEN")

        if not self.username or not self.access_token:
            raise ValueError("GitHub username and access token must be provided")

        self.headers = {"authorization": f"token {self.access_token}"}
        self.query_count: Dict[str, int] = {
            "user_getter": 0,
            "follower_getter": 0,
            "graph_repos_stars": 0,
            "recursive_loc": 0,
            "graph_commits": 0,
            "loc_query": 0,
        }

        # Fetch user data on initialization
        self.user_id, self.account_created_at = self.get_user_info()

        self.parser = SVGParser()
        self.parsed_data = self.find_data_from_githubcard()

        self.commits_cache = CommitsCacheManager()

    def find_data_from_githubcard(self):
        url = f"https://github-profile-summary-cards.vercel.app/api/cards/stats?username={self.username}"

        svg_content = self.parser.fetch_svg(url)
        if svg_content:
            return self.parser.parse_svg(svg_content)

    def _make_graphql_request(self, query: str, variables: Dict) -> requests.Response:
        """
        Make a GraphQL request to GitHub API with error handling.

        Args:
            query (str): GraphQL query string
            variables (dict): Variables for the query

        Returns:
            requests.Response: API response
        """
        try:
            response = requests.post(
                "https://api.github.com/graphql",
                json={"query": query, "variables": variables},
                headers=self.headers,
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            raise Exception(f"GitHub API request failed: {e}")

    def get_user_info(self) -> Tuple[str, str]:
        """
        Retrieve user's GitHub account ID and creation time.

        Returns:
            Tuple containing user ID and account creation timestamp
        """
        self._increment_query_count("user_getter")
        query = """
        query($login: String!){
            user(login: $login) {
                id
                createdAt
            }
        }"""
        variables = {"login": self.username}

        response = self._make_graphql_request(query, variables)
        data = response.json()["data"]["user"]
        return data["id"], data["createdAt"]

    def calculate_age(self, birthday: datetime.date) -> str:
        """
        Calculate time since birthday with optional birthday emoji.

        Args:
            birthday (datetime.date): Birth date to calculate from

        Returns:
            str: Formatted age string
        """
        diff = relativedelta.relativedelta(datetime.datetime.today(), birthday)

        def pluralize(unit: int) -> str:
            return "s" if unit != 1 else ""

        return (
            f"{diff.years} year{pluralize(diff.years)}, "
            f"{diff.months} month{pluralize(diff.months)}, "
            f"{diff.days} day{pluralize(diff.days)}"
            f" {'🎂' if (diff.months == 0 and diff.days == 0) else ''}"
        )

    def get_repository_count(self, owner_affiliation: List[str] = ["OWNER"]) -> int:
        """
        Get total repository count for the user.

        Args:
            owner_affiliation (List[str], optional): Repository ownership filter

        Returns:
            int: Total number of repositories
        """
        self._increment_query_count("graph_repos_stars")

        query = """
        query ($owner_affiliation: [RepositoryAffiliation], $login: String!, $cursor: String) {
            user(login: $login) {
                repositories(first: 100, after: $cursor, ownerAffiliations: $owner_affiliation) {
                    totalCount
                }
            }
        }"""

        variables = {
            "owner_affiliation": owner_affiliation,
            "login": self.username,
            "cursor": None,
        }

        response = self._make_graphql_request(query, variables)
        return response.json()["data"]["user"]["repositories"]["totalCount"]

    def update_svg_file(self, filename: str, age_data: str, repo_data: str) -> None:
        """
        Update SVG file with static config values and live GitHub stats.

        Args:
            filename (str): Path to SVG file
            age_data (str): Calculated age string
            repo_data (str): Repository count
        """

        def set_by_id(doc, element_id: str, value: str) -> None:
            for node in doc.getElementsByTagName("tspan"):
                if node.getAttribute("id") == element_id:
                    node.firstChild.data = value  # type: ignore[union-attr]
                    return
            raise KeyError(f"SVG element with id='{element_id}' not found")

        svg = minidom.parse(filename)
        cfg = self.config

        # Static fields from config
        set_by_id(svg, "username", str(cfg["personal"]["username_header"]))
        set_by_id(svg, "val-os", str(cfg["system"]["os"]))
        set_by_id(svg, "val-host", str(cfg["system"]["host"]))
        set_by_id(svg, "val-kernel", str(cfg["system"]["kernel"]))
        set_by_id(svg, "val-ide", str(cfg["system"]["ide"]))
        set_by_id(svg, "val-lang-prog", str(cfg["languages"]["programming"]))
        set_by_id(svg, "val-lang-fw", str(cfg["languages"]["frameworks"]))
        set_by_id(svg, "val-hobbies-sw", str(cfg["hobbies"]["software"]))
        set_by_id(svg, "val-hobbies-hw", str(cfg["hobbies"]["hardware"]))
        set_by_id(svg, "val-email", str(cfg["contact"]["email"]))
        set_by_id(svg, "val-linkedin", str(cfg["contact"]["linkedin"]))
        set_by_id(svg, "val-leetcode", str(cfg["contact"]["leetcode"]))
        set_by_id(svg, "val-discord", str(cfg["contact"]["discord"]))
        set_by_id(svg, "val-loc", str(cfg["stats"]["loc"]))

        # Dynamic fields — computed at runtime
        set_by_id(svg, "val-uptime", age_data)
        set_by_id(svg, "val-repos", repo_data)
        set_by_id(svg, "val-commits", str(self.commits_cache.get_total_commits()))

        with open(filename, mode="w", encoding="utf-8") as f:
            f.write(svg.toxml("utf-8").decode("utf-8"))

    def _increment_query_count(self, function_name: str) -> None:
        """
        Increment query count for a specific function.

        Args:
            function_name (str): Name of the function making the API call
        """
        self.query_count[function_name] += 1

    def performance_track(self, func, *args):
        """
        Track performance of a function.

        Args:
            func (callable): Function to track
            *args: Arguments for the function

        Returns:
            Tuple of function return and execution time
        """
        start = time.perf_counter()
        func_return = func(*args)
        exec_time = time.perf_counter() - start
        return func_return, exec_time

    def print_performance_summary(self, performance_data: List[Tuple]) -> None:
        """
        Print performance summary and query statistics.

        Args:
            performance_data (List[Tuple]): List of performance tracking results
        """
        total_time = 0
        print("Calculation times:")

        for query_type, (result, diff) in performance_data:
            print(f"   {query_type + ':':<23}", end="")

            if diff > 1:
                print(f"{diff:>12.4f} s")
            else:
                print(f"{diff * 1000:>12.4f} ms")

            total_time += diff

        print(f"{'Total function time:':<21} {total_time:>11.4f}")

        print(f"Total GitHub GraphQL API calls: {sum(self.query_count.values()):>3}")
        for func_name, count in self.query_count.items():
            print(f"   {func_name + ':':<28} {count:>6}")


def main():
    config = load_config()
    tracker = GitHubStatsTracker(config=config)

    performance_data = []

    tracker.commits_cache.update_commits(
        tracker.username,  # type: ignore[arg-type]
        tracker.parsed_data["Commits"],  # type: ignore[index]
        year=datetime.date.today().year,
    )

    # Birthday from config
    birthday = datetime.date.fromisoformat(str(config["personal"]["birthday"]))

    # Track age calculation
    age_data, age_time = tracker.performance_track(tracker.calculate_age, birthday)
    performance_data.append(("age calculation", (age_data, age_time)))

    # Track repository count
    repo_data, repo_time = tracker.performance_track(tracker.get_repository_count)
    performance_data.append(("my repositories", (repo_data, repo_time)))

    # Update SVG file
    svg_file = config["svg"]["file"]
    tracker.update_svg_file(svg_file, age_data, f"{repo_data:,}")

    # Print performance summary
    tracker.print_performance_summary(performance_data)
