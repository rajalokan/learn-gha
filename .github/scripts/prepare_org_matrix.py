#!/usr/bin/env python3
"""Prepare the organization matrix for the multiorg workflow."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import List, Optional

def _fetch_all_orgs(installation_token: str) -> List[str]:
    """Fetch all organization logins accessible with the installation token."""
    headers = {
        "Authorization": f"token {installation_token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "multiorg-script-runner",
    }

    orgs: List[str] = []
    url: Optional[str] = "https://api.github.com/user/installations?per_page=100"
    while url:
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode("utf-8"))
            installations = data.get("installations", [])
            for installation in installations:
                if installation.get("target_type") == "Organization":
                    account = installation.get("account") or {}
                    login = account.get("login")
                    if login:
                        orgs.append(login)

            link_header = response.headers.get("Link")
            next_url: Optional[str] = None
            if link_header:
                parts = [part.strip() for part in link_header.split(",")]
                for part in parts:
                    if ";" not in part:
                        continue
                    link, rel = [segment.strip() for segment in part.split(";", 1)]
                    if rel == 'rel="next"':
                        next_url = link.strip("<>")
                        break
            url = next_url

    return sorted(set(orgs))


def main() -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        raise RuntimeError("GITHUB_OUTPUT environment variable is not set.")

    raw = os.getenv("ORG_NAMES") or ""
    provided = [value.strip() for value in raw.split(",") if value.strip()]
    has_all_flag = "ORG_ALL" in provided

    if has_all_flag:
        installation_token = os.getenv("INSTALLATION_TOKEN")
        if not installation_token:
            raise RuntimeError("ORG_ALL requested but INSTALLATION_TOKEN is missing.")
        orgs: Optional[List[str]] = _fetch_all_orgs(installation_token)
    elif provided:
        orgs = [value for value in provided if value != "ORG_ALL"]
    else:
        orgs = None

    if isinstance(orgs, list) and not orgs:
        if has_all_flag:
            raise RuntimeError("Organization list is empty when fetching all organizations.")
        raise RuntimeError("Organization list is empty.")

    value = "[null]" if orgs is None else json.dumps(orgs)
    with open(output_path, "a", encoding="utf-8") as handle:
        handle.write(f"org-matrix={value}\n")


if __name__ == "__main__":
    main()
