from pathlib import Path


def check_valid_dirs(dirs: list) -> list:
    """Return directories that actually exist on the system, otherwise return
    empty list"""
    valid_dirs = []
    for dir in dirs:
        print("\nVerifying directory...")

        # Instantiate the Path class
        dir_path = Path(dir)

        # Check if path exists
        dir_exists = dir_path.exists()

        if not dir_exists:
            print(
                f"""
                    The default directory '{dir}' does not appear to
                    exist on this system."""
            )
        else:
            valid_dirs.append(dir)

    return valid_dirs


def delete_files(files: list) -> None:
    for file in files:
        try:
            Path(file).unlink(missing_ok=False)
            print(f"{file} deleted")
        except (PermissionError, FileNotFoundError):
            print(
                f"""{file} not deleted, possibly due to insuffiient file
                permissions or it might not exist: """
            )
            continue
        if not (any(Path(file.parents[0]).iterdir())):  # checks for empty dir
            Path.rmdir(file.parents[0])
