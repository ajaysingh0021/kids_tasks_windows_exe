# kids_tasks_windows_exe
This is a local Windows Exe file which can be run without internet also on windows PC.

Step-by-Step Guide to Create Your Windows App
This guide will walk you through turning the Python script into a single executable file (.exe) that you can run on any modern Windows computer, even if it doesn't have Python installed.

Step 1: Install Python
If you don't already have Python installed, you'll need to install it first.

Go to the official Python website: python.org/downloads/

Download the latest version for Windows.

Run the installer. Important: On the first screen of the installer, make sure to check the box that says "Add Python to PATH". This will make the next steps much easier.

Step 2: Save the To-Do App Code
Open a text editor like Notepad.

Copy the entire Python code from the document above.

Paste it into the text editor.

Save the file as app.py on your Desktop or in another folder you can easily find.

Step 3: Install the PyInstaller Package
PyInstaller is a tool that reads your Python script and bundles it with all its necessary files into a single executable.

Open the Windows Command Prompt. You can find it by searching for "cmd" in the Start Menu.

In the command prompt, type the following command and press Enter:

pip install pyinstaller

Step 4: Create the .exe File
This is the final step where PyInstaller does its magic.

In the same Command Prompt window, you need to navigate to the folder where you saved your app.py file. For example, if you saved it on your Desktop, you would type:

cd Desktop

Once you are in the correct directory, run the following command. This tells PyInstaller to create a single, windowed application file.

pyinstaller --onefile --windowed app.py

--onefile: This bundles everything into a single .exe file.

--windowed: This prevents a console/command prompt window from appearing in the background when you run your app.

Wait for the process to complete. You will see a lot of text in the command prompt. When it's finished, you will see a message like "Building EXE from EXE-00.toc completed successfully."

Step 5: Run Your New App!
In the same folder where you saved app.py, you will now see a new folder named dist.

Open the dist folder. Inside, you will find app.exe.

You can double-click this file to run your To-Do list application. You can also move this .exe file to any other location on your computer, and it will still work.

When you run it, the app will create a tasks.txt file in the same directory to save your to-do items.
