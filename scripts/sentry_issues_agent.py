#!/usr/bin/env python3
"""
Sentry Issues Agent - Interactive CLI tool for managing Sentry issues.

This agent provides an easy-to-use interface for querying, filtering, and
managing issues in your Sentry project without memorizing complex CLI commands.

Usage:
    # Interactive mode
    ./scripts/sentry_issues_agent.py

    # Direct commands
    ./scripts/sentry_issues_agent.py list
    ./scripts/sentry_issues_agent.py list --status unresolved --limit 10
    ./scripts/sentry_issues_agent.py details <ISSUE_ID>
    ./scripts/sentry_issues_agent.py resolve <ISSUE_ID>
    ./scripts/sentry_issues_agent.py stats
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# Color codes for terminal output
class Colors:
  """ANSI color codes for terminal output."""
  RED = '\033[0;31m'
  GREEN = '\033[0;32m'
  YELLOW = '\033[1;33m'
  BLUE = '\033[0;34m'
  MAGENTA = '\033[0;35m'
  CYAN = '\033[0;36m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'
  NC = '\033[0m'  # No Color


@dataclass
class SentryConfig:
  """Sentry configuration from .sentryclirc."""
  org: str
  project: str
  url: str

  @classmethod
  def load(cls) -> 'SentryConfig':
    """Load configuration from .sentryclirc file.

    Returns:
      SentryConfig: Configuration object with org, project, and url.

    Raises:
      FileNotFoundError: If .sentryclirc is not found.
      ValueError: If configuration is invalid.
    """
    project_root = Path(__file__).parent.parent
    config_file = project_root / '.sentryclirc'

    if not config_file.exists():
      raise FileNotFoundError(
        f"Configuration file not found: {config_file}\n"
        "Please run the Sentry CLI setup first."
      )

    config = {}
    with open(config_file) as f:
      current_section = None
      for line in f:
        line = line.strip()
        if line.startswith('[') and line.endswith(']'):
          current_section = line[1:-1]
        elif '=' in line and current_section == 'defaults':
          key, value = line.split('=', 1)
          config[key.strip()] = value.strip()

    # Validate configuration
    if 'YOUR_ORG_SLUG' in config.get('org', '') or 'YOUR_AUTH_TOKEN' in open(config_file).read():
      raise ValueError(
        "Configuration contains placeholder values.\n"
        "Please update .sentryclirc with your actual credentials.\n"
        "See docs/SENTRY_CLI_SETUP.md for instructions."
      )

    return cls(
      org=config.get('org', ''),
      project=config.get('project', ''),
      url=config.get('url', 'https://sentry.io/')
    )


class SentryAgent:
  """Agent for interacting with Sentry issues via CLI."""

  def __init__(self, config: SentryConfig):
    """Initialize the Sentry agent.

    Args:
      config: Sentry configuration object.
    """
    self.config = config
    self._verify_cli()

  def _verify_cli(self) -> None:
    """Verify that sentry-cli is installed and configured.

    Raises:
      RuntimeError: If sentry-cli is not available or not authenticated.
    """
    try:
      result = subprocess.run(
        ['sentry-cli', '--version'],
        capture_output=True,
        text=True,
        check=True
      )
      print(f"{Colors.GREEN}✓ Sentry CLI: {result.stdout.strip()}{Colors.NC}")
    except FileNotFoundError:
      raise RuntimeError(
        f"{Colors.RED}Error: sentry-cli is not installed{Colors.NC}\n"
        "Install it with: brew install getsentry/tools/sentry-cli"
      )
    except subprocess.CalledProcessError:
      raise RuntimeError(f"{Colors.RED}Error: sentry-cli is not working properly{Colors.NC}")

    # Verify authentication
    try:
      subprocess.run(
        ['sentry-cli', 'info'],
        capture_output=True,
        check=True
      )
      print(f"{Colors.GREEN}✓ Authentication successful{Colors.NC}")
    except subprocess.CalledProcessError:
      raise RuntimeError(
        f"{Colors.RED}Error: Sentry authentication failed{Colors.NC}\n"
        "Please check your .sentryclirc configuration."
      )

  def _run_command(self, cmd: list[str], capture_json: bool = False) -> str | dict[str, Any]:
    """Run a sentry-cli command and return the output.

    Args:
      cmd: Command arguments to pass to sentry-cli.
      capture_json: If True, parse output as JSON.

    Returns:
      Command output as string or parsed JSON dict.

    Raises:
      subprocess.CalledProcessError: If command fails.
    """
    full_cmd = ['sentry-cli'] + cmd
    result = subprocess.run(
      full_cmd,
      capture_output=True,
      text=True,
      check=True
    )

    if capture_json:
      try:
        return json.loads(result.stdout)
      except json.JSONDecodeError:
        return result.stdout

    return result.stdout

  def list_issues(
    self,
    status: str = 'unresolved',
    limit: int = 20,
    query: str = ''
  ) -> None:
    """List issues from Sentry.

    Args:
      status: Issue status filter (unresolved, resolved, ignored).
      limit: Maximum number of issues to display.
      query: Additional search query.
    """
    print(f"\n{Colors.BOLD}{Colors.BLUE}Fetching issues from Sentry...{Colors.NC}\n")
    print(f"Organization: {Colors.CYAN}{self.config.org}{Colors.NC}")
    print(f"Project: {Colors.CYAN}{self.config.project}{Colors.NC}")
    print(f"Status: {Colors.CYAN}{status}{Colors.NC}")
    print(f"Limit: {Colors.CYAN}{limit}{Colors.NC}\n")

    try:
      cmd = [
        'issues', 'list',
        '--org', self.config.org,
        '--project', self.config.project,
        '--status', status
      ]

      if query:
        cmd.extend(['--query', query])

      output = self._run_command(cmd)

      # Parse and display issues
      lines = output.strip().split('\n')
      if not lines or len(lines) < 2:
        print(f"{Colors.YELLOW}No issues found.{Colors.NC}")
        return

      # Display header
      print(f"{Colors.BOLD}{lines[0]}{Colors.NC}")
      print("─" * 80)

      # Display issues (limit the number)
      displayed = 0
      for line in lines[1:]:
        if line.strip() and displayed < limit:
          # Color code based on content
          if 'error' in line.lower() or 'exception' in line.lower():
            print(f"{Colors.RED}{line}{Colors.NC}")
          elif 'warning' in line.lower():
            print(f"{Colors.YELLOW}{line}{Colors.NC}")
          else:
            print(line)
          displayed += 1

      if len(lines) - 1 > limit:
        print(f"\n{Colors.YELLOW}... and {len(lines) - 1 - limit} more issues{Colors.NC}")

      print(f"\n{Colors.GREEN}Total issues displayed: {displayed}{Colors.NC}")

    except subprocess.CalledProcessError as e:
      print(f"{Colors.RED}Error fetching issues: {e.stderr}{Colors.NC}")
      sys.exit(1)

  def get_issue_details(self, issue_id: str) -> None:
    """Get detailed information about a specific issue.

    Args:
      issue_id: The Sentry issue ID.
    """
    print(f"\n{Colors.BOLD}{Colors.BLUE}Fetching issue details...{Colors.NC}\n")

    try:
      # Get issue details using events command
      cmd = [
        'events', 'list',
        '--org', self.config.org,
        '--project', self.config.project
      ]

      output = self._run_command(cmd)
      print(output)

      # Provide direct link
      url = f"{self.config.url}organizations/{self.config.org}/issues/{issue_id}/"
      print(f"\n{Colors.CYAN}View in browser: {url}{Colors.NC}")

    except subprocess.CalledProcessError as e:
      print(f"{Colors.RED}Error fetching issue details: {e.stderr}{Colors.NC}")
      sys.exit(1)

  def resolve_issue(self, issue_id: str) -> None:
    """Resolve a Sentry issue.

    Args:
      issue_id: The Sentry issue ID to resolve.
    """
    print(f"\n{Colors.YELLOW}Resolving issue {issue_id}...{Colors.NC}\n")

    try:
      cmd = [
        'issues', 'resolve',
        '--org', self.config.org,
        '--project', self.config.project,
        issue_id
      ]

      output = self._run_command(cmd)
      print(f"{Colors.GREEN}✓ Issue resolved successfully{Colors.NC}")
      print(output)

    except subprocess.CalledProcessError as e:
      print(f"{Colors.RED}Error resolving issue: {e.stderr}{Colors.NC}")
      sys.exit(1)

  def unresolve_issue(self, issue_id: str) -> None:
    """Unresolve a Sentry issue.

    Args:
      issue_id: The Sentry issue ID to unresolve.
    """
    print(f"\n{Colors.YELLOW}Unresolving issue {issue_id}...{Colors.NC}\n")

    try:
      cmd = [
        'issues', 'unresolve',
        '--org', self.config.org,
        '--project', self.config.project,
        issue_id
      ]

      output = self._run_command(cmd)
      print(f"{Colors.GREEN}✓ Issue unresolved successfully{Colors.NC}")
      print(output)

    except subprocess.CalledProcessError as e:
      print(f"{Colors.RED}Error unresolving issue: {e.stderr}{Colors.NC}")
      sys.exit(1)

  def get_stats(self) -> None:
    """Display project statistics and recent activity."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}Sentry Project Statistics{Colors.NC}\n")
    print(f"Organization: {Colors.CYAN}{self.config.org}{Colors.NC}")
    print(f"Project: {Colors.CYAN}{self.config.project}{Colors.NC}\n")

    statuses = ['unresolved', 'resolved']

    for status in statuses:
      try:
        cmd = [
          'issues', 'list',
          '--org', self.config.org,
          '--project', self.config.project,
          '--status', status
        ]

        output = self._run_command(cmd)
        lines = output.strip().split('\n')
        count = max(0, len(lines) - 1)  # Subtract header

        color = Colors.RED if status == 'unresolved' and count > 0 else Colors.GREEN
        print(f"{color}{status.capitalize()} issues: {count}{Colors.NC}")

      except subprocess.CalledProcessError:
        print(f"{Colors.YELLOW}{status.capitalize()} issues: Unable to fetch{Colors.NC}")

    # Provide dashboard link
    dashboard_url = f"{self.config.url}organizations/{self.config.org}/issues/?project={self.config.project}"
    print(f"\n{Colors.CYAN}Dashboard: {dashboard_url}{Colors.NC}\n")

  def interactive_mode(self) -> None:
    """Run the agent in interactive mode."""
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}╔═══════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}║   Sentry Issues Agent - Interactive Mode  ║{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}╚═══════════════════════════════════════════╝{Colors.NC}\n")

    print(f"{Colors.CYAN}Available commands:{Colors.NC}")
    print("  list [status] [limit]  - List issues (default: unresolved, 20)")
    print("  details <issue_id>     - Get issue details")
    print("  resolve <issue_id>     - Resolve an issue")
    print("  unresolve <issue_id>   - Unresolve an issue")
    print("  stats                  - Show project statistics")
    print("  help                   - Show this help message")
    print("  quit/exit              - Exit interactive mode")
    print()

    while True:
      try:
        user_input = input(f"{Colors.BOLD}{Colors.GREEN}sentry>{Colors.NC} ").strip()

        if not user_input:
          continue

        parts = user_input.split()
        command = parts[0].lower()

        if command in ['quit', 'exit', 'q']:
          print(f"\n{Colors.CYAN}Goodbye!{Colors.NC}\n")
          break

        elif command == 'help':
          print(f"\n{Colors.CYAN}Available commands:{Colors.NC}")
          print("  list [status] [limit]  - List issues")
          print("  details <issue_id>     - Get issue details")
          print("  resolve <issue_id>     - Resolve an issue")
          print("  unresolve <issue_id>   - Unresolve an issue")
          print("  stats                  - Show project statistics")
          print("  help                   - Show this help message")
          print("  quit/exit              - Exit interactive mode")
          print()

        elif command == 'list':
          status = parts[1] if len(parts) > 1 else 'unresolved'
          limit = int(parts[2]) if len(parts) > 2 else 20
          self.list_issues(status=status, limit=limit)

        elif command == 'details':
          if len(parts) < 2:
            print(f"{Colors.RED}Error: Please provide an issue ID{Colors.NC}")
            continue
          self.get_issue_details(parts[1])

        elif command == 'resolve':
          if len(parts) < 2:
            print(f"{Colors.RED}Error: Please provide an issue ID{Colors.NC}")
            continue
          self.resolve_issue(parts[1])

        elif command == 'unresolve':
          if len(parts) < 2:
            print(f"{Colors.RED}Error: Please provide an issue ID{Colors.NC}")
            continue
          self.unresolve_issue(parts[1])

        elif command == 'stats':
          self.get_stats()

        else:
          print(f"{Colors.RED}Unknown command: {command}{Colors.NC}")
          print(f"Type {Colors.CYAN}'help'{Colors.NC} for available commands")

      except KeyboardInterrupt:
        print(f"\n{Colors.CYAN}Goodbye!{Colors.NC}\n")
        break
      except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.NC}")


def main() -> None:
  """Main entry point for the Sentry issues agent."""
  parser = argparse.ArgumentParser(
    description='Interactive agent for managing Sentry issues',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
  # Interactive mode
  %(prog)s

  # List unresolved issues
  %(prog)s list

  # List resolved issues with limit
  %(prog)s list --status resolved --limit 10

  # Get issue details
  %(prog)s details 12345

  # Resolve an issue
  %(prog)s resolve 12345

  # Show statistics
  %(prog)s stats
    """
  )

  subparsers = parser.add_subparsers(dest='command', help='Command to execute')

  # List command
  list_parser = subparsers.add_parser('list', help='List issues')
  list_parser.add_argument(
    '--status',
    default='unresolved',
    choices=['unresolved', 'resolved', 'ignored'],
    help='Issue status filter'
  )
  list_parser.add_argument(
    '--limit',
    type=int,
    default=20,
    help='Maximum number of issues to display'
  )
  list_parser.add_argument(
    '--query',
    default='',
    help='Additional search query'
  )

  # Details command
  details_parser = subparsers.add_parser('details', help='Get issue details')
  details_parser.add_argument('issue_id', help='Issue ID')

  # Resolve command
  resolve_parser = subparsers.add_parser('resolve', help='Resolve an issue')
  resolve_parser.add_argument('issue_id', help='Issue ID to resolve')

  # Unresolve command
  unresolve_parser = subparsers.add_parser('unresolve', help='Unresolve an issue')
  unresolve_parser.add_argument('issue_id', help='Issue ID to unresolve')

  # Stats command
  subparsers.add_parser('stats', help='Show project statistics')

  args = parser.parse_args()

  try:
    # Load configuration
    config = SentryConfig.load()
    agent = SentryAgent(config)

    # Execute command or enter interactive mode
    if args.command == 'list':
      agent.list_issues(
        status=args.status,
        limit=args.limit,
        query=args.query
      )
    elif args.command == 'details':
      agent.get_issue_details(args.issue_id)
    elif args.command == 'resolve':
      agent.resolve_issue(args.issue_id)
    elif args.command == 'unresolve':
      agent.unresolve_issue(args.issue_id)
    elif args.command == 'stats':
      agent.get_stats()
    else:
      # No command specified, enter interactive mode
      agent.interactive_mode()

  except (FileNotFoundError, ValueError, RuntimeError) as e:
    print(f"{Colors.RED}{e}{Colors.NC}", file=sys.stderr)
    sys.exit(1)
  except KeyboardInterrupt:
    print(f"\n{Colors.CYAN}Interrupted by user{Colors.NC}")
    sys.exit(0)


if __name__ == '__main__':
  main()

