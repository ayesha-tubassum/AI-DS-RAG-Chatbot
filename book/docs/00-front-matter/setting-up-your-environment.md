---
id: setting-up-your-environment
title: Setting Up Your Environment
sidebar_position: 5
---

# Setting Up Your Environment

Before writing Python code, you need two things on your computer:

1. Python itself
2. A code editor

This chapter explains how to install both on Windows.

## Installing Python

Python is free to download. Follow these steps:

1. Open your web browser and go to the official Python download page.
2. Download the latest Python 3.12 installer for Windows.
3. Run the installer.
4. On the first screen, make sure the box for **Add Python to PATH** is checked.
5. Click **Install Now** and wait for the installation to finish.

To check that Python is installed correctly, open a terminal window and type:

```bash
python --version
```

You should see a version number, such as `Python 3.12.x`. If you see an error, check that Python was installed and that the **Add Python to PATH** option was selected.

## Installing VS Code

VS Code is a free editor that makes writing and running code easier.

1. Open your web browser and go to the VS Code download page.
2. Download the installer for Windows.
3. Run the installer and follow the steps.
4. When asked, keep the recommended default settings.

## Running Your First Program

Now let us run a simple program.

1. Open VS Code.
2. Create a new file and name it `hello.py`.
3. Type the following line:

```python
print("Hello")
```

4. Save the file.
5. Right-click anywhere in the file and choose **Run Python File in Terminal**, or open a terminal in VS Code and type:

```bash
python hello.py
```

6. You should see this output:

```text
Hello
```

Congratulations. You have installed Python and VS Code, and you have run your first program.

## What to Do If Something Goes Wrong

- If the terminal does not recognise `python`, reopen the terminal after installing Python. Sometimes a restart is needed.
- If VS Code asks to install extensions, you can allow it. The Python extension provides helpful features, but the basic steps above do not require it.
- Double-check that you downloaded Python from the official page.
