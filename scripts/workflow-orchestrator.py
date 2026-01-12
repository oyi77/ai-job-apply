#!/usr/bin/env python3
"""
Workflow Orchestrator: OpenSpec ↔ Vibe Kanban Integration

This script enforces workflow by:
1. Reading OpenSpec proposals and creating Vibe Kanban tasks
2. Converting OpenSpec tasks.md into Vibe Kanban subtasks
3. Linking design documents
4. Orchestrating task automation
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import sys


class OpenSpecChange:
    """Represents an OpenSpec change proposal."""
    
    def __init__(self, change_id: str, change_path: Path):
        self.change_id = change_id
        self.change_path = change_path
        self.proposal_path = change_path / "proposal.md"
        self.tasks_path = change_path / "tasks.md"
        self.design_path = change_path / "design.md"
        self.status_path = change_path / "STATUS.md"
        
    def exists(self) -> bool:
        """Check if proposal exists."""
        return self.proposal_path.exists()
    
    def read_proposal(self) -> Dict[str, Any]:
        """Read and parse proposal.md."""
        if not self.proposal_path.exists():
            return {}
        
        content = self.proposal_path.read_text()
        
        # Parse proposal structure
        proposal = {
            "title": self.extract_title(content),
            "why": self.extract_section(content, "## Why"),
            "what_changes": self.extract_section(content, "## What Changes"),
            "impact": self.extract_section(content, "## Impact"),
        }
        
        return proposal
    
    def read_tasks(self) -> List[Dict[str, Any]]:
        """Read and parse tasks.md into structured tasks."""
        if not self.tasks_path.exists():
            return []
        
        content = self.tasks_path.read_text()
        tasks = []
        
        # Parse markdown task list format: ## Section, - [ ] task
        current_section = None
        task_id = 0
        
        for line in content.split('\n'):
            # Section header
            if line.startswith('##'):
                current_section = line.replace('##', '').strip()
                continue
            
            # Task item
            if line.strip().startswith('- [ ]') or line.strip().startswith('- [x]'):
                task_text = re.sub(r'^- \[[ x]\]\s*', '', line.strip())
                task_id += 1
                tasks.append({
                    "id": task_id,
                    "section": current_section or "General",
                    "description": task_text,
                    "completed": line.strip().startswith('- [x]'),
                })
        
        return tasks
    
    def read_design(self) -> Optional[str]:
        """Read design.md if it exists."""
        if self.design_path.exists():
            return self.design_path.read_text()
        return None
    
    def has_status(self) -> bool:
        """Check if STATUS.md exists."""
        return self.status_path.exists()
    
    @staticmethod
    def extract_title(content: str) -> str:
        """Extract title from proposal (first # header)."""
        for line in content.split('\n'):
            if line.startswith('# Change:') or line.startswith('# '):
                return line.replace('# Change:', '').replace('#', '').strip()
        return ""
    
    @staticmethod
    def extract_section(content: str, section_header: str) -> str:
        """Extract section content."""
        lines = content.split('\n')
        in_section = False
        section_lines = []
        
        for line in lines:
            if line.startswith(section_header):
                in_section = True
                continue
            if in_section and line.startswith('##') and not line.startswith(section_header):
                break
            if in_section:
                section_lines.append(line)
        
        return '\n'.join(section_lines).strip()


class WorkflowOrchestrator:
    """Orchestrates workflow between OpenSpec and Vibe Kanban."""
    
    def __init__(self, openspec_path: Path = Path("openspec"), project_id: Optional[str] = None):
        self.openspec_path = openspec_path
        self.changes_path = openspec_path / "changes"
        self.project_id = project_id
        self.changes: List[OpenSpecChange] = []
    
    def discover_changes(self) -> List[OpenSpecChange]:
        """Discover all OpenSpec changes."""
        if not self.changes_path.exists():
            return []
        
        changes = []
        for item in self.changes_path.iterdir():
            if item.is_dir() and item.name != "archive":
                change = OpenSpecChange(item.name, item)
                if change.exists():
                    changes.append(change)
        
        self.changes = changes
        return changes
    
    def generate_vibe_kanban_task_description(self, change: OpenSpecChange) -> str:
        """Generate Vibe Kanban task description from OpenSpec proposal."""
        proposal = change.read_proposal()
        tasks = change.read_tasks()
        design = change.read_design()
        
        description_parts = []
        
        # Add proposal summary
        if proposal.get("why"):
            description_parts.append("## Why")
            description_parts.append(proposal["why"])
            description_parts.append("")
        
        if proposal.get("what_changes"):
            description_parts.append("## What Changes")
            description_parts.append(proposal["what_changes"])
            description_parts.append("")
        
        if proposal.get("impact"):
            description_parts.append("## Impact")
            description_parts.append(proposal["impact"])
            description_parts.append("")
        
        # Add design document reference
        if design:
            description_parts.append("## Design Document")
            description_parts.append(f"See: `openspec/changes/{change.change_id}/design.md`")
            description_parts.append("")
        
        # Add tasks summary
        if tasks:
            description_parts.append("## Implementation Tasks")
            description_parts.append(f"Total tasks: {len(tasks)}")
            description_parts.append("")
            description_parts.append("See OpenSpec tasks.md for detailed subtasks:")
            description_parts.append(f"`openspec/changes/{change.change_id}/tasks.md`")
            description_parts.append("")
            
            # Group by section
            sections = {}
            for task in tasks:
                section = task["section"]
                if section not in sections:
                    sections[section] = []
                sections[section].append(task)
            
            for section, section_tasks in sections.items():
                description_parts.append(f"### {section}")
                for task in section_tasks[:5]:  # Show first 5
                    status = "✅" if task["completed"] else "⏳"
                    description_parts.append(f"- {status} {task['description']}")
                if len(section_tasks) > 5:
                    description_parts.append(f"  ... and {len(section_tasks) - 5} more tasks")
                description_parts.append("")
        
        # Add OpenSpec reference
        description_parts.append("---")
        description_parts.append(f"**OpenSpec Change ID**: `{change.change_id}`")
        description_parts.append(f"**Proposal**: `openspec/changes/{change.change_id}/proposal.md`")
        if change.tasks_path.exists():
            description_parts.append(f"**Tasks**: `openspec/changes/{change.change_id}/tasks.md`")
        if design:
            description_parts.append(f"**Design**: `openspec/changes/{change.change_id}/design.md`")
        if change.has_status():
            description_parts.append(f"**Status**: `openspec/changes/{change.change_id}/STATUS.md`")
        
        return "\n".join(description_parts)
    
    def generate_task_metadata(self, change: OpenSpecChange) -> Dict[str, Any]:
        """Generate metadata for Vibe Kanban task."""
        proposal = change.read_proposal()
        tasks = change.read_tasks()
        
        # Determine priority based on change type and status
        priority = "medium"
        if "security" in change.change_id or "critical" in change.change_id.lower():
            priority = "high"
        elif "enhancement" in change.change_id or "nice-to-have" in change.change_id:
            priority = "low"
        
        # Determine status
        status = "todo"
        if change.has_status():
            status_content = change.status_path.read_text()
            if "complete" in status_content.lower() or "100%" in status_content:
                status = "done"
            elif "progress" in status_content.lower() or "in progress" in status_content.lower():
                status = "inprogress"
        
        return {
            "change_id": change.change_id,
            "title": proposal.get("title", change.change_id),
            "priority": priority,
            "status": status,
            "task_count": len(tasks),
            "completed_tasks": sum(1 for t in tasks if t["completed"]),
            "has_design": change.design_path.exists(),
            "openspec_path": f"openspec/changes/{change.change_id}",
        }
    
    def generate_subtasks_from_tasks(self, change: OpenSpecChange) -> List[Dict[str, Any]]:
        """Generate Vibe Kanban subtasks from OpenSpec tasks.md."""
        tasks = change.read_tasks()
        subtasks = []
        
        for task in tasks:
            subtasks.append({
                "title": task["description"],
                "description": f"Section: {task['section']}\nOpenSpec Task ID: {task['id']}",
                "status": "done" if task["completed"] else "todo",
                "metadata": {
                    "section": task["section"],
                    "task_id": task["id"],
                    "change_id": change.change_id,
                }
            })
        
        return subtasks
    
    def generate_workflow_report(self) -> Dict[str, Any]:
        """Generate workflow orchestration report."""
        changes = self.discover_changes()
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_changes": len(changes),
            "changes": [],
        }
        
        for change in changes:
            metadata = self.generate_task_metadata(change)
            report["changes"].append(metadata)
        
        return report
    
    def print_workflow_summary(self):
        """Print workflow summary for manual review."""
        changes = self.discover_changes()
        
        print(f"\n📋 OpenSpec ↔ Vibe Kanban Workflow Orchestration")
        print(f"=" * 60)
        print(f"Found {len(changes)} OpenSpec changes\n")
        
        for change in changes:
            metadata = self.generate_task_metadata(change)
            proposal = change.read_proposal()
            
            print(f"📄 {change.change_id}")
            print(f"   Title: {metadata['title']}")
            print(f"   Status: {metadata['status']}")
            print(f"   Priority: {metadata['priority']}")
            print(f"   Tasks: {metadata['completed_tasks']}/{metadata['task_count']} completed")
            print(f"   Design: {'✅' if metadata['has_design'] else '❌'}")
            print(f"   Path: {metadata['openspec_path']}")
            print()
        
        print(f"\n💡 Next Steps:")
        print(f"   1. Review changes above")
        print(f"   2. Create Vibe Kanban tasks using this script")
        print(f"   3. Use tag templates from workflow-tags.md")
        print(f"   4. Link tasks to OpenSpec proposals")
        print()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenSpec ↔ Vibe Kanban Workflow Orchestrator")
    parser.add_argument("--project-id", help="Vibe Kanban project ID")
    parser.add_argument("--changes-path", default="openspec/changes", help="Path to OpenSpec changes")
    parser.add_argument("--report", action="store_true", help="Generate workflow report")
    parser.add_argument("--summary", action="store_true", help="Print workflow summary")
    
    args = parser.parse_args()
    
    orchestrator = WorkflowOrchestrator(
        openspec_path=Path("openspec"),
        project_id=args.project_id
    )
    
    if args.summary:
        orchestrator.print_workflow_summary()
    elif args.report:
        report = orchestrator.generate_workflow_report()
        print(json.dumps(report, indent=2))
    else:
        orchestrator.print_workflow_summary()


if __name__ == "__main__":
    main()

