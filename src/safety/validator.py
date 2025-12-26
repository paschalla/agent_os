import re
from typing import Tuple, Optional

class CommandValidator:
    """
    Validates commands against safety tiers.
    """
    
    # Safe commands (Read-only) - Tier 1
    TIER_1_SAFE = {
        'ls', 'pwd', 'whoami', 'echo', 'cat', 'grep', 
        'head', 'tail', 'tree', 'find', 'git status', 
        'git log', 'git diff'
    }

    # Write commands (Create/Edit) - Tier 2
    TIER_2_WRITE = {
        'touch', 'mkdir', 'cp', 'mv', 'rm', 
        'git add', 'git commit', 'pip install',
        'python', 'python3'
    }

    # High Risk (Requires explicit approval) - Tier 3
    # Note: 'sudo' is handled separately
    TIER_3_RISK = {
        'mkfs', 'dd', 'reboot', 'shutdown', 
        'chmod', 'chown', 'wget', 'curl', 'ssh'
    }

    @staticmethod
    def validate(command: str) -> Tuple[bool, str, Optional[str]]:
        """
        Analyzes a command string.
        Returns: (is_safe, reason, tier_name)
        """
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return False, "Empty command", None

        base_cmd = cmd_parts[0]

        # 1. Check for Sudo
        if base_cmd == 'sudo':
            return False, "Sudo commands require manual review.", "TIER_3_SUDO"
            
        # 2. Check for dangerous flags
        if base_cmd == 'rm' and ('-rf' in cmd_parts or '-fr' in cmd_parts):
            return False, "Recursive delete (rm -rf) is dangerous.", "TIER_3_HIGH_RISK"

        # 3. Classify based on lists
        if base_cmd in CommandValidator.TIER_1_SAFE:
            return True, "Safe read-only command.", "TIER_1_SAFE"
        
        if base_cmd in CommandValidator.TIER_2_WRITE:
            return True, "Write operation - Requires Confirmation.", "TIER_2_WRITE"
            
        if base_cmd in CommandValidator.TIER_3_RISK:
            return False, "High risk command.", "TIER_3_HIGH_RISK"

        # Default for unknown commands
        return False, f"Unknown command '{base_cmd}'. Proceed with caution.", "UNKNOWN"
