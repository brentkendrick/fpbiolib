# import subprocess

# base version number
__version__ = "0.0.1"


# # Get git commit as string to append to version
# def get_git_revision_short_hash():
#     return (
#         subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
#         .decode("ascii")
#         .strip()
#     )


# # append git commit if possible
# try:
#     commit = get_git_revision_short_hash()
#     __version__ += "-" + commit
# except subprocess.CalledProcessError:
#     pass
