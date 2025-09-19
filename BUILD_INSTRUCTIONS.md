# How to Build the RotorControl Executable (.exe)

This guide provides the steps to package the `rotor_control_gui.py` script into a standalone Windows executable (`.exe`). This allows you to run the application without needing to have Python installed.

## Step 1: Install PyInstaller

`PyInstaller` is a tool that packages a Python application and all its dependencies into a single package. You only need to install it once.

1.  Open the Windows **Command Prompt** (`cmd`).
2.  Run the following command to install PyInstaller:
    ```bash
    pip install pyinstaller
    ```

## Step 2: Run the Packaging Command

1.  In the Command Prompt, navigate to the directory where you have saved the final `rotor_control_gui.py` file. For example, if it's on your Desktop, you would run:
    ```bash
    cd Desktop
    ```
2.  Once you are in the correct directory, run the following command:
    ```bash
    pyinstaller --onefile --windowed --name="RotorControl" rotor_control_gui.py
    ```

**Command Breakdown:**
*   `--onefile`: Bundles everything into a single `.exe` file.
*   `--windowed`: Prevents the black console window from appearing when you run the GUI.
*   `--name="RotorControl"`: Sets the name of your final executable file to `RotorControl.exe`.

## Step 3: Locate and Run Your Application

After the command finishes, PyInstaller will create a few folders. You will find your new `RotorControl.exe` application inside a folder named **`dist`**.

You can now double-click `RotorControl.exe` to run it. You can also move this file to any other location on your computer, like your Desktop, for easy access.

**Important Note:** This process packages the Python script, but it does **not** package the `hamlib` library itself. You still need to have `hamlib` installed on the computer where you run the `.exe`. The application is designed to help you find the `hamlib` folder if it's not in the default location.
