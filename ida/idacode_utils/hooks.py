import os

script_folder = ""
getcwd_original = os.getcwd

def getcwd_hook():
    # NOTE: We return the script folder here, otherwise breakpoints fail in VSCode
    if script_folder:
        return script_folder
    return getcwd_original()

def set_script_folder(folder):
    global script_folder

    script_folder = folder

def install():
    os.getcwd = getcwd_hook
