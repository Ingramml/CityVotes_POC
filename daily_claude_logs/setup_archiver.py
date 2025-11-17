#!/usr/bin/env python3
"""
Auto-Setup Script for Claude Session Archiver
Creates the archiver system in any new project directory
"""

import os
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path


class ArchiverSetup:
    """Handles automatic setup of Claude Session Archiver in new projects"""

    def __init__(self):
        self.archiver_files = [
            "session_capture.py",
            "daily_summarizer.py",
            "file_reference_system.py",
            "learning_insights_tracker.py",
            "weekly_review_generator.py",
            "claude_session_archiver.py",
            "setup_archiver.py"
        ]

    def setup_in_project(self, project_root: str, source_archiver_path: str = None) -> bool:
        """
        Set up the archiver system in a new project

        Args:
            project_root: Target project directory
            source_archiver_path: Path to existing archiver implementation

        Returns:
            bool: Success status
        """
        try:
            project_root = os.path.abspath(project_root)

            # Create logs directory structure
            logs_dir = os.path.join(project_root, "daily_claude_logs")

            directories = [
                "raw_conversations",
                "daily_summaries",
                "daily_transcripts",
                "learning_insights",
                "weekly_reviews",
                "file_references",
                "file_references/content_cache"
            ]

            for dir_name in directories:
                dir_path = os.path.join(logs_dir, dir_name)
                os.makedirs(dir_path, exist_ok=True)

            # Copy archiver files if source provided
            if source_archiver_path and os.path.exists(source_archiver_path):
                for filename in self.archiver_files:
                    source_file = os.path.join(source_archiver_path, filename)
                    target_file = os.path.join(logs_dir, filename)

                    if os.path.exists(source_file):
                        shutil.copy2(source_file, target_file)

            # Create configuration file
            config = {
                "setup_date": datetime.now().isoformat(),
                "project_root": project_root,
                "archiver_version": "1.0",
                "auto_capture": True,
                "auto_daily_summary": True,
                "storage_optimization": True,
                "retention_days": 365
            }

            config_path = os.path.join(logs_dir, "archiver_config.json")
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)

            # Create setup marker
            setup_marker = {
                "setup_completed": True,
                "setup_date": datetime.now().isoformat(),
                "setup_version": "1.0",
                "directories_created": directories,
                "files_copied": len([f for f in self.archiver_files if os.path.exists(os.path.join(logs_dir, f))])
            }

            marker_path = os.path.join(logs_dir, "setup_complete.json")
            with open(marker_path, 'w') as f:
                json.dump(setup_marker, f, indent=2)

            # Create README for the archiver
            self._create_archiver_readme(logs_dir)

            return True

        except Exception as e:
            print(f"Error setting up archiver: {e}")
            return False

    def _create_archiver_readme(self, logs_dir: str):
        """Create README file explaining the archiver system"""
        readme_content = """# Claude Session Archiver

This directory contains the Claude Session Archiver system for tracking and analyzing AI interactions.

## Structure

- `raw_conversations/` - Raw session data in JSON format
- `daily_summaries/` - Daily summaries of activities and accomplishments
- `daily_transcripts/` - Human-readable daily reports
- `learning_insights/` - Analysis of learning patterns and AI behavior
- `weekly_reviews/` - Weekly aggregated analysis and trends
- `file_references/` - Space-efficient file tracking system

## Usage

### Basic Usage
```python
from claude_session_archiver import ClaudeSessionArchiver

# Initialize archiver
archiver = ClaudeSessionArchiver()

# Start session
archiver.start_session()

# Capture interactions
archiver.capture_interaction(
    prompt="Your prompt here",
    response="Claude's response",
    files_accessed=["file1.py", "file2.txt"]
)

# Generate daily summary
archiver.generate_daily_summary()
```

### Command Line Usage
```bash
# Initialize in new project
python claude_session_archiver.py --init

# Generate daily summary
python claude_session_archiver.py --daily-summary

# Generate weekly review
python claude_session_archiver.py --weekly-review

# Show statistics
python claude_session_archiver.py --stats

# Cleanup old data (30+ days)
python claude_session_archiver.py --cleanup 30
```

### Quick Functions
```python
# Quick capture
from claude_session_archiver import quick_capture
quick_capture("prompt", "response", ["file.py"])

# Quick daily report
from claude_session_archiver import generate_daily_report
generate_daily_report()

# Quick weekly report
from claude_session_archiver import generate_weekly_report
generate_weekly_report()
```

## Features

- **Session Capture**: Records all prompts, responses, and tool usage
- **File References**: Space-efficient file tracking with deduplication
- **Daily Summaries**: Automated analysis of daily activities
- **Learning Insights**: Tracks AI behavior patterns and learning progression
- **Weekly Reviews**: Comprehensive weekly trend analysis
- **Storage Optimization**: Compressed storage with content deduplication
- **Export/Import**: Full data export capabilities

## Configuration

Edit `archiver_config.json` to customize:
- Auto-capture settings
- Retention policies
- Storage optimization
- Analysis preferences

## Maintenance

- Run cleanup periodically: `python claude_session_archiver.py --cleanup 30`
- Export data before major changes: `python claude_session_archiver.py --export /backup/path`
- Check stats regularly: `python claude_session_archiver.py --stats`

Generated by Claude Session Archiver Setup v1.0
"""

        readme_path = os.path.join(logs_dir, "README.md")
        with open(readme_path, 'w') as f:
            f.write(readme_content)

    def check_project_compatibility(self, project_root: str) -> Dict:
        """Check if project is suitable for archiver setup"""
        project_root = os.path.abspath(project_root)

        compatibility = {
            "compatible": True,
            "issues": [],
            "recommendations": []
        }

        # Check if directory exists and is writable
        if not os.path.exists(project_root):
            compatibility["compatible"] = False
            compatibility["issues"].append("Project directory does not exist")
            return compatibility

        if not os.access(project_root, os.W_OK):
            compatibility["compatible"] = False
            compatibility["issues"].append("Project directory is not writable")

        # Check if archiver already exists
        logs_dir = os.path.join(project_root, "daily_claude_logs")
        if os.path.exists(logs_dir):
            compatibility["issues"].append("Archiver directory already exists")
            compatibility["recommendations"].append("Use existing archiver or remove daily_claude_logs directory first")

        # Check available space (warn if < 100MB)
        try:
            statvfs = os.statvfs(project_root)
            free_space = statvfs.f_frsize * statvfs.f_bavail
            if free_space < 100 * 1024 * 1024:  # 100MB
                compatibility["recommendations"].append("Low disk space - consider cleanup")
        except:
            pass

        # Check for Python environment
        if not sys.executable:
            compatibility["recommendations"].append("Python environment not detected")

        return compatibility

    def create_global_archiver(self, base_path: str = None) -> bool:
        """Create a global archiver that can be used across projects"""
        if base_path is None:
            base_path = os.path.expanduser("~/.claude_global_archiver")

        try:
            # Set up global archiver
            success = self.setup_in_project(base_path)

            if success:
                # Create symbolic link script for easy access
                link_script = os.path.join(base_path, "link_to_project.py")
                self._create_link_script(link_script)

            return success

        except Exception as e:
            print(f"Error creating global archiver: {e}")
            return False

    def _create_link_script(self, script_path: str):
        """Create script to link global archiver to projects"""
        script_content = '''#!/usr/bin/env python3
"""
Link Global Claude Archiver to Project
Creates symbolic links to use global archiver in any project
"""

import os
import sys
import argparse

def link_to_project(project_path, global_archiver_path=None):
    """Create symbolic link to global archiver in project"""
    if global_archiver_path is None:
        global_archiver_path = os.path.dirname(os.path.abspath(__file__))

    project_logs = os.path.join(project_path, "daily_claude_logs")

    if os.path.exists(project_logs):
        print(f"Archiver already exists in {project_path}")
        return False

    try:
        os.symlink(global_archiver_path, project_logs)
        print(f"Linked global archiver to {project_path}")
        return True
    except Exception as e:
        print(f"Error linking archiver: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project_path", help="Path to project directory")
    args = parser.parse_args()

    link_to_project(args.project_path)
'''

        with open(script_path, 'w') as f:
            f.write(script_content)

        # Make executable
        os.chmod(script_path, 0o755)

    def auto_detect_and_setup(self, search_path: str = ".") -> List[str]:
        """Auto-detect project directories and offer to set up archiver"""
        project_indicators = [
            "package.json",
            "requirements.txt",
            "Cargo.toml",
            "go.mod",
            "pom.xml",
            ".git",
            "README.md"
        ]

        potential_projects = []

        for root, dirs, files in os.walk(search_path):
            # Skip hidden directories and already setup projects
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'daily_claude_logs']

            if any(indicator in files or indicator in dirs for indicator in project_indicators):
                if not os.path.exists(os.path.join(root, "daily_claude_logs")):
                    potential_projects.append(root)

        return potential_projects

    def interactive_setup(self):
        """Interactive setup wizard"""
        print("🔧 Claude Session Archiver Setup Wizard")
        print("=" * 40)

        # Ask for setup type
        print("\nSetup options:")
        print("1. Setup in current directory")
        print("2. Setup in specific directory")
        print("3. Create global archiver")
        print("4. Auto-detect and setup multiple projects")

        try:
            choice = input("\nEnter choice (1-4): ").strip()

            if choice == "1":
                success = self.setup_in_project(".")
                if success:
                    print("✅ Archiver setup completed in current directory")
                else:
                    print("❌ Setup failed")

            elif choice == "2":
                path = input("Enter project directory path: ").strip()
                if os.path.exists(path):
                    success = self.setup_in_project(path)
                    if success:
                        print(f"✅ Archiver setup completed in {path}")
                    else:
                        print("❌ Setup failed")
                else:
                    print("❌ Directory does not exist")

            elif choice == "3":
                success = self.create_global_archiver()
                if success:
                    print("✅ Global archiver created in ~/.claude_global_archiver")
                else:
                    print("❌ Global setup failed")

            elif choice == "4":
                search_path = input("Enter search directory (. for current): ").strip() or "."
                projects = self.auto_detect_and_setup(search_path)

                if projects:
                    print(f"\n📁 Found {len(projects)} potential projects:")
                    for i, project in enumerate(projects, 1):
                        print(f"  {i}. {project}")

                    setup_all = input("\nSetup archiver in all projects? (y/n): ").lower() == 'y'

                    if setup_all:
                        for project in projects:
                            success = self.setup_in_project(project)
                            if success:
                                print(f"✅ Setup completed: {project}")
                            else:
                                print(f"❌ Setup failed: {project}")
                else:
                    print("No suitable projects found")

            else:
                print("Invalid choice")

        except KeyboardInterrupt:
            print("\n\nSetup cancelled")
        except Exception as e:
            print(f"\n❌ Error during setup: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Claude Session Archiver Setup")
    parser.add_argument("--interactive", action="store_true", help="Run interactive setup wizard")
    parser.add_argument("--project", metavar="PATH", help="Setup in specific project directory")
    parser.add_argument("--global", action="store_true", help="Create global archiver")
    parser.add_argument("--auto-detect", metavar="PATH", help="Auto-detect projects in PATH and setup")
    parser.add_argument("--check", metavar="PATH", help="Check project compatibility")
    parser.add_argument("--source", metavar="PATH", help="Source archiver path for copying files")

    args = parser.parse_args()

    setup = ArchiverSetup()

    if args.interactive:
        setup.interactive_setup()

    elif args.project:
        success = setup.setup_in_project(args.project, args.source)
        if success:
            print(f"✅ Archiver setup completed in {args.project}")
        else:
            print("❌ Setup failed")

    elif getattr(args, 'global'):
        success = setup.create_global_archiver()
        if success:
            print("✅ Global archiver created")
        else:
            print("❌ Global setup failed")

    elif args.auto_detect:
        projects = setup.auto_detect_and_setup(args.auto_detect)
        print(f"Found {len(projects)} potential projects")
        for project in projects:
            print(f"  - {project}")

    elif args.check:
        compatibility = setup.check_project_compatibility(args.check)
        print(f"Project compatibility: {'✅ Compatible' if compatibility['compatible'] else '❌ Issues found'}")

        if compatibility['issues']:
            print("Issues:")
            for issue in compatibility['issues']:
                print(f"  - {issue}")

        if compatibility['recommendations']:
            print("Recommendations:")
            for rec in compatibility['recommendations']:
                print(f"  - {rec}")

    else:
        parser.print_help()