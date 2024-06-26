import os
import subprocess
import fnmatch
import glob

def get_git_tracked_files():
    try:
        result = subprocess.run(['git', 'ls-files'], capture_output=True, text=True, check=True)
        return set(result.stdout.splitlines())
    except subprocess.CalledProcessError:
        print("Error: Not a git repository or git is not installed.")
        return set()

def is_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file.read()
        return True
    except UnicodeDecodeError:
        return False

def should_ignore(path, ignore_patterns):
    return any(fnmatch.fnmatch(path, pattern) for pattern in ignore_patterns)

def get_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

def generate_tree(repo_path, ignore_patterns):
    ignore_pattern = '|'.join(f"{p}" for p in ignore_patterns if '*' not in p)
    ignore_args = ['-I', ignore_pattern] if ignore_pattern else []
    
    try:
        result = subprocess.run(
            ['tree', '-L', '3', '--charset', 'ascii', '--noreport'] + ignore_args + [repo_path],
            capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        print("Error: 'tree' command failed. Make sure it's installed and accessible.")
        return ""

def generate_markdown(repo_path, output_file, ignore_patterns, include_files):
    git_tracked_files = get_git_tracked_files()
    
    with open(output_file, 'w', encoding='utf-8') as md_file:
        md_file.write(f"# Repository Description\n\n")

        # Generate directory tree
        md_file.write("## Project Structure\n\n```\n")
        md_file.write(generate_tree(repo_path, ignore_patterns))
        md_file.write("```\n\n")

        # Generate file contents for specified files
        md_file.write("## File Contents\n\n")
        for file_pattern in include_files:
            if file_pattern.startswith('./'):
                # Handle specific path patterns
                for file_path in glob.glob(os.path.join(repo_path, file_pattern), recursive=True):
                    process_file(file_path, repo_path, git_tracked_files, ignore_patterns, md_file)
            else:
                # Handle general patterns
                for root, _, files in os.walk(repo_path):
                    for file in fnmatch.filter(files, file_pattern):
                        file_path = os.path.join(root, file)
                        process_file(file_path, repo_path, git_tracked_files, ignore_patterns, md_file)

def process_file(file_path, repo_path, git_tracked_files, ignore_patterns, md_file):
    relative_path = os.path.relpath(file_path, repo_path)
    if relative_path in git_tracked_files and is_text_file(file_path) and not should_ignore(relative_path, ignore_patterns):
        md_file.write(f"### {relative_path}\n\n")
        md_file.write("```" + (os.path.splitext(file_path)[1][1:] or "txt") + "\n")
        md_file.write(get_file_content(file_path))
        md_file.write("\n```\n\n")

if __name__ == "__main__":
    repo_path = "."  # Current directory, change this if needed
    output_file = "repo_description.md"
    ignore_patterns = [
        "*.pyc",
        "__pycache__",
        "*.git*",
        "README.md",
        "venv",
        "*.egg-info",
        "*.log",
        "*.sqlite3",
        "*.md",
        "*.sh",
        "node_modules",
    ]
    include_files = [
        ".vue",
        "*.js",
        "*.html",
        "*.css",
        # "package.json",
        "remote_updater/settings.py",
        "./updater/*.py",  # This specific pattern is now supported alongside general patterns
    ]

    generate_markdown(repo_path, output_file, ignore_patterns, include_files)
    print(f"Repository description generated in {output_file}")