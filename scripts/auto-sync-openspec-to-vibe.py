#!/usr/bin/env python3
"""
Automatically sync OpenSpec proposals to Vibe Kanban tasks.

This script is designed to be used by the AI assistant to automatically create
Vibe Kanban tasks from OpenSpec proposals using MCP functions.
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from workflow_orchestrator import WorkflowOrchestrator, OpenSpecChange


def get_task_description(change: OpenSpecChange, orchestrator: WorkflowOrchestrator) -> str:
    """Generate full task description for Vibe Kanban."""
    return orchestrator.generate_vibe_kanban_task_description(change)


def get_task_title(change: OpenSpecChange, orchestrator: WorkflowOrchestrator) -> str:
    """Get task title from OpenSpec proposal."""
    metadata = orchestrator.generate_task_metadata(change)
    title = metadata.get("title", "")
    if not title:
        # Fallback: convert change_id to title
        title = change.change_id.replace("-", " ").replace("_", " ").title()
    return title


def create_vibe_task_for_openspec(change_id: str, project_id: str) -> dict:
    """
    Generate the data needed to create a Vibe Kanban task for an OpenSpec change.
    Returns a dict with title, description, and metadata.
    """
    orchestrator = WorkflowOrchestrator(project_id=project_id)
    changes = orchestrator.discover_changes()
    
    change = next((c for c in changes if c.change_id == change_id), None)
    if not change:
        raise ValueError(f"OpenSpec change '{change_id}' not found")
    
    title = get_task_title(change, orchestrator)
    description = get_task_description(change, orchestrator)
    metadata = orchestrator.generate_task_metadata(change)
    
    return {
        "project_id": project_id,
        "title": title,
        "description": description,
        "metadata": metadata
    }


def get_all_openspec_changes(project_id: str) -> list:
    """Get all OpenSpec changes that need Vibe Kanban tasks."""
    orchestrator = WorkflowOrchestrator(project_id=project_id)
    changes = orchestrator.discover_changes()
    
    result = []
    for change in changes:
        metadata = orchestrator.generate_task_metadata(change)
        result.append({
            "change_id": change.change_id,
            "title": metadata.get("title", change.change_id),
            "status": metadata.get("status", "todo"),
            "task_count": metadata.get("task_count", 0),
            "has_design": metadata.get("has_design", False),
        })
    
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync OpenSpec to Vibe Kanban")
    parser.add_argument("--project-id", required=True, help="Vibe Kanban project ID")
    parser.add_argument("--change-id", help="Specific change ID to process")
    parser.add_argument("--list", action="store_true", help="List all OpenSpec changes")
    
    args = parser.parse_args()
    
    if args.list:
        changes = get_all_openspec_changes(args.project_id)
        print(f"\n📋 OpenSpec Changes ({len(changes)} found):\n")
        for change in changes:
            print(f"  • {change['change_id']}")
            print(f"    Title: {change['title']}")
            print(f"    Status: {change['status']}")
            print(f"    Tasks: {change['task_count']}")
            print()
    elif args.change_id:
        task_data = create_vibe_task_for_openspec(args.change_id, args.project_id)
        print(f"\n📋 Task Data for '{args.change_id}':\n")
        print(f"Title: {task_data['title']}")
        print(f"\nDescription ({len(task_data['description'])} chars):")
        print(task_data['description'][:500] + "..." if len(task_data['description']) > 500 else task_data['description'])
    else:
        print("Use --list to see all changes or --change-id <id> to get task data")

