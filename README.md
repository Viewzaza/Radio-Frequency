# rotor-control-gui


## This commit introduces a new Python application, `rotor_control_gui.py`, that provides a graphical user interface for controlling a radio rotor using `hamlib`.

The application allows the user to:
- Configure and save settings for the `rotctld` server (e.g., hamlib path, COM port, rotor model).
- Start and stop the `rotctld` server process from the GUI.
- Set and get the rotor's azimuth and elevation.
- View logs from the `rotctld` and `rotctl` commands.

Visual Indicators:
- A 2D compass widget now displays the rotor's current azimuth.
- A 180-degree arc widget displays the current elevation.
- These visuals provide an intuitive, at-a-glance view of the rotor's orientation.

Hamlib Auto-Detection:
- The application now automatically searches for the `hamlib` installation in common directories on startup.
- If not found, it prompts the user with a file dialog to locate the `hamlib\bin` directory manually.
- A "Browse" button has been added to the settings for changing the path at any time.

Visual Enhancements:
- The Azimuth compass and Elevation indicator widgets have been significantly enlarged to improve readability.
- Font sizes within the visual widgets have been increased.
- The main window geometry has been adjusted to better accommodate the larger visuals.

Manual Command Prompt:
- A new "Manual Command" section has been added to the GUI.
- This allows users to send any raw command string (e.g., "S", "M 180 30") directly to `rotctl` for advanced control.
- Command output and errors are logged directly to the status area.
