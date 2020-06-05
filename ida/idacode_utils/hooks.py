import os

script_folder = ""
getcwd_original = os.getcwd

def getcwd_hook():
    global script_folder

    cwd = getcwd_original()
    if cwd.lower() in script_folder.lower() and script_folder.lower() != cwd.lower():
        cwd = script_folder
    return cwd

def set_script_folder(folder):
    global script_folder

    script_folder = folder

def install():
    os.getcwd = getcwd_hook