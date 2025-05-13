from os import path

current = path.abspath(__file__)
parent = path.dirname(current)

# Avoid using the default cache location (e.g., ~/.cache),
# ensuring that models are not deleted unexpectedly, reducing re-download time.
cache_directory = parent

del path, current, parent
