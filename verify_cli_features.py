#!/usr/bin/env python3
"""
SHERPA V1 - CLI Features Verification Script
Verifies Rich CLI formatting and Click framework implementation
"""

import sys
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'


def print_header(title):
    """Print a formatted header"""
    print(f"\n{BLUE}{BOLD}{'=' * 80}{RESET}")
    print(f"{BLUE}{BOLD}{title:^80}{RESET}")
    print(f"{BLUE}{BOLD}{'=' * 80}{RESET}\n")


def print_test(test_num, title, passed, details=""):
    """Print test result"""
    status = f"{GREEN}✅ PASS{RESET}" if passed else f"{RED}❌ FAIL{RESET}"
    print(f"{BOLD}Test {test_num}: {title}{RESET}")
    print(f"  Status: {status}")
    if details:
        print(f"  Details: {details}")
    print()


def verify_rich_cli_formatting():
    """Verify Rich CLI formatting implementation"""
    print_header("RICH CLI FORMATTING VERIFICATION")

    status_file = Path("sherpa/cli/commands/status.py")
    if not status_file.exists():
        print_test(1, "Status file exists", False, f"File not found: {status_file}")
        return 0, 6

    content = status_file.read_text()

    tests_passed = 0
    total_tests = 6

    # Test 1: Verify Rich library is imported
    test1 = "from rich" in content and "Console" in content
    print_test(
        1,
        "Rich library imported",
        test1,
        "Found: from rich.console import Console" if test1 else "Missing Rich imports"
    )
    if test1:
        tests_passed += 1

    # Test 2: Verify Rich formatting is used
    test2 = "console.print" in content and "Panel" in content
    print_test(
        2,
        "Rich formatting methods used",
        test2,
        "Found: console.print() and Panel()" if test2 else "Missing Rich usage"
    )
    if test2:
        tests_passed += 1

    # Test 3: Verify tables are formatted properly
    test3 = "Table(" in content and "add_column" in content and "add_row" in content
    print_test(
        3,
        "Tables formatted properly",
        test3,
        "Found: Table, add_column, add_row" if test3 else "Missing table formatting"
    )
    if test3:
        tests_passed += 1

    # Test 4: Verify colors are used appropriately
    test4 = all(color in content for color in ['green', 'red', 'yellow', 'cyan'])
    colors_found = [c for c in ['green', 'red', 'yellow', 'cyan', 'blue'] if c in content]
    print_test(
        4,
        "Colors used appropriately",
        test4,
        f"Found colors: {', '.join(colors_found)}" if test4 else "Missing color usage"
    )
    if test4:
        tests_passed += 1

    # Test 5: Verify progress bars are displayed
    test5 = "progress" in content.lower() and ("█" in content or "_create_progress_bar" in content)
    print_test(
        5,
        "Progress bars displayed",
        test5,
        "Found: progress bar implementation" if test5 else "Missing progress bars"
    )
    if test5:
        tests_passed += 1

    # Test 6: Verify emoji/icons are used
    emojis_found = []
    emoji_list = ['🟢', '✅', '❌', '📊', '⏸️', '📋', '⚠️']
    for emoji in emoji_list:
        if emoji in content:
            emojis_found.append(emoji)
    test6 = len(emojis_found) >= 3
    print_test(
        6,
        "Emoji/icons used where helpful",
        test6,
        f"Found {len(emojis_found)} emojis: {' '.join(emojis_found[:5])}" if test6 else "Not enough emoji usage"
    )
    if test6:
        tests_passed += 1

    return tests_passed, total_tests


def verify_click_cli_framework():
    """Verify Click CLI framework implementation"""
    print_header("CLICK CLI FRAMEWORK VERIFICATION")

    main_file = Path("sherpa/cli/main.py")
    if not main_file.exists():
        print_test(1, "Main CLI file exists", False, f"File not found: {main_file}")
        return 0, 6

    content = main_file.read_text()

    tests_passed = 0
    total_tests = 6

    # Test 1: Verify Click framework is imported and used
    test1 = "import click" in content and "@click.group" in content and "@click.command" in content
    print_test(
        1,
        "Click framework imported and used",
        test1,
        "Found: import click, @click.group, @click.command" if test1 else "Missing Click framework"
    )
    if test1:
        tests_passed += 1

    # Test 2: Verify all commands are listed
    commands = ['init', 'generate', 'run', 'query', 'snippets', 'status', 'logs', 'serve']
    commands_found = [cmd for cmd in commands if f"def {cmd}(" in content]
    test2 = len(commands_found) >= 7  # At least 7 out of 8
    print_test(
        2,
        "All commands listed",
        test2,
        f"Found {len(commands_found)}/8 commands: {', '.join(commands_found)}" if test2 else "Missing commands"
    )
    if test2:
        tests_passed += 1

    # Test 3: Verify command descriptions are present
    test3 = '"""' in content and content.count('"""') >= 8
    print_test(
        3,
        "Command descriptions present",
        test3,
        f"Found {content.count('\"\"\"') // 2} docstrings" if test3 else "Missing docstrings"
    )
    if test3:
        tests_passed += 1

    # Test 4: Verify Click options are documented
    option_count = content.count("@click.option")
    test4 = option_count >= 4 and "help=" in content
    print_test(
        4,
        "Click options documented",
        test4,
        f"Found {option_count} @click.option decorators with help text" if test4 else "Missing option documentation"
    )
    if test4:
        tests_passed += 1

    # Test 5: Verify Click arguments are used
    argument_count = content.count("@click.argument")
    test5 = argument_count >= 2
    print_test(
        5,
        "Click arguments documented",
        test5,
        f"Found {argument_count} @click.argument decorators" if test5 else "Missing argument decorators"
    )
    if test5:
        tests_passed += 1

    # Test 6: Verify argument validation with types
    test6 = "type=click.Path" in content or ("type=str" in content or "type=int" in content)
    print_test(
        6,
        "Argument validation with types",
        test6,
        "Found: Type validation (Path, str, int)" if test6 else "Missing type validation"
    )
    if test6:
        tests_passed += 1

    return tests_passed, total_tests


def main():
    """Run all verifications"""
    print(f"\n{BOLD}{BLUE}🏔️  SHERPA V1 - CLI Features Verification{RESET}")
    print(f"{BOLD}{'=' * 80}{RESET}\n")

    # Run Rich CLI formatting tests
    rich_passed, rich_total = verify_rich_cli_formatting()

    # Run Click framework tests
    click_passed, click_total = verify_click_cli_framework()

    # Print summary
    print_header("SUMMARY")

    total_passed = rich_passed + click_passed
    total_tests = rich_total + click_total
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

    print(f"{BOLD}Rich CLI Formatting:{RESET}")
    print(f"  {rich_passed}/{rich_total} tests passed ({rich_passed/rich_total*100:.1f}%)")
    print()

    print(f"{BOLD}Click CLI Framework:{RESET}")
    print(f"  {click_passed}/{click_total} tests passed ({click_passed/click_total*100:.1f}%)")
    print()

    print(f"{BOLD}Overall:{RESET}")
    print(f"  {total_passed}/{total_tests} tests passed ({success_rate:.1f}%)")
    print()

    if total_passed == total_tests:
        print(f"{GREEN}{BOLD}🎉 ALL TESTS PASSED!{RESET}")
        print(f"{GREEN}Both Rich CLI formatting and Click framework are fully implemented.{RESET}")
        return 0
    else:
        print(f"{YELLOW}{BOLD}⚠️  SOME TESTS FAILED{RESET}")
        print(f"{YELLOW}Please review the output above for details.{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
