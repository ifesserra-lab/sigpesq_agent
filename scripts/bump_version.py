import sys
import re
from pathlib import Path

def bump_version(new_version):
    """
    Updates the version in pyproject.toml.
    Supports both vX.Y.Z and X.Y.Z formats.
    """
    # Remove 'v' prefix if present
    if new_version.startswith('v'):
        new_version = new_version[1:]
        
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("Error: pyproject.toml not found.")
        sys.exit(1)
        
    content = pyproject_path.read_text()
    
    # Regex to find version = "..."
    # We look for version = "..." specifically in the [project] section
    new_content = re.sub(
        r'(version\s*=\s*")([^"]*)(")',
        rf'\g<1>{new_version}\g<3>',
        content,
        count=1
    )
    
    if content == new_content:
        print("Warning: Version not found or already matches.")
    else:
        pyproject_path.write_text(new_content)
        print(f"Successfully updated version to {new_version} in pyproject.toml")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/bump_version.py <new_version>")
        sys.exit(1)
        
    target_version = sys.argv[1]
    bump_version(target_version)
