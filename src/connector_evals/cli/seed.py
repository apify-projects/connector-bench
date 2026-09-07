import os
from pathlib import Path
from typing import Annotated

import typer
from dotenv import load_dotenv
from rich.console import Console
from typer import Argument, Option

from connector_evals.notion_fixtures import seed_notion

console = Console()


def seed_command(
    app_name: Annotated[
        str, Argument(help="App to seed fixtures for. Only 'notion' for now.")
    ],
    env_file: Annotated[
        Path | None,
        Option("--env-file", help="Path to a .env file to load.", show_default=False),
    ] = None,
) -> None:
    if app_name != "notion":
        raise typer.BadParameter(f"No fixture seeder for app '{app_name}'")

    if env_file is not None:
        if not env_file.exists():
            console.print(f"[red]Env file not found: {env_file}[/red]")
            raise typer.Exit(code=1)
        load_dotenv(env_file, override=True)
    elif Path(".env").exists():
        load_dotenv(".env", override=False)

    token = os.environ.get("NOTION_API_TOKEN")
    parent = os.environ.get("NOTION_PARENT_PAGE_ID")
    if not token or not parent:
        console.print(
            "[red]NOTION_API_TOKEN and NOTION_PARENT_PAGE_ID are required "
            "(create an internal integration at notion.so/profile/integrations, "
            "share a parent page with it, put both in .env).[/red]"
        )
        raise typer.Exit(code=1)

    seed_notion(token, parent, log=console.print)
