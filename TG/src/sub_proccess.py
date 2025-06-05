import os


def clean_up():
    directory = os.path.join('TG', 'Data', 'Downloads')
    items = os.listdir(directory)
    for item in items:
        os.remove(os.path.join(directory, item))