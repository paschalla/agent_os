import os
import glob
from typing import Dict, Any

class FileTool:
    """
    File system operations.
    """
    
    def read_file(self, file_path: str) -> str:
        try:
            expanded_path = os.path.expanduser(file_path)
            if not os.path.exists(expanded_path):
                return f"Error: File '{expanded_path}' does not exist."
            with open(expanded_path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def write_file(self, file_path: str, content: str) -> str:
        try:
            expanded_path = os.path.expanduser(file_path)
            parent_dir = os.path.dirname(expanded_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
            
            with open(expanded_path, 'w') as f:
                f.write(content)
            return f"Successfully wrote to {expanded_path}"
        except Exception as e:
            return f"Error writing file: {e}"
            
    def list_dir(self, path: str = ".") -> str:
        try:
            expanded_path = os.path.expanduser(path)
            if not os.path.exists(expanded_path):
                 return f"Error: Directory '{expanded_path}' does not exist."
            
            files = []
            for item in os.listdir(expanded_path):
                full_path = os.path.join(expanded_path, item)
                kind = "DIR" if os.path.isdir(full_path) else "FILE"
                files.append(f"[{kind}] {item}")
            return "\n".join(files) if files else "(Empty directory)"
        except Exception as e:
            return f"Error listing directory: {e}"
            
    def find_files(self, pattern: str, path: str = ".") -> str:
        try:
            expanded_path = os.path.expanduser(path)
            search_pattern = os.path.join(expanded_path, "**", pattern)
            matches = glob.glob(search_pattern, recursive=True)
            
            if not matches:
                return f"No files found matching '{pattern}' in '{path}'"
            
            results = []
            for m in matches[:50]:
                try:
                    rel = os.path.relpath(m, expanded_path)
                    results.append(rel)
                except:
                    results.append(m)
            
            output = "\n".join(results)
            if len(matches) > 50:
                output += f"\n... (and {len(matches) - 50} more)"
            return output
        except Exception as e:
            return f"Error finding files: {e}"
