"""
SHERPA V1 - Autonomous Runner
Two-agent system with knowledge injection and auto-continue
"""

import asyncio
import json
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

from sherpa.core.db import Database
from sherpa.core.snippet_manager import SnippetManager
from sherpa.core.harness.agent_client import create_agent_client, CLAUDE_SDK_AVAILABLE
from sherpa.core.harness.prompts import (
    get_initializer_prompt,
    get_coding_prompt,
    inject_knowledge_into_prompt,
    copy_spec_to_project
)


# Configuration
AUTO_CONTINUE_DELAY_SECONDS = 3
DEFAULT_MODEL = "claude-sonnet-4.5"


async def run_agent_session(
    client: object,
    message: str,
    session_id: str,
    db: Database,
    iteration: int
) -> tuple[str, str]:
    """
    Run a single agent session using Claude Agent SDK.

    Args:
        client: Claude SDK client
        message: The prompt to send
        session_id: Session ID for tracking
        db: Database instance
        iteration: Current iteration number

    Returns:
        (status, response_text) where status is:
        - "continue" if agent should continue working
        - "error" if an error occurred
    """
    print(f"[Session {iteration}] Sending prompt to Claude Agent SDK...\n")

    # Log session start
    await db.add_log(
        session_id,
        'info',
        f'Agent iteration {iteration} started',
        json.dumps({'iteration': iteration})
    )

    try:
        # Send the query
        await client.query(message)

        # Collect response text and show tool use
        response_text = ""
        async for msg in client.receive_response():
            msg_type = type(msg).__name__

            # Handle AssistantMessage (text and tool use)
            if msg_type == "AssistantMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    block_type = type(block).__name__

                    if block_type == "TextBlock" and hasattr(block, "text"):
                        response_text += block.text
                        print(block.text, end="", flush=True)
                    elif block_type == "ToolUseBlock" and hasattr(block, "name"):
                        print(f"\n[Tool: {block.name}]", flush=True)

            # Handle UserMessage (tool results)
            elif msg_type == "UserMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    block_type = type(block).__name__

                    if block_type == "ToolResultBlock":
                        result_content = getattr(block, "content", "")
                        is_error = getattr(block, "is_error", False)

                        if "blocked" in str(result_content).lower():
                            print(f"   [BLOCKED] {result_content}", flush=True)
                        elif is_error:
                            error_str = str(result_content)[:500]
                            print(f"   [Error] {error_str}", flush=True)
                        else:
                            print("   [Done]", flush=True)

        print("\n" + "-" * 70 + "\n")

        # Log session completion
        await db.add_log(
            session_id,
            'info',
            f'Agent iteration {iteration} completed',
            json.dumps({'iteration': iteration, 'response_length': len(response_text)})
        )

        return "continue", response_text

    except Exception as e:
        print(f"Error during agent session: {e}")

        # Log error
        await db.add_log(
            session_id,
            'error',
            f'Agent iteration {iteration} failed: {str(e)}',
            json.dumps({'iteration': iteration, 'error': str(e)})
        )

        return "error", str(e)


async def get_relevant_snippets(
    snippet_manager: SnippetManager,
    spec_content: str,
    max_snippets: int = 5
) -> List[Dict]:
    """
    Get relevant code snippets based on the specification.

    Args:
        snippet_manager: Snippet manager instance
        spec_content: Content of the specification
        max_snippets: Maximum number of snippets to return

    Returns:
        List of relevant snippets
    """
    try:
        # Extract keywords from spec for querying
        # For now, use simple keyword extraction
        # In production, this would use AI to extract relevant topics

        keywords = []
        spec_lower = spec_content.lower()

        # Check for common patterns
        if 'api' in spec_lower or 'rest' in spec_lower:
            keywords.append('api rest')
        if 'authentication' in spec_lower or 'auth' in spec_lower:
            keywords.append('security auth')
        if 'react' in spec_lower or 'frontend' in spec_lower:
            keywords.append('react hooks')
        if 'async' in spec_lower or 'await' in spec_lower:
            keywords.append('python async')
        if 'error' in spec_lower or 'exception' in spec_lower:
            keywords.append('python error-handling')
        if 'test' in spec_lower:
            keywords.append('testing unit')
        if 'git' in spec_lower or 'commit' in spec_lower:
            keywords.append('git commits')

        # Get snippets for each keyword
        all_snippets = []
        for keyword in keywords[:3]:  # Limit to top 3 topics
            snippets = await snippet_manager.search_snippets(keyword, limit=2)
            all_snippets.extend(snippets)

        # Return unique snippets (limit to max_snippets)
        seen_ids = set()
        unique_snippets = []
        for snippet in all_snippets:
            snippet_id = snippet.get('id')
            if snippet_id and snippet_id not in seen_ids:
                seen_ids.add(snippet_id)
                unique_snippets.append(snippet)
                if len(unique_snippets) >= max_snippets:
                    break

        return unique_snippets

    except Exception as e:
        print(f"Warning: Failed to get relevant snippets: {e}")
        return []


async def run_autonomous_harness(
    session_id: str,
    spec_content: str,
    project_dir: Path,
    db: Database,
    max_iterations: Optional[int] = None,
    enable_knowledge_injection: bool = True
) -> None:
    """
    Run the autonomous agent loop with two-agent system.

    Args:
        session_id: Session ID for tracking
        spec_content: Content of the specification file
        project_dir: Directory for the project (will be created)
        db: Database instance
        max_iterations: Maximum number of iterations (None for unlimited)
        enable_knowledge_injection: Whether to inject knowledge snippets
    """
    if not CLAUDE_SDK_AVAILABLE:
        print("\n[Error] Claude Code SDK not available.")
        print("This is expected in the test environment.")
        print("In production, install with: pip install claude-code-sdk")
        await db.update_session(session_id, {'status': 'error'})
        await db.add_log(
            session_id,
            'error',
            'Claude Code SDK not available',
            json.dumps({'sdk_available': False})
        )
        return

    print("\n" + "=" * 70)
    print("  SHERPA V1 - AUTONOMOUS CODING HARNESS")
    print("=" * 70)
    print(f"\nSession ID: {session_id}")
    print(f"Project directory: {project_dir}")
    print(f"Model: {DEFAULT_MODEL}")
    print(f"Knowledge injection: {enable_knowledge_injection}")
    if max_iterations:
        print(f"Max iterations: {max_iterations}")
    else:
        print("Max iterations: Unlimited")
    print()

    # Create project directory
    project_dir.mkdir(parents=True, exist_ok=True)

    # Copy spec to project directory
    copy_spec_to_project(project_dir, spec_content)

    # Check if this is a fresh start or continuation
    tests_file = project_dir / "feature_list.json"
    is_first_run = not tests_file.exists()

    # Initialize snippet manager for knowledge injection
    snippet_manager = None
    if enable_knowledge_injection:
        snippet_manager = SnippetManager()
        await snippet_manager.initialize()

    # Get relevant snippets for knowledge injection
    relevant_snippets = []
    if snippet_manager and enable_knowledge_injection:
        print("[Knowledge] Retrieving relevant code snippets...")
        relevant_snippets = await get_relevant_snippets(
            snippet_manager,
            spec_content,
            max_snippets=5
        )
        print(f"[Knowledge] Found {len(relevant_snippets)} relevant snippets\n")

        # Log knowledge injection
        await db.add_log(
            session_id,
            'info',
            f'Knowledge injection enabled - {len(relevant_snippets)} snippets loaded',
            json.dumps({
                'snippets': [s.get('title', 'Unknown') for s in relevant_snippets]
            })
        )

    if is_first_run:
        print("=" * 70)
        print("  INITIALIZER AGENT - GENERATING FEATURE LIST")
        print("=" * 70)
        print("\n[Note] This may take 10-20 minutes to generate comprehensive tests.")
        print("[Note] The agent will create 100+ detailed test cases.")
        print()

        await db.update_session(session_id, {'status': 'initializing'})
    else:
        print(f"Continuing existing project from {project_dir}")

        # Update session status
        await db.update_session(session_id, {'status': 'active'})

    # Main loop
    iteration = 0

    while True:
        iteration += 1

        # Check max iterations
        if max_iterations and iteration > max_iterations:
            print(f"\n[Complete] Reached max iterations ({max_iterations})")
            await db.update_session(session_id, {'status': 'stopped'})
            await db.add_log(
                session_id,
                'info',
                f'Session stopped - reached max iterations ({max_iterations})',
                json.dumps({'iteration': iteration})
            )
            break

        # Print session header
        print("\n" + "=" * 70)
        if is_first_run:
            print(f"  INITIALIZER AGENT - ITERATION {iteration}")
        else:
            print(f"  CODING AGENT - ITERATION {iteration}")
        print("=" * 70 + "\n")

        # Create client (fresh context)
        try:
            # Choose prompt based on session type
            if is_first_run:
                base_prompt = get_initializer_prompt()
                agent_type = 'initializer'
            else:
                base_prompt = get_coding_prompt()
                agent_type = 'coding'

            # Inject knowledge into prompt if enabled
            if enable_knowledge_injection and relevant_snippets:
                prompt = inject_knowledge_into_prompt(base_prompt, relevant_snippets)
                print(f"[Knowledge] Injected {len(relevant_snippets)} snippets into prompt\n")
            else:
                prompt = base_prompt

            # Create fresh client with knowledge-enhanced prompt
            client = create_agent_client(
                project_dir=project_dir,
                model=DEFAULT_MODEL,
                system_prompt=prompt
            )

            if client is None:
                raise Exception("Failed to create agent client")

        except Exception as e:
            print(f"\n[Error] Failed to create agent client: {e}")
            await db.update_session(session_id, {'status': 'error'})
            await db.add_log(
                session_id,
                'error',
                f'Failed to create agent client: {str(e)}',
                json.dumps({'iteration': iteration, 'error': str(e)})
            )
            break

        # Run session with async context manager
        async with client:
            status, response = await run_agent_session(
                client,
                prompt,
                session_id,
                db,
                iteration
            )

        # After first iteration, switch to coding agent
        if is_first_run:
            is_first_run = False
            print("\n[Success] Initializer agent completed")
            print("[Next] Coding agents will continue...")
            await db.update_session(session_id, {'status': 'active'})

        # Handle status
        if status == "continue":
            print(f"\n[Auto-continue] Next iteration in {AUTO_CONTINUE_DELAY_SECONDS}s...")
            await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

        elif status == "error":
            print("\n[Error] Session encountered an error")
            print("[Retry] Will retry with a fresh session...")
            await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

        # Small delay between sessions
        if max_iterations is None or iteration < max_iterations:
            print("\n[Preparing] Next session starting...\n")
            await asyncio.sleep(1)

    # Final summary
    print("\n" + "=" * 70)
    print("  SESSION COMPLETE")
    print("=" * 70)
    print(f"\nSession ID: {session_id}")
    print(f"Project directory: {project_dir}")
    print(f"Total iterations: {iteration}")

    # Update final session status
    await db.update_session(session_id, {'status': 'completed'})
    await db.add_log(
        session_id,
        'info',
        f'Session completed after {iteration} iterations',
        json.dumps({'total_iterations': iteration})
    )

    print("\n[Complete] Autonomous harness session finished!")
