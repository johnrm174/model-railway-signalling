#---------------------------------------------------------------------------------------
# Simple utility to connect to the NCE DCC Meter / Analyser for basic DCC Diagnostics.
# Current functionality includes capture/parsing of DCC Accessory commands and DCC
# Locomotive commands. Accessory commands (ASON/ASOF) are ALWAYS reported. Locomotive
# commands are only reported if they represent a change in the state of the locomotive
# (i.e. change in speed, functions or direction) - This is to filter out all the
# 'stay alive' commands that would otherwise flood the output
#---------------------------------------------------------------------------------------

import serial
import serial.tools.list_ports
import threading
import queue
import time
import re
import tkinter as tk

#---------------------------------------------------------------------------------------
# Port Configuration for NCE Communications over the USB Serial port
#---------------------------------------------------------------------------------------

BAUD_RATE = 115200

#---------------------------------------------------------------------------------------
# Function to find which USB port we think the NCE Analyser is connected to
#---------------------------------------------------------------------------------------

def find_nce_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if any(x in port.description for x in ["Silicon Labs", "CP210", "UART Bridge", "USB Serial", "ttyUSB"]):
            return(port.device)
    return(None)

#---------------------------------------------------------------------------------------
# Function to process/report received Locomotive updates: Returns a status
# change message as a string (or None if the message couldn't be decoded)
#---------------------------------------------------------------------------------------

def process_loco_update(loco_id, status):
    # Handle Speed/Direction/ESTOP
    if "S" in status and ":" not in status:
        if "ESTOP" in status:
            return(f" {loco_id} | EMERGENCY STOP triggered!")
        speed_match = re.search(r'S(\d{3})', status)
        if speed_match:
            speed = int(speed_match.group(1))
            direction = "Forward" if "F" in status else "Reverse"
            motion = "Stopped" if speed == 0 else f"Moving at {speed}"
            return(f" {loco_id} | {motion} ({direction})")
    # Handle Functions (FG1 to FG5)
    elif "FG" in status or "F:" in status: # Added F: to catch menu examples
        # Grab the Group ID (FG1, FG2, etc.)
        header = status.split(":")[0]
        raw_bits = status.split(":")[-1]
        # Split by commas to get each slot in the group
        slots = [s.strip() for s in raw_bits.split(",") if s.strip()]
        active_list = sorted(list(set(slots)), key=lambda x: int(x) if x.isdigit() else 0)
        # Include the Loco ID, Group ID (header) and the state in the final report
        if not active_list: return(f" {loco_id} | {header} | All OFF")
        else: return(f" {loco_id} | {header} | Active: {', '.join(active_list)}")
    return(None)

#---------------------------------------------------------------------------------------
# Class for the NCE interface - Class methods are:
#    start(self, port) - Open the specified serial port and start the Tx/Rx service
#    stop(self) - Close the serial port and stop the Tx/Rx service)
# All Tx and Rx messages are passed to/from the calling program via queues
#---------------------------------------------------------------------------------------

class NCEInterface:
    def __init__(self, port):
        # Open the serial port with a low timeout for responsiveness
        self.ser = serial.Serial(port, BAUD_RATE, timeout=0.01)
        self.rx_queue = queue.Queue()
        self.tx_queue = queue.Queue()
        self.running = True
        self.exited = False
        # A buffer is used for the incoming data to handle partial messages
        self.buffer = ""

    def start(self):
        self.thread = threading.Thread(target=self._io_loop, daemon=True)
        self.thread.start()

    def _io_loop(self):
        self.exited = False
        while self.running:
            try:
                # Handle Transmit of all messages in the tx_queue
                while not self.tx_queue.empty():
                    self.ser.write(self.tx_queue.get_nowait())
                # Handle Receive using the buffer to cope with partial messages
                if self.ser.in_waiting > 0:
                    new_data = self.ser.read(self.ser.in_waiting).decode('ascii', errors='replace')
                    self.buffer += new_data
                    # If we have a line terminator, we can extract complete messages
                    while "\r" in self.buffer or "\n" in self.buffer:
                        # Split at the first occurrence of a newline/return
                        # This ensures we only put WHOLE messages onto the rx_queue
                        if "\r" in self.buffer: line, self.buffer = self.buffer.split("\r", 1)
                        else: line, self.buffer = self.buffer.split("\n", 1)
                        clean_line = line.strip()
                        # Put the message onto the rx_queue
                        if clean_line: self.rx_queue.put(clean_line)
            except Exception as e:
                self.rx_queue.put(f"DEBUG_ERR: {e}")
            time.sleep(0.01)
        self.exited = True

    def stop(self):
        # Terminate the io_loop thread
        self.running = False
        # Wait until the io_loop has exited
        while not self.exited: time.sleep(0.001)
        # Close the port
        self.ser.close()

#---------------------------------------------------------------------------------------
# Main Class for the NCE Analyser application (uses a Tkinter root window)
#---------------------------------------------------------------------------------------

class NCEApp(tk.Tk):
    def __init__(self, nce_interface):
        super().__init__()
        # Create an instance of the nce_interface class (for Tx and Rx)
        self.nce = nce_interface
        # the loco_states dict holds the current states (speed, direction, functions)
        # of all Locos we have 'seen' - and uses this to ensure only loco state changes
        # are reported (filters out the constant stream of stay alive messages)        
        self.loco_states = {}
        # Configure the window
        self.title("NCE DCC Analyser - Steady RX Mode")
        self.geometry("1000x600")
        self.configure(bg="#121212")
        # Terminal Display (using a Tk Text widget)
        self.display = tk.Text(self, bg="black", fg="#00FF00", font=("TkFixedFont", 10), state="disabled")
        self.display.pack(expand=True, fill="both", padx=10, pady=10)
        # UI Color Tags
        self.display.tag_config("cmd", foreground="#E0F7FF")
        self.display.tag_config("sys", foreground="#EEEEEE")
        # Bind the events we need (close window and any key press
        self.bind("<Key>", self.on_key_press)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        # Start polling the rx queue for received messages
        self.write_to_screen("System Ready. Waiting for DCC data...", "sys")
        self.poll_rx()
        
    # Write messages to the window (Rx messages and selected Tx keypresses)
    def write_to_screen(self, text, tag=None):
        self.display.config(state="normal")
        ts = time.strftime('%H:%M:%S')
        self.display.insert(tk.END, f"[{ts}] {text}\n", tag)
        self.display.see(tk.END)
        self.display.config(state="disabled")

    # Send keypresses to the NCE interface - Note that we only display the
    # printable characters - space and return are not printed
    def on_key_press(self, event):
        char = event.char
        if event.keysym == "space":
            self.nce.tx_queue.put(b" ")
        elif event.keysym == "Return":
            self.nce.tx_queue.put(b"\r")
        elif char and char.isprintable():
            cmd = char.upper()
            self.nce.tx_queue.put(cmd.encode('ascii'))
            self.write_to_screen(f"NCE: {cmd}", "cmd")
        
    # Function to handle messages received from the NCE Interface
    def poll_rx(self):
        # Retrieve each message from the Rx Queue. If we get a Queue
        # Empty exception then we just wait for 20ms and try again
        while not self.nce.rx_queue.empty():
            message = self.nce.rx_queue.get_nowait()
            # Handle DCC Short Accessory commands
            if message.startswith("A"):
                match = re.search(r'A(\d{4})([RN])', message)
                if match:
                    addr = int(match.group(1))
                    state = "ASON" if match.group(2) == "R" else "ASOF"
                    self.write_to_screen(f"A{addr:<4} | {state}")
            # Handle Locomotive Commands (With State Tracking such that we only report changes)            
            elif message.startswith("L"):
                # Split the received message into individual reports (in case multiple messages
                # are bundled together - A typical message might look like 'L1234 SPEED 28'
                chunks = [("L"+c) for c in message.split("L") if c]
                for chunk in chunks:
                    # Reject any empty chunks (caused by leading or double delimiters)
                    if not chunk: continue
                    parts = chunk.split(" ", 1)
                    # Regect any malformed reports (missing the status text after the space)
                    if len(parts) < 2: continue
                    # Split the message into its constituent parts - loco_id and status
                    loco_id, status = parts[0], parts[1]
                    # Create a Specific Key to record the current state (in the loco_states dict)
                    # If status is "FG1:,,,", attr is "FG1". If "S000F", attr is "SPD".
                    attr = status.split(":")[0] if ":" in status else "SPD"
                    state_key = f"{loco_id}_{attr}"
                    # ONLY proceed if the RAW status has changed for THIS group                    
                    if self.loco_states.get(state_key) != status:
                        self.loco_states[state_key] = status
                        # Generate the clean message for output
                        clean_msg = process_loco_update(loco_id, status)
                        if clean_msg:
                            # Don't repeat the same clean message that was output last time
                            text_key = f"{state_key}_LAST_TEXT"
                            if self.loco_states.get(text_key) != clean_msg:
                                self.loco_states[text_key] = clean_msg
                                self.write_to_screen(clean_msg)
            else:
                # This handles the Help Menu and other info messages
                self.write_to_screen(f"NCE: {message}")
        self.after(20, self.poll_rx)

    # Function to perform an orderly shutdown of the application
    def on_close(self):
        self.nce.stop()
        self.destroy()

#---------------------------------------------------------------------------------------
# Main function starts here
#---------------------------------------------------------------------------------------

if __name__ == "__main__":
    # Find the USB serial port we think is connected to the NCE Meter
    # If we cant find a port then we just exit the application
    nce_port = find_nce_port()
    if nce_port:
        nce_interface = NCEInterface(nce_port)
        nce_interface.start()
        nce_application = NCEApp(nce_interface)
        nce_application.mainloop()
        
#############################################################################################################        
        
        