from pathlib import Path
import datetime


def fullpath_parents(fullpath: Path, num_parents: int) -> Path:
    """This is a recursive function to find a directory
    corresponding to the defined number of parents"""

    if not num_parents == 1:
        fullpath = getattr(fullpath, "parent")
        return fullpath_parents(fullpath, num_parents - 1)

    return getattr(fullpath, "parent")


def parent_dirs(basedir: str, num_parents: int, ext: str) -> Path:
    """
    Takes in a directory and returns directories that
    are num_parents upstream of the filetype using glob regression.
    """
    basedir = Path(basedir).absolute()
    file_search = list(basedir.rglob(f"*{ext}"))
    parent_directories = []
    for file in file_search:
        parent_directories.append(fullpath_parents(file, num_parents))
    parent_directories = list(set(parent_directories))  # only grab unique dirs
    return parent_directories


def all_files_exist(files: list) -> bool:
    existing_files = [
        list(f.parents[0].glob(f.name)) for f in files
    ]  # returns empty list of lists if no file
    existing_files = [
        item for sublist in existing_files for item in sublist
    ]  # flatten the list
    return existing_files == files


def any_files_exist(files: list) -> bool:
    existing_files = [
        list(f.parents[0].glob(f.name)) for f in files
    ]  # returns empty list of lists if no file
    existing_files = [
        item for sublist in existing_files for item in sublist
    ]  # flatten the list
    # getting file size
    filesizes = {file: file.stat().st_size for file in existing_files}

    dates_created = [
        datetime.datetime.fromtimestamp(
            fname.stat().st_ctime, tz=datetime.timezone.utc
        )
        for fname in existing_files
    ]
    days_since_creation = [
        int((datetime.datetime.now(datetime.timezone.utc) - date_created).days)
        for date_created in dates_created
    ]

    if any(days <= 3 for days in days_since_creation):
        """Trick system into thinking no files exist if
        files were created in the last few days so that
        partial sequences will get overwritten with full
        sequence
        """
        return False

    return bool(existing_files)
