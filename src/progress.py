from typing import Generator

from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)


class Spinner:
    def __init__(self, console: Console = None, task: str = "Working"):
        if not console:
            console = Console()
        self.console = console
        self.task = task

    def __enter__(self) -> Generator[Progress, None, None]:
        with Progress(
            TextColumn("  "),
            TimeElapsedColumn(),
            TextColumn("[purple]{task.description}"),
            SpinnerColumn("simpleDots"),
            console=self.console,
        ) as p:
            p.add_task(description=self.task)
            yield p

    def __exit__(self, *exit_args):
        pass


class ProgressBar(Progress):
    def get_renderables(self):
        for task in self.tasks:
            if task.fields.get("progress_type") == "green":
                self.columns = (
                    "[green]{task.description}",
                    BarColumn(),
                    MofNCompleteColumn(),
                    TimeElapsedColumn(),
                    "•",
                    TimeRemainingColumn(),
                )
            if task.fields.get("progress_type") == "blue":
                self.columns = (
                    "[blue]{task.description}",
                    SpinnerColumn(),
                    TimeElapsedColumn(),
                )
            yield self.make_tasks_table([task])
