## rotor-control-gui

# feat: Create GUI for radio rotor control

This commit introduces a new Python application, `rotor_control_gui.py`, that provides a graphical user interface for controlling a radio rotor using `hamlib`.

The application allows the user to:
- Configure and save settings for the `rotctld` server (e.g., hamlib path, COM port, rotor model).
- Start and stop the `rotctld` server process from the GUI.
- Set and get the rotor's azimuth and elevation.
- View logs from the `rotctld` and `rotctl` commands.
