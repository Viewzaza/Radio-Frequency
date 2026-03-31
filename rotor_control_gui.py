import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import subprocess
try:
    from serial.tools import list_ports
except ImportError:
    list_ports = None
import threading
import time
import json
import os
import math

class Compass(tk.Canvas):
    """A tkinter canvas widget that displays a compass face and a pointer for azimuth."""
    def __init__(self, parent, size=200, *args, **kwargs):
        super().__init__(parent, width=size, height=size, *args, **kwargs)
        self.size = size
        self.center = size / 2
        self.radius = size / 2 * 0.9  # Use 90% of radius for the main circle
        self.pointer = None
        self.configure(bg='white')
        self._draw_static_elements()
        self.update_azimuth(0) # Initialize pointer at North

    def _draw_static_elements(self):
        # Draw outer circle
        self.create_oval(
            self.center - self.radius, self.center - self.radius,
            self.center + self.radius, self.center + self.radius,
            outline='gray', width=2
        )
        # Draw tick marks and labels
        for angle in range(0, 360, 30):
            angle_rad = math.radians(angle)
            x1 = self.center + self.radius * math.sin(angle_rad)
            y1 = self.center - self.radius * math.cos(angle_rad)
            if angle % 90 == 0:
                tick_len = 10
                # Draw N, E, S, W labels
                if angle == 0: label = "N"
                elif angle == 90: label = "E"
                elif angle == 180: label = "S"
                else: label = "W"
                x_text = self.center + (self.radius + 15) * math.sin(angle_rad)
                y_text = self.center - (self.radius + 20) * math.cos(angle_rad)
                self.create_text(x_text, y_text, text=label, font=("Arial", 16, "bold"))
            else:
                tick_len = 7

            x2 = self.center + (self.radius - tick_len) * math.sin(angle_rad)
            y2 = self.center - (self.radius - tick_len) * math.cos(angle_rad)
            self.create_line(x1, y1, x2, y2, fill='gray', width=2)

    def update_azimuth(self, angle):
        """Updates the compass pointer to the given angle (in degrees)."""
        if self.pointer:
            self.delete(self.pointer)

        # Angle needs to be converted to radians for trig functions
        angle_rad = math.radians(angle)

        x_end = self.center + self.radius * 0.9 * math.sin(angle_rad)
        y_end = self.center - self.radius * 0.9 * math.cos(angle_rad)

        # Draw the pointer as a red line with an arrow
        self.pointer = self.create_line(
            self.center, self.center, x_end, y_end,
            arrow=tk.LAST, fill='red', width=3
        )

class ElevationIndicator(tk.Canvas):
    """A tkinter canvas widget that displays a 180-degree arc for elevation."""
    def __init__(self, parent, size=200, *args, **kwargs):
        super().__init__(parent, width=size, height=size/2 + 25, *args, **kwargs)
        self.size = size
        self.center_x = size / 2
        self.center_y = size / 2
        self.radius = size / 2 * 0.9
        self.pointer = None
        self.configure(bg='white')
        self._draw_static_elements()
        self.update_elevation(0)

    def _draw_static_elements(self):
        # Draw the 180-degree arc
        self.create_arc(
            self.center_x - self.radius, self.center_y - self.radius,
            self.center_x + self.radius, self.center_y + self.radius,
            start=0, extent=180, style=tk.ARC, outline='gray', width=2
        )
        # Draw tick marks and labels for 0, 90, 180
        for angle in range(0, 181, 45):
            angle_rad = math.radians(180 - angle) # 0 is on the right
            x1 = self.center_x + self.radius * math.cos(angle_rad)
            y1 = self.center_y - self.radius * math.sin(angle_rad)

            if angle % 90 == 0:
                tick_len = 10
                x_text = self.center_x + (self.radius + 18) * math.cos(angle_rad)
                y_text = self.center_y - (self.radius + 18) * math.sin(angle_rad)
                self.create_text(x_text, y_text, text=str(angle), font=("Arial", 12))
            else:
                tick_len = 7

            x2 = self.center_x + (self.radius - tick_len) * math.cos(angle_rad)
            y2 = self.center_y - (self.radius - tick_len) * math.sin(angle_rad)
            self.create_line(x1, y1, x2, y2, fill='gray', width=2)

    def update_elevation(self, angle):
        """Updates the indicator to the given elevation angle."""
        if self.pointer:
            self.delete(self.pointer)

        # Clamp angle between 0 and 180
        angle = max(0, min(180, angle))

        angle_rad = math.radians(180 - angle) # Convert to radians, 0 on right

        x_end = self.center_x + self.radius * 0.95 * math.cos(angle_rad)
        y_end = self.center_y - self.radius * 0.95 * math.sin(angle_rad)

        self.pointer = self.create_line(
            self.center_x, self.center_y, x_end, y_end,
            arrow=tk.LAST, fill='blue', width=3
        )

class RotorControlGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Rotor Control")
        self.geometry("950x800")

        self.rotctld_process = None
        self.config_file = "rotor_config.json"
        self.config = self.load_config()

        # State variables for reconnection logic
        self.server_running_manually = False # Tracks if user intended the server to be running
        self.rotor_connected = False
        self.after_id_server_monitor = None
        self.after_id_rotor_monitor = None

        self.auto_reconnect_var = tk.BooleanVar(value=True)
        self.live_updates_var = tk.BooleanVar(value=True)

        self.create_widgets()
        self.find_hamlib_path() # Find hamlib on startup
        self.update_com_ports() # Populate COM ports on startup
        self.start_monitoring()

    def update_com_ports(self):
        if list_ports is None:
            self.log("pyserial not installed, cannot list COM ports.")
            return

        self.log("Scanning for available COM ports...")
        ports = [port.device for port in list_ports.comports()]
        self.com_port_combo['values'] = ports
        if ports:
            # If current value is not in list, set it to the first available port
            if self.com_port_var.get() not in ports:
                self.com_port_var.set(ports[0])
            self.log(f"Found ports: {', '.join(ports)}")
        else:
            self.log("No COM ports found.")

    def find_hamlib_path(self):
        path = self.hamlib_path_var.get()
        if os.path.exists(os.path.join(path, "rotctld.exe")):
            self.log(f"Hamlib found at configured path: {path}")
            return

        self.log("Hamlib not found in configured path. Searching common locations...")
        search_paths = [
            "C:\\Program Files\\hamlib-w64-4.6.3\\bin",
            "C:\\Program Files\\hamlib\\bin",
            "C:\\Program Files (x86)\\hamlib\\bin"
        ]
        for path in search_paths:
            if os.path.exists(os.path.join(path, "rotctld.exe")):
                self.log(f"Hamlib found at: {path}")
                self.hamlib_path_var.set(path)
                self.save_config()
                return

        self.log("Hamlib not found automatically.")
        if messagebox.askyesno("Hamlib Not Found", "Could not automatically locate the Hamlib 'bin' directory. Would you like to browse for it manually?"):
            self.browse_hamlib_path()
        else:
            self.log("Manual search for Hamlib canceled by user.")
            self.start_server_button.config(state="disabled")


    def browse_hamlib_path(self):
        path = filedialog.askdirectory(title="Please select the Hamlib 'bin' directory")
        if path:
            if os.path.exists(os.path.join(path, "rotctld.exe")):
                self.hamlib_path_var.set(path)
                self.save_config()
                self.log(f"Hamlib path set to: {path}")
                self.start_server_button.config(state="normal")
            else:
                messagebox.showerror("Invalid Directory", f"The selected directory is not a valid Hamlib 'bin' directory. 'rotctld.exe' not found in {path}")
                self.start_server_button.config(state="disabled")

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    # Return if file is not empty
                    content = f.read()
                    if content:
                        return json.loads(content)
            except (json.JSONDecodeError, FileNotFoundError):
                # If file is corrupt or other error, fall through to return defaults.
                # Do not log here, as the logger may not be initialized yet.
                pass

        return {
            "hamlib_path": "C:\\Program Files\\hamlib-w64-4.6.3\\bin",
            "rotor_model": "901",
            "com_port": "COM6",
            "baud_rate": "600",
            "host": "127.0.0.1",
            "port": "4533"
        }

    def save_config(self):
        self.config["hamlib_path"] = self.hamlib_path_var.get()
        self.config["rotor_model"] = self.rotor_model_var.get()
        self.config["com_port"] = self.com_port_var.get()
        self.config["baud_rate"] = self.baud_rate_var.get()
        self.config["host"] = self.host_var.get()
        self.config["port"] = self.port_var.get()
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def create_widgets(self):
        # This is a complete rewrite of the widget creation to improve the layout.

        # Main layout frames
        main_frame = ttk.Frame(self)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Configure grid layout for main_frame
        main_frame.columnconfigure(0, weight=1) # Left frame column
        main_frame.columnconfigure(1, weight=1) # Right frame column
        main_frame.rowconfigure(0, weight=1)

        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew")

        # --- Left Frame Content (Controls) ---
        left_frame.rowconfigure(2, weight=1) # Make logs frame expand

        # Frame for rotctld settings
        settings_frame = ttk.LabelFrame(left_frame, text="Server Settings")
        settings_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        settings_frame.columnconfigure(1, weight=1)

        self.hamlib_path_var = tk.StringVar(value=self.config.get("hamlib_path"))
        self.rotor_model_var = tk.StringVar(value=self.config.get("rotor_model"))
        self.com_port_var = tk.StringVar(value=self.config.get("com_port"))
        self.baud_rate_var = tk.StringVar(value=self.config.get("baud_rate"))
        self.host_var = tk.StringVar(value=self.config.get("host"))
        self.port_var = tk.StringVar(value=self.config.get("port"))

        ttk.Label(settings_frame, text="Hamlib Path:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        path_frame = ttk.Frame(settings_frame)
        path_frame.grid(row=0, column=1, columnspan=2, padx=5, pady=2, sticky="ew")
        ttk.Entry(path_frame, textvariable=self.hamlib_path_var).pack(side="left", fill="x", expand=True)
        ttk.Button(path_frame, text="...", command=self.browse_hamlib_path, width=3).pack(side="left", padx=(5,0))

        ttk.Label(settings_frame, text="Rotor Model:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(settings_frame, textvariable=self.rotor_model_var).grid(row=1, column=1, columnspan=2, padx=5, pady=2, sticky="ew")

        ttk.Label(settings_frame, text="COM Port:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        com_frame = ttk.Frame(settings_frame)
        com_frame.grid(row=2, column=1, columnspan=2, padx=5, pady=2, sticky="ew")
        self.com_port_combo = ttk.Combobox(com_frame, textvariable=self.com_port_var, state='readonly')
        self.com_port_combo.pack(side="left", fill="x", expand=True)
        ttk.Button(com_frame, text="Refresh", command=self.update_com_ports, width=8).pack(side="left", padx=(5,0))

        ttk.Label(settings_frame, text="Baud Rate:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(settings_frame, textvariable=self.baud_rate_var).grid(row=3, column=1, columnspan=2, padx=5, pady=2, sticky="ew")

        server_button_frame = ttk.Frame(settings_frame)
        server_button_frame.grid(row=6, column=0, columnspan=3, pady=5)
        self.start_server_button = ttk.Button(server_button_frame, text="Start Server", command=self.start_rotctld)
        self.start_server_button.pack(side="left", padx=5)
        self.stop_server_button = ttk.Button(server_button_frame, text="Stop Server", command=self.stop_rotctld, state="disabled")
        self.stop_server_button.pack(side="left", padx=5)

        ttk.Checkbutton(settings_frame, text="Attempt to auto-reconnect server", variable=self.auto_reconnect_var).grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Frame for rotor control
        control_frame = ttk.LabelFrame(left_frame, text="Manual Control")
        control_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        control_frame.columnconfigure(1, weight=1)

        self.azimuth_var = tk.StringVar(value="0")
        self.elevation_var = tk.StringVar(value="0")

        ttk.Label(control_frame, text="Azimuth:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(control_frame, textvariable=self.azimuth_var).grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        ttk.Label(control_frame, text="Elevation:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(control_frame, textvariable=self.elevation_var).grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        control_button_frame = ttk.Frame(control_frame)
        control_button_frame.grid(row=2, column=0, columnspan=2, pady=5)
        self.set_position_button = ttk.Button(control_button_frame, text="Set Position", command=self.set_position, state="disabled")
        self.set_position_button.pack(side="left", padx=5)
        self.get_position_button = ttk.Button(control_button_frame, text="Get Position", command=self.get_position, state="disabled")
        self.get_position_button.pack(side="left", padx=5)

        ttk.Checkbutton(control_frame, text="Live GUI Updates", variable=self.live_updates_var).grid(row=4, column=0, columnspan=3, pady=5, sticky="w")

        self.manual_cmd_var = tk.StringVar()
        ttk.Label(control_frame, text="Manual Cmd:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        cmd_entry = ttk.Entry(control_frame, textvariable=self.manual_cmd_var)
        cmd_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")
        cmd_entry.bind("<Return>", self.send_manual_command)
        send_button = ttk.Button(control_frame, text="Send", command=self.send_manual_command, width=8)
        send_button.grid(row=3, column=2, padx=5, pady=2)

        # Frame for status and logs
        status_frame = ttk.LabelFrame(left_frame, text="Status & Logs")
        status_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        status_frame.rowconfigure(2, weight=1)
        status_frame.columnconfigure(0, weight=1)

        self.server_status_var = tk.StringVar(value="Server Status: Stopped")
        self.rotor_conn_status_var = tk.StringVar(value="Rotor Connection: Disconnected")
        self.current_position_var = tk.StringVar(value="Current Position: N/A")

        ttk.Label(status_frame, textvariable=self.server_status_var).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(status_frame, textvariable=self.rotor_conn_status_var).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(status_frame, textvariable=self.current_position_var).grid(row=2, column=0, sticky="w", padx=5, pady=2)

        self.log_area = scrolledtext.ScrolledText(status_frame, wrap=tk.WORD, height=10)
        self.log_area.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)

        # --- Right Frame Content (Visuals) ---
        right_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)
        visuals_frame = ttk.LabelFrame(right_frame, text="Visual Display")
        visuals_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        visuals_frame.rowconfigure(1, weight=1) # Azimuth row
        visuals_frame.rowconfigure(3, weight=1) # Elevation row
        visuals_frame.columnconfigure(0, weight=1)

        ttk.Label(visuals_frame, text="Azimuth", font=("Arial", 14)).grid(row=0, column=0, pady=(5,0))
        self.compass = Compass(visuals_frame, size=300)
        self.compass.grid(row=1, column=0, pady=5, sticky="nsew")

        ttk.Label(visuals_frame, text="Elevation", font=("Arial", 14)).grid(row=2, column=0, pady=(15,0))
        self.elevation_indicator = ElevationIndicator(visuals_frame, size=250)
        self.elevation_indicator.grid(row=3, column=0, pady=5, sticky="nsew")

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def start_rotctld(self, from_user=True):
        if from_user:
            self.server_running_manually = True
            self.save_config()

        hamlib_path = self.hamlib_path_var.get()
        rotctld_exe = os.path.join(hamlib_path, "rotctld.exe")

        if not os.path.exists(rotctld_exe):
            messagebox.showerror("Error", f"rotctld.exe not found at {rotctld_exe}")
            return False

        command = [
            rotctld_exe, "-m", self.rotor_model_var.get(), "-r", self.com_port_var.get(),
            "-s", self.baud_rate_var.get(), "-T", self.host_var.get(), "-t", self.port_var.get(), "-vvvv"
        ]

        try:
            self.log(f"Starting server: {' '.join(command)}")
            self.rotctld_process = subprocess.Popen(
                command, cwd=hamlib_path, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )

            self.server_status_var.set("Server Status: Running")
            self.start_server_button.config(state="disabled")
            self.stop_server_button.config(state="normal")
            self.set_position_button.config(state="normal")
            self.get_position_button.config(state="normal")

            threading.Thread(target=self.read_process_output, args=(self.rotctld_process.stdout,), daemon=True).start()
            threading.Thread(target=self.read_process_output, args=(self.rotctld_process.stderr,), daemon=True).start()
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start rotctld: {e}")
            self.log(f"Error starting server: {e}")
            return False

    def read_process_output(self, pipe):
        for line in iter(pipe.readline, ''):
            self.log(line.strip())
        pipe.close()

    def stop_rotctld(self, from_user=True):
        if from_user:
            self.server_running_manually = False

        if self.rotctld_process:
            self.log("Stopping server...")
            self.rotctld_process.terminate()
            try:
                self.rotctld_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.log("Server did not terminate, killing it.")
                self.rotctld_process.kill()
            self.rotctld_process = None
            self.log("Server stopped.")

        self.server_status_var.set("Server Status: Stopped")
        self.rotor_conn_status_var.set("Rotor Connection: Disconnected")
        self.current_position_var.set("Current Position: N/A")
        if hasattr(self, 'compass'): self.compass.update_azimuth(0)
        if hasattr(self, 'elevation_indicator'): self.elevation_indicator.update_elevation(0)
        self.rotor_connected = False
        self.start_server_button.config(state="normal")
        self.stop_server_button.config(state="disabled")
        self.set_position_button.config(state="disabled")
        self.get_position_button.config(state="disabled")

    def run_rotctl_command(self, command_args):
        hamlib_path = self.hamlib_path_var.get()
        rotctl_exe = os.path.join(hamlib_path, "rotctl.exe")

        if not os.path.exists(rotctl_exe):
            self.log(f"Error: rotctl.exe not found at {rotctl_exe}")
            return None, "rotctl.exe not found"

        command = [rotctl_exe, "-m", "2", "-r", f"{self.host_var.get()}:{self.port_var.get()}"] + command_args

        try:
            result = subprocess.run(
                command, cwd=hamlib_path, capture_output=True, text=True, timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                return result.stdout.strip(), None
            else:
                # Log without showing command to keep logs cleaner
                self.log(f"rotctl command failed: {result.stderr.strip()}")
                return None, result.stderr.strip()
        except Exception as e:
            self.log(f"Exception running rotctl: {e}")
            return None, str(e)

    def set_position(self):
        if not self.rotor_connected:
            messagebox.showwarning("Warning", "Rotor not connected. Cannot set position.")
            return

        azimuth = self.azimuth_var.get()
        elevation = self.elevation_var.get()

        self.log(f"Setting position to Azimuth={azimuth}, Elevation={elevation}")
        stdout, stderr = self.run_rotctl_command(["P", azimuth, elevation])

        if stderr:
            self.log(f"Error setting position: {stderr}")
            messagebox.showerror("Error", f"Failed to set position: {stderr}")
            self.rotor_connected = False
            self.rotor_conn_status_var.set("Rotor Connection: Error")
        else:
            self.log(f"Position set command sent successfully.")
            # Optimistically update position, monitor loop will verify
            self.after(1000, self.check_rotor_connection)

    def get_position(self):
        # This is now just a user-facing action
        if not self.server_running_manually:
            messagebox.showwarning("Warning", "Server is not running.")
            return
        self.log("Manual position check requested.")
        self.check_rotor_connection()

    def send_manual_command(self, event=None):
        if not self.rotor_connected:
            messagebox.showwarning("Warning", "Rotor not connected. Cannot send command.")
            return

        command_str = self.manual_cmd_var.get()
        if not command_str:
            return

        command_args = command_str.split()
        self.log(f"MANUAL CMD: {command_str}")

        stdout, stderr = self.run_rotctl_command(command_args)

        if stdout:
            self.log(f"OUTPUT: {stdout}")
        if stderr:
            self.log(f"ERROR: {stderr}")

        # After sending a command, it's good practice to check the position again
        # to update the state and visuals.
        self.after(500, self.check_rotor_connection)
        self.manual_cmd_var.set("") # Clear the entry

    def check_rotor_connection(self):
        # This is the core connection check function
        stdout, stderr = self.run_rotctl_command(["p"])

        if stderr:
            if self.rotor_connected:
                self.log("Rotor connection lost.")
            self.rotor_connected = False
            self.rotor_conn_status_var.set("Rotor Connection: Disconnected / Error")
            self.current_position_var.set("Current Position: N/A")
            return False
        else:
            if not self.rotor_connected:
                self.log("Rotor connection established.")
            self.rotor_connected = True
            self.rotor_conn_status_var.set("Rotor Connection: Connected")
            lines = stdout.split('\n')
            az = lines[0] if lines else "0.0"
            el = lines[1] if len(lines) > 1 else "0.0"
            self.current_position_var.set(f"Current Position: Azimuth={az}, Elevation={el}")

            try:
                az_float = float(az)
                el_float = float(el)
                self.compass.update_azimuth(az_float)
                self.elevation_indicator.update_elevation(el_float)
            except (ValueError, TypeError):
                pass # Ignore if values are not valid floats

            return True

    def start_monitoring(self):
        self.monitor_server_process()
        self.monitor_rotor_connection()

    def monitor_server_process(self):
        if self.after_id_server_monitor:
            self.after_cancel(self.after_id_server_monitor)

        is_running = self.rotctld_process and self.rotctld_process.poll() is None

        if self.server_running_manually and not is_running and self.auto_reconnect_var.get():
            self.log("Server process terminated unexpectedly. Attempting to restart...")
            self.stop_rotctld(from_user=False) # Clean up first
            self.start_rotctld(from_user=False)

        # Update GUI status
        if is_running:
            self.server_status_var.set("Server Status: Running")
        else:
            self.server_status_var.set("Server Status: Stopped")

        self.after_id_server_monitor = self.after(3000, self.monitor_server_process)

    def monitor_rotor_connection(self):
        if self.after_id_rotor_monitor:
            self.after_cancel(self.after_id_rotor_monitor)

        is_server_running = self.rotctld_process and self.rotctld_process.poll() is None

        if is_server_running:
            if self.live_updates_var.get():
                if not self.rotor_connected and self.auto_reconnect_var.get():
                    self.rotor_conn_status_var.set("Rotor Connection: Attempting to connect...")
                self.check_rotor_connection()
        else:
            self.rotor_connected = False
            self.rotor_conn_status_var.set("Rotor Connection: Disconnected")
            self.current_position_var.set("Current Position: N/A")

        self.after_id_rotor_monitor = self.after(5000, self.monitor_rotor_connection)

    def on_closing(self):
        self.save_config()
        if self.rotctld_process and self.rotctld_process.poll() is None:
            if messagebox.askokcancel("Quit", "The rotctld server is running. Do you want to stop it and quit?"):
                self.stop_rotctld()
                self.destroy()
        else:
            self.destroy()

if __name__ == "__main__":
    app = RotorControlGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
