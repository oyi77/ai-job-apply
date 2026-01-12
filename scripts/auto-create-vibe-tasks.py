#!/usr/bin/env python3
"""
Auto-Create Vibe Kanban Tasks from OpenSpec Proposals

This script automatically creates Vibe Kanban tasks and subtasks from OpenSpec proposals.
It uses the workflow-orchestrator to parse OpenSpec changes and creates tasks via MCP.
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from workflow_orchestrator import WorkflowOrchestrator, OpenSpecChange


class VibeKanbanAutoCreator:
    """Automatically creates Vibe Kanban tasks from OpenSpec proposals."""
    
    def __init__(self, project_id: str, openspec_path: Path = Path("openspec")):
        self.project_id = project_id
        self.orchestrator = WorkflowOrchestrator(openspec_path, project_id)
        self.created_tasks = []
    
    def create_task_from_openspec(self, change: OpenSpecChange, dry_run: bool = False) -> Optional[str]:
        """
        Create a Vibe Kanban task from an OpenSpec change.
        Returns task_id if created successfully.
        """
        proposal = change.read_proposal()
        metadata = self.orchestrator.generate_task_metadata(change)
        description = self.orchestrator.generate_vibe_kanban_task_description(change)
        
        title = metadata.get("title", change.change_id)
        if not title:
            title = change.change_id.replace("-", " ").title()
        
        # Determine status based on OpenSpec status
        status = metadata.get("status", "todo")
        vibe_status = self.map_status(status)
        
        print(f"\n📋 Creating task: {title}")
        print(f"   Change ID: {change.change_id}")
        print(f"   Status: {vibe_status}")
        print(f"   Tasks: {metadata['completed_tasks']}/{metadata['task_count']}")
        
        if dry_run:
            print(f"   [DRY RUN] Would create task with description ({len(description)} chars)")
            return f"dry-run-{change.change_id}"
        
        # Create task via MCP (this would need to be called from the AI assistant)
        # For now, return the data structure needed
        task_data = {
            "project_id": self.project_id,
            "title": title,
            "description": description,
            "status": vibe_status,
            "metadata": {
                "change_id": change.change_id,
                "openspec_path": f"openspec/changes/{change.change_id}",
                "task_count": metadata["task_count"],
                "completed_tasks": metadata["completed_tasks"],
            }
        }
        
        return task_data
    
    def create_subtasks(self, parent_task_id: str, change: OpenSpecChange, dry_run: bool = False) -> List[Dict[str, Any]]:
        """Create subtasks from OpenSpec tasks.md."""
        subtasks = self.orchestrator.generate_subtasks_from_tasks(change)
        
        if not subtasks:
            return []
        
        print(f"\n   Creating {len(subtasks)} subtasks...")
        
        created_subtasks = []
        for i, subtask in enumerate(subtasks, 1):
            title = subtask["title"]
            description = subtask.get("description", "")
            status = subtask.get("status", "todo")
            
            print(f"   {i}. {title[:50]}... ({status})")
            
            if dry_run:
                created_subtasks.append({
                    "title": title,
                    "status": status,
                    "dry_run": True
                })
            else:
                # Note: Vibe Kanban MCP doesn't have direct subtask creation
                # Subtasks would need to be created as separate tasks with parent reference
                # or via a different method
                created_subtasks.append({
                    "parent_task_id": parent_task_id,
                    "title": title,
                    "description": description,
                    "status": status,
                    "metadata": subtask.get("metadata", {})
                })
        
        return created_subtasks
    
    @staticmethod
    def map_status(openspec_status: str) -> str:
        """Map OpenSpec status to Vibe Kanban status."""
        status_map = {
            "done": "done",
            "complete": "done",
            "inprogress": "inprogress",
            "in progress": "inprogress",
            "progress": "inprogress",
            "todo": "todo",
            "pending": "todo",
        }
        return status_map.get(openspec_status.lower(), "todo")
    
    def auto_create_all(self, dry_run: bool = False, filter_change_id: Optional[str] = None) -> Dict[str, Any]:
        """Automatically create Vibe Kanban tasks for all OpenSpec changes."""
        changes = self.orchestrator.discover_changes()
        
        if filter_change_id:
            changes = [c for c in changes if c.change_id == filter_change_id]
        
        print(f"\n🚀 Auto-Creating Vibe Kanban Tasks from OpenSpec")
        print(f"=" * 60)
        print(f"Project ID: {self.project_id}")
        print(f"Found {len(changes)} OpenSpec changes")
        print(f"Dry Run: {dry_run}\n")
        
        results = {
            "project_id": self.project_id,
            "dry_run": dry_run,
            "total_changes": len(changes),
            "created_tasks": [],
            "errors": []
        }
        
        for change in changes:
            try:
                task_data = self.create_task_from_openspec(change, dry_run=dry_run)
                
                if dry_run:
                    subtasks = self.create_subtasks("dry-run-parent", change, dry_run=True)
                    results["created_tasks"].append({
                        "change_id": change.change_id,
                        "title": task_data if isinstance(task_data, str) else task_data.get("title"),
                        "subtasks": len(subtasks),
                        "dry_run": True
                    })
                else:
                    # In real implementation, this would call MCP to create task
                    # For now, we'll generate the command/data needed
                    subtasks = self.create_subtasks(task_data, change, dry_run=False) if isinstance(task_data, dict) else []
                    results["created_tasks"].append({
                        "change_id": change.change_id,
                        "task_data": task_data,
                        "subtasks": subtasks
                    })
                
            except Exception as e:
                error_msg = f"Error creating task for {change.change_id}: {e}"
                print(f"   ❌ {error_msg}")
                results["errors"].append({
                    "change_id": change.change_id,
                    "error": str(e)
                })
        
        return results
    
    def generate_mcp_commands(self, change_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate MCP command structures for creating tasks.
        This returns the data needed to call MCP functions.
        """
        changes = self.orchestrator.discover_changes()
        
        if change_id:
            changes = [c for c in changes if c.change_id == change_id]
        
        commands = []
        
        for change in changes:
            metadata = self.orchestrator.generate_task_metadata(change)
            description = self.orchestrator.generate_vibe_kanban_task_description(change)
            
            title = metadata.get("title", change.change_id.replace("-", " ").title())
            
            # Main task creation command
            command = {
                "function": "mcp_vibe_kanban_create_task",
                "params": {
                    "project_id": self.project_id,
                    "title": title,
                    "description": description
                },
                "metadata": {
                    "change_id": change.change_id,
                    "openspec_path": f"openspec/changes/{change.change_id}",
                    "task_count": metadata["task_count"]
                }
            }
            
            commands.append(command)
            
            # Generate subtask commands (would be called after parent task creation)
            subtasks = self.orchestrator.generate_subtasks_from_tasks(change)
            for subtask in subtasks[:10]:  # Limit to first 10 for now
                subtask_command = {
                    "function": "mcp_vibe_kanban_create_task",
                    "params": {
                        "project_id": self.project_id,
                        "title": subtask["title"],
                        "description": subtask.get("description", "")
                    },
                    "metadata": {
                        "parent_change_id": change.change_id,
                        "is_subtask": True
                    }
                }
                commands.append(subtask_command)
        
        return commands


def main():
    """Main entry point - generates MCP commands for AI assistant."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Auto-create Vibe Kanban tasks from OpenSpec proposals"
    )
    parser.add_argument(
        "--project-id",
        required=True,
        help="Vibe Kanban project ID"
    )
    parser.add_argument(
        "--change-id",
        help="Specific OpenSpec change ID to process (optional)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without actually creating"
    )
    parser.add_argument(
        "--generate-commands",
        action="store_true",
        help="Generate MCP command JSON for AI assistant"
    )
    
    args = parser.parse_args()
    
    creator = VibeKanbanAutoCreator(args.project_id)
    
    if args.generate_commands:
        commands = creator.generate_mcp_commands(args.change_id)
        print(json.dumps(commands, indent=2))
    else:
        results = creator.auto_create_all(dry_run=args.dry_run, filter_change_id=args.change_id)
        
        print(f"\n✅ Summary")
        print(f"=" * 60)
        print(f"Total changes processed: {results['total_changes']}")
        print(f"Tasks created: {len(results['created_tasks'])}")
        print(f"Errors: {len(results['errors'])}")
        
        if results["errors"]:
            print(f"\n❌ Errors:")
            for error in results["errors"]:
                print(f"   - {error['change_id']}: {error['error']}")
        
        if not args.dry_run:
            print(f"\n💡 Note: This script generates task data.")
            print(f"   To actually create tasks, use --generate-commands and call MCP functions.")
            print(f"   Or use the AI assistant with this script's output.")


if __name__ == "__main__":
    main()

