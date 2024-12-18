# basic_coding_template
This is just a template method to follow for all new project files.

When starting a new project always run the command:
python -m venv .venv

This creates a virtual enviornment which can then be activated using:
.venv/Scripts/activate

Then run the requirements.txt file can be installed using pip

## Primary files needed

1. requirments.txt: This will contain all the required libraries to be downloaded using pip (Assuming pip is already installed).
2. .gitignore: Must have file to avoid virtual envs and env variables (which are secret) from being exposed publically.
3. .pylintrc: For code correction through pylint, but having personal control over what is being checked by pylint.
4. main.py: This should be the only file that is being run in a project.
5. LICENSE: For copyright reasons and stuff, imp for large production style projects.

## Folders

1. services: Most methods and functions will be written here
2. controllers: Can have api endpoints and final outputs only
3. config: Wil have db controls and connection handling (A basic config handler is attached)
