from .shell import ShellTool
from .fs import FileTool

class ToolRegistry:
    def __init__(self):
        self.shell = ShellTool()
        self.fs = FileTool()
        
        self.tools = {
            "run_command": self.shell.run,
            "read_file": self.fs.read_file,
            "write_file": self.fs.write_file,
            "list_dir": self.fs.list_dir,
            "find_files": self.fs.find_files
        }

    def get_tool(self, name: str):
        return self.tools.get(name)
    
    def get_tool_names(self):
        return list(self.tools.keys())
