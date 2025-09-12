# Gpredict Debugging Instructions

We need to see the detailed log output from the `rotctld` server to understand why Gpredict can read data but cannot send commands. The best way to do this is to run the server manually from the command line.

Please follow these steps carefully:

### Step 1: Stop the Server in the GUI

In the **RotorControl application**, make sure you have clicked the **"Stop Server"** button. This is very important to ensure no other `rotctld` process is running in the background.

### Step 2: Open Command Prompt and Navigate to Hamlib

Open the Windows **Command Prompt (cmd)**. You can find this by searching for `cmd` in the Start Menu.

In the command prompt, type the following command and press Enter. This will take you to the correct directory where the `rotctld.exe` program is located.

```bash
cd "C:\Program Files\hamlib-w64-4.6.3\bin"
```

### Step 3: Run `rotctld` Manually

Now, start the server by running this exact command in the same command prompt window:

```bash
rotctld -m 901 -r COM6 -s 600 -T 127.0.0.1 -t 4533 -vvvv
```

A lot of text will probably appear in the window. **Leave this command prompt window open.** It is now your running `rotctld` server, and it will print all log messages directly to this window.

### Step 4: Use Gpredict and Get the Logs

1.  Open **Gpredict**.
2.  Connect Gpredict to the rotor. You should see new log messages appear in the command prompt window.
3.  Try to **move the rotor** to a new position using Gpredict's controls. This is the step that is currently failing.
4.  After you have tried to move the rotor, go back to the command prompt window.
5.  **Copy all of the text** from the window. You can usually do this by right-clicking in the window and selecting "Mark", then highlighting all the text, and pressing Enter to copy.
6.  **Paste the copied text** back into our chat.

This log information is the key to solving this problem. It will show me the exact command Gpredict is sending and the error message `rotctld` is giving in response.
