#!/usr/bin/env python3
"""
File Reference System for Claude Logs
Space-efficient file tracking and content management
"""

import json
import os
import hashlib
import gzip
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class FileReferenceSystem:
    """Manages space-efficient file references and content storage"""

    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()
        self.logs_dir = os.path.join(self.project_root, "daily_claude_logs")
        self.refs_dir = os.path.join(self.logs_dir, "file_references")
        self.content_cache_dir = os.path.join(self.refs_dir, "content_cache")

        # Ensure directories exist
        os.makedirs(self.refs_dir, exist_ok=True)
        os.makedirs(self.content_cache_dir, exist_ok=True)

        # Load or create file index
        self.file_index = self._load_file_index()

    def _load_file_index(self) -> Dict:
        """Load or create the file index"""
        index_path = os.path.join(self.refs_dir, "file_index.json")

        if os.path.exists(index_path):
            try:
                with open(index_path, 'r') as f:
                    return json.load(f)
            except:
                pass

        # Create new index
        return {
            "created": datetime.now().isoformat(),
            "files": {},
            "content_hashes": {},
            "stats": {
                "total_files_tracked": 0,
                "total_content_versions": 0,
                "storage_saved_bytes": 0
            }
        }

    def _save_file_index(self):
        """Save the file index"""
        index_path = os.path.join(self.refs_dir, "file_index.json")
        with open(index_path, 'w') as f:
            json.dump(self.file_index, f, indent=2)

    def create_file_reference(self, filepath: str, content: str = None,
                            operation: str = "read") -> Dict:
        """Create or update a file reference with space-efficient storage"""

        abs_path = os.path.abspath(filepath)
        rel_path = os.path.relpath(abs_path, self.project_root)

        # Generate file reference
        file_ref = {
            "path": rel_path,
            "absolute_path": abs_path,
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "exists": os.path.exists(abs_path)
        }

        if os.path.exists(abs_path):
            try:
                stat = os.stat(abs_path)
                file_ref.update({
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "file_hash": self._get_file_hash(abs_path)
                })
            except Exception as e:
                file_ref["error"] = str(e)

        # Handle content if provided
        if content is not None:
            content_ref = self._store_content_efficiently(content, rel_path)
            file_ref.update(content_ref)

        # Update file index
        self._update_file_index(rel_path, file_ref)

        return file_ref

    def _store_content_efficiently(self, content: str, rel_path: str) -> Dict:
        """Store content using deduplication and compression"""

        content_hash = hashlib.sha256(content.encode()).hexdigest()
        content_size = len(content.encode())

        # Check if we already have this content
        if content_hash in self.file_index["content_hashes"]:
            existing_ref = self.file_index["content_hashes"][content_hash]

            # Update stats for storage saved
            self.file_index["stats"]["storage_saved_bytes"] += content_size

            return {
                "content_hash": content_hash,
                "content_size": content_size,
                "content_stored": False,
                "content_reference": existing_ref["cache_file"],
                "deduplication": True,
                "preview": self._create_content_preview(content)
            }

        # Store new content
        cache_filename = f"{content_hash[:16]}.json.gz"
        cache_path = os.path.join(self.content_cache_dir, cache_filename)

        # Create content entry
        content_entry = {
            "hash": content_hash,
            "size": content_size,
            "created": datetime.now().isoformat(),
            "files": [rel_path],  # Track which files use this content
            "content": content
        }

        # Compress and store
        try:
            with gzip.open(cache_path, 'wt', encoding='utf-8') as f:
                json.dump(content_entry, f)

            # Update content hash index
            self.file_index["content_hashes"][content_hash] = {
                "cache_file": cache_filename,
                "size": content_size,
                "created": datetime.now().isoformat(),
                "reference_count": 1
            }

            self.file_index["stats"]["total_content_versions"] += 1

            return {
                "content_hash": content_hash,
                "content_size": content_size,
                "content_stored": True,
                "content_reference": cache_filename,
                "deduplication": False,
                "preview": self._create_content_preview(content)
            }

        except Exception as e:
            return {
                "content_hash": content_hash,
                "content_size": content_size,
                "content_stored": False,
                "error": str(e),
                "preview": self._create_content_preview(content)
            }

    def _create_content_preview(self, content: str) -> Dict:
        """Create a preview of content for quick reference"""
        lines = content.split('\n')
        total_lines = len(lines)

        if total_lines <= 20:
            return {
                "type": "full",
                "lines": lines,
                "total_lines": total_lines
            }
        else:
            return {
                "type": "preview",
                "first_10_lines": lines[:10],
                "last_10_lines": lines[-10:],
                "total_lines": total_lines,
                "truncated_lines": total_lines - 20
            }

    def _update_file_index(self, rel_path: str, file_ref: Dict):
        """Update the file index with new reference"""

        if rel_path not in self.file_index["files"]:
            self.file_index["files"][rel_path] = {
                "first_seen": datetime.now().isoformat(),
                "references": []
            }
            self.file_index["stats"]["total_files_tracked"] += 1

        # Add this reference
        self.file_index["files"][rel_path]["references"].append({
            "timestamp": file_ref["timestamp"],
            "operation": file_ref["operation"],
            "content_hash": file_ref.get("content_hash"),
            "size": file_ref.get("content_size", 0)
        })

        # Keep only last 50 references per file
        refs = self.file_index["files"][rel_path]["references"]
        if len(refs) > 50:
            self.file_index["files"][rel_path]["references"] = refs[-50:]

        # Save updated index
        self._save_file_index()

    def get_file_content(self, content_hash: str) -> Optional[str]:
        """Retrieve file content by hash"""

        if content_hash not in self.file_index["content_hashes"]:
            return None

        cache_info = self.file_index["content_hashes"][content_hash]
        cache_file = cache_info["cache_file"]
        cache_path = os.path.join(self.content_cache_dir, cache_file)

        try:
            with gzip.open(cache_path, 'rt', encoding='utf-8') as f:
                content_entry = json.load(f)
                return content_entry["content"]
        except Exception as e:
            print(f"Error reading cached content: {e}")
            return None

    def get_file_history(self, rel_path: str) -> Optional[Dict]:
        """Get the history of a file"""

        if rel_path not in self.file_index["files"]:
            return None

        file_info = self.file_index["files"][rel_path]

        return {
            "path": rel_path,
            "first_seen": file_info["first_seen"],
            "total_references": len(file_info["references"]),
            "references": file_info["references"]
        }

    def _get_file_hash(self, filepath: str) -> str:
        """Get SHA256 hash of file"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except:
            return "error_reading_file"

    def cleanup_old_content(self, days_old: int = 30):
        """Remove cached content older than specified days"""
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)

        hashes_to_remove = []
        for content_hash, info in self.file_index["content_hashes"].items():
            created = datetime.fromisoformat(info["created"]).timestamp()
            if created < cutoff_date:
                hashes_to_remove.append(content_hash)

        for content_hash in hashes_to_remove:
            self._remove_cached_content(content_hash)

        print(f"Cleaned up {len(hashes_to_remove)} old content entries")

    def _remove_cached_content(self, content_hash: str):
        """Remove cached content entry"""
        if content_hash in self.file_index["content_hashes"]:
            cache_info = self.file_index["content_hashes"][content_hash]
            cache_file = cache_info["cache_file"]
            cache_path = os.path.join(self.content_cache_dir, cache_file)

            try:
                os.remove(cache_path)
            except:
                pass

            del self.file_index["content_hashes"][content_hash]

    def get_storage_stats(self) -> Dict:
        """Get storage efficiency statistics"""
        total_cache_size = 0
        cache_files = 0

        try:
            for filename in os.listdir(self.content_cache_dir):
                if filename.endswith('.json.gz'):
                    filepath = os.path.join(self.content_cache_dir, filename)
                    total_cache_size += os.path.getsize(filepath)
                    cache_files += 1
        except:
            pass

        stats = self.file_index["stats"].copy()
        stats.update({
            "cache_directory_size_bytes": total_cache_size,
            "cache_files_count": cache_files,
            "unique_content_hashes": len(self.file_index["content_hashes"]),
            "storage_efficiency_percent": round(
                (stats["storage_saved_bytes"] / max(1, stats["storage_saved_bytes"] + total_cache_size)) * 100, 2
            )
        })

        return stats