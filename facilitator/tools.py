"""
System Tools
------------
Functions exposed to the LLM for file manipulation and command execution.
"""

import os
import subprocess
import platform

# Safety: Restrict operations to the current working directory or subdirectories
BASE_DIR = os.getcwd()

def _is_safe_path(path):
    """
    Ensures the path is within the base directory to prevent directory traversal.
    """
    try:
        # Resolve absolute path
        abs_path = os.path.abspath(os.path.join(BASE_DIR, path))
        return abs_path.startswith(BASE_DIR)
    except Exception:
        return False

def write_file(path, content):
    """
    Writes content to a file.
    
    Args:
        path (str): Relative path to the file.
        content (str): Content to write.
        
    Returns:
        str: Status message.
    """
    if not _is_safe_path(path):
        return f"Error: Path '{path}' is outside the allowed directory."
        
    try:
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to '{path}'."
    except Exception as e:
        return f"Error writing file: {str(e)}"

def read_file(path):
    """
    Reads content from a file.
    
    Args:
        path (str): Relative path to the file.
        
    Returns:
        str: File content or error message.
    """
    if not _is_safe_path(path):
        return f"Error: Path '{path}' is outside the allowed directory."
        
    try:
        if not os.path.exists(path):
            return f"Error: File '{path}' does not exist."
            
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def run_command(command):
    """
    Executes a shell command.
    
    Args:
        command (str): Command to execute.
        
    Returns:
        str: Command output (stdout + stderr).
    """
    # Basic safety check (very primitive, meant for MVP)
    forbidden = ["rm -rf", "format", "del /s /q c:", "sudo"]
    for bad in forbidden:
        if bad in command.lower():
            return f"Error: Command '{command}' contains forbidden patterns."
            
    try:
        # Run command
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30, # Timeout to prevent hanging
            cwd=BASE_DIR
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]\n{result.stderr}"
            
        return output
    except Exception as e:
        return f"Error executing command: {str(e)}"

def list_dir(path="."):
    """
    Lists files in a directory.
    """
    if not _is_safe_path(path):
        return f"Error: Path '{path}' is outside the allowed directory."
        
    try:
        items = os.listdir(path)
        return "\n".join(items)
    except Exception as e:
        return f"Error listing directory: {str(e)}"

# Registry of available tools for internal lookup
TOOL_REGISTRY = {
    "write_file": write_file,
    "read_file": read_file,
    "run_command": run_command,
    "list_dir": list_dir
}
