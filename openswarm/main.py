#!/usr/bin/env python

import logging
import time

from dataclasses import dataclass
from enum import Enum

import click
import structlog

from tqdm import tqdm

from rich.console import Console
from rich.live import Live
from rich.table import Table


@dataclass
class ProjectConfig():
    name: str
    url: str
    build_cmd: str


@click.group()
@click.pass_context
def main(ctx):
    pass

if __name__ == "__main__":
    main(obj={})
