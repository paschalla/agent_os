def wrap_sudo_command(command: str) -> str:
    """
    Wraps a command with the custom gemini-sudo wrapper if it starts with sudo.
    Example: 'sudo apt update' -> 'sudo gemini-sudo apt update'
    """
    if command.startswith("sudo "):
        # Remove the initial 'sudo ' and replace with wrapper
        inner_cmd = command[5:]
        return f"sudo gemini-sudo {inner_cmd}"
    return command
