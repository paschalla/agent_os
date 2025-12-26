import subprocess
import logging
from typing import Dict, Any, Optional
from ..safety.validator import CommandValidator
from ..safety.sudo import wrap_sudo_command

logger = logging.getLogger(__name__)

class ShellTool:
    """
    Executes shell commands with safety validation.
    """
    
    def __init__(self):
        self.validator = CommandValidator()

    def run(self, command: str) -> Dict[str, Any]:
        """
        Runs a shell command if allowed.
        """
        # Validate
        is_safe, reason, tier = self.validator.validate(command)
        
        if not is_safe:
            logger.warning(f"Blocked command: {command} ({reason})")
            return {
                "success": False, 
                "output": f"Security Block: {reason} (Tier: {tier})",
                "tier": tier
            }

        # Apply Sudo Wrapper if needed
        final_cmd = wrap_sudo_command(command)
        
        try:
            # Execute
            result = subprocess.run(
                final_cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=60
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\nStderr: {result.stderr}"
                
            return {
                "success": result.returncode == 0,
                "output": output.strip() or "(No output)",
                "tier": tier
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "Command timed out.", "tier": tier}
        except Exception as e:
            return {"success": False, "output": f"Execution error: {e}", "tier": tier}
