complex_throttle_enabled = False
try:
    import cv2  # New Import - Open Source Computer Vision Library ####################################################
    import sounddevice  # New Import ##################################################################################
    from PIL import Image, ImageTk  # New Import- Handles OpenCV to Tkinter conversion (APT install ###################
    complex_throttle_enabled = True
except:
    pass

import tkinter as Tk
import threading
import logging
import numpy
import math
import subprocess
import os

from .. import library

#---------------------------------------------------------------------------------------------
# Class for a generic dial object (based on a Cannvas)
#---------------------------------------------------------------------------------------------

class dial(Tk.Canvas):
    def __init__(self, parent, size, label, min_val, max_val, tick_step, color="white"):
        super().__init__(parent, width=size, height=size, highlightthickness=0)
        self.size = size
        self.min_val = min_val
        self.max_val = max_val
        self.tick_step = tick_step
        self.center = size / 2
        self.radius = (size / 2) * 0.85
        # Draw background and bezel
        self.create_oval(self.center-self.radius, self.center-self.radius, 
                         self.center+self.radius, self.center+self.radius, 
                         fill="#1a1a1a", outline="#444", width=3)
        # Draw Ticks and add the label
        self.draw_ticks()
        self.create_text(self.center, self.center + (self.radius * 0.4), 
                         text=label, fill="White", font=("Arial", int(size/15), "bold"))
        # Create the needle
        self.needle = self.create_line(self.center, self.center, self.center, self.center, 
                                       fill=color, width=max(2, int(size/40)), capstyle="round")
        # Center hub
        self.create_oval(self.center-5, self.center-5, self.center+5, self.center+5, fill="#333")
        self.update_dial(min_val)

    def draw_ticks(self):
        # Sweep from 135 to 405 degrees
        total_range = self.max_val - self.min_val
        num_ticks = int(total_range / self.tick_step) + 1
        for i in range(num_ticks):
            val = self.min_val + (i * self.tick_step)
            # Map value to angle
            angle = 135 + ((val - self.min_val) / total_range * 270)
            rad = math.radians(angle)
            # Start and end points for tick lines
            x_outer = self.center + self.radius * 0.95 * math.cos(rad)
            y_outer = self.center + self.radius * 0.95 * math.sin(rad)
            x_inner = self.center + self.radius * 0.80 * math.cos(rad)
            y_inner = self.center + self.radius * 0.80 * math.sin(rad)
            self.create_line(x_inner, y_inner, x_outer, y_outer, fill="white", width=1)
            # Add numeric labels for major ticks (every 2nd tick or based on size)
            if i % 2 == 0 or num_ticks < 10:
                x_text = self.center + self.radius * 0.65 * math.cos(rad)
                y_text = self.center + self.radius * 0.65 * math.sin(rad)
                self.create_text(x_text, y_text, text=str(int(val)), 
                                 fill="white", font=("Arial", int(self.size/15)))

    def update_dial(self, value):
        value = max(self.min_val, min(self.max_val, value))
        angle = 135 + ((value - self.min_val) / (self.max_val - self.min_val) * 270)
        rad = math.radians(angle)
        x = self.center + self.radius * 0.85 * math.cos(rad)
        y = self.center + self.radius * 0.85 * math.sin(rad)
        self.coords(self.needle, self.center, self.center, x, y)

#----------------------------------------------------------------------------------
# Class for basic integer entry box
#----------------------------------------------------------------------------------

class integer_entry_box(Tk.Entry):
    def __init__(self, parent_frame, width:int, callback=None):
        self.value = 0
        self.entry = Tk.StringVar(parent_frame, str(self.value))
        self.parent_frame = parent_frame
        self.callback = callback
        super().__init__(self.parent_frame, width=width, textvariable=self.entry, justify='center')
        self.bind('<Return>', self.entry_box_updated)
        self.bind('<Escape>', self.entry_box_cancel)
        self.bind('<FocusOut>', self.entry_box_updated)
        
    def entry_box_updated(self, event):
        entered_value = self.entry.get()        
        if entered_value == "":
            self.entry.set("0")
            self.value = 0
        elif not entered_value.lstrip('-+').isdigit():
            self.configure(fg='red')
        else:
            self.configure(fg='black')
            self.value = int(self.entry.get())
        if event.keysym == 'Return': self.parent_frame.focus()
        if self.callback is not None: self.callback()
        
    def entry_box_cancel(self, event):
        self.entry.set(str(self.value))
        self.configure(fg='black')
        self.parent_frame.focus()
        
    def get(self):
        return(self.value)
        
#----------------------------------------------------------------------------------
# Class for a complex throttle Window (using the dials above)
# The axle offsets are only used for generating the clakity-clack sounds
#----------------------------------------------------------------------------------

class complex_throttle(Tk.Toplevel):
    def __init__(self, root_window, name, mass, max_speed, max_te, traction_responsiveness, 
                 brake_responsiveness, dcc_address:int, axle_offsets=None, stream_url=None):
        super().__init__(root_window)
        self.name = name
        self.title(self.name)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root_window = root_window
        self.dcc_address = dcc_address
        self.session_id = None  
        self.dcc_direction = True  
        self.dcc_speed_value = 0
        # Set up single-threaded video stream variables
        self.stream_url = stream_url
        self.cap = None
        self.next_video_loop_event = None
        self.video_running = False
        if self.stream_url:
            video_frame = Tk.Frame(self, bg="black", width=480, height=270)
            video_frame.pack(side=Tk.TOP, pady=5)
            video_frame.pack_propagate(False)
            self.video_screen = Tk.Label(video_frame, text="Connecting to Cab View...", fg="white", bg="black", width=60, height=15)
            self.video_screen.pack(fill=Tk.BOTH, expand=True)
            self.cap = cv2.VideoCapture(self.stream_url)
            if self.cap.isOpened():
                self.video_running = True
                self.update_video_stream()
            else:
                self.video_screen.configure(text="Error: Could not open ESPHome Stream")
        # Control desk UI layout
        control_desk = Tk.Frame(self)
        control_desk.pack(side=Tk.TOP, fill=Tk.BOTH, expand=True, padx=10, pady=10)
        # Left Column: Throttle Slider
        left_lever_frame = Tk.Frame(control_desk)
        left_lever_frame.pack(side=Tk.LEFT, padx=10, fill=Tk.Y)
        Tk.Label(left_lever_frame, text="THROTTLE", font=('Arial', 10, 'bold')).pack(side=Tk.TOP)
        self.throttle_demand = Tk.DoubleVar(value=0)
        self.throttle = Tk.Scale(left_lever_frame, from_=100, to=0, orient="vertical", width=50, length=320, 
                                 sliderlength=40, variable=self.throttle_demand, resolution=12.5, tickinterval=12.5, showvalue=0)
        self.throttle.pack(side=Tk.TOP, expand=True, fill=Tk.Y)
        # Center Column: Dashboard Instruments & Mass Config
        center_dashboard = Tk.Frame(control_desk)
        center_dashboard.pack(side=Tk.LEFT, padx=5, fill=Tk.BOTH, expand=True)
        self.mass_frame = Tk.Frame(center_dashboard)
        self.mass_frame.pack(pady=5)
        line1_frame = Tk.Frame(self.mass_frame)
        line1_frame.pack(side=Tk.TOP, anchor="center")
        Tk.Label(line1_frame, text=f"{name} ({mass} Tonnes)", font=('Arial', 10, 'bold')).pack()
        line2_frame = Tk.Frame(self.mass_frame)
        line2_frame.pack(side=Tk.TOP, anchor="center", pady=(2, 0))
        Tk.Label(line2_frame, text="Load: ").pack(side=Tk.LEFT)
        self.load_mass_entry = integer_entry_box(line2_frame, width=5, callback=self.mass_updated)
        self.load_mass_entry.pack(side=Tk.LEFT)
        Tk.Label(line2_frame, text=" (Tonnes)").pack(side=Tk.LEFT)
        self.speed_dial = dial(center_dashboard, 180, "MPH", 0, max_speed, 10, "orange")
        self.speed_dial.pack(pady=0)
        aux_dial_frame = Tk.Frame(center_dashboard)
        aux_dial_frame.pack(pady=5)
        self.power_dial = dial(aux_dial_frame, 120, "PWR\n  %", 0, 100, 25, "cyan")
        self.power_dial.pack(side=Tk.LEFT, padx=5)
        self.brake_dial = dial(aux_dial_frame, 120, "PSI\n  %", 0, 100, 20, "red")
        self.brake_dial.pack(side=Tk.LEFT, padx=5)
        # Right Column: Brake Slider
        right_lever_frame = Tk.Frame(control_desk)
        right_lever_frame.pack(side=Tk.LEFT, padx=10, fill=Tk.Y)
        Tk.Label(right_lever_frame, text="BRAKE", font=('Arial', 10, 'bold')).pack(side=Tk.TOP)
        self.brake_demand = Tk.DoubleVar(value=0)
        self.brake = Tk.Scale(right_lever_frame, from_=100, to=0, orient="vertical", width=50, length=320, 
                              sliderlength=40, variable=self.brake_demand, resolution=5, tickinterval=20, showvalue=0)
        self.brake.pack(side=Tk.TOP, expand=True, fill=Tk.Y)                
        # Train Physics Variables Initialization
        self.loco_mass = mass
        self.load_mass = 0
        self.mass = self.loco_mass + self.load_mass
        self.max_speed = max_speed
        self.max_te = max_te
        self.traction_responsiveness = traction_responsiveness
        self.brake_responsiveness = brake_responsiveness
        self.axle_offsets = axle_offsets
        self.target_throttle = 0.0
        self.target_brake = 0.0
        self.actual_power = 0.0
        self.actual_brake_pressure = 100.0  
        self.current_speed = 0.0
        self.rolling_resistance = 0.05
        self.iterations = 0
        # Synthesized Audio Engine Setup
        self.sample_rate = 22050
        self.stereo_buffer = numpy.zeros((8192, 2)) 
        self.hiss_buffer_len = self.sample_rate * 2
        self.pre_baked_hiss = numpy.random.normal(0, 0.12, self.hiss_buffer_len) * 0.2
        self.audio_sample_index = 0  
        self.track_distance = 0.0
        self.joint_spacing = 120.0
        self.clack_lock = threading.Lock()
        self.pending_clacks = [] 
        self.active_clacks = []  
        # Generate the synthetic track joint impact sound wave profile
        if axle_offsets is None:
            self.axle_joint_indices = []
            self.clack_sample = numpy.array([])
        else:
            self.axle_joint_indices = [-1] * len(axle_offsets)
            duration = 0.5 
            t_sample = numpy.linspace(0, duration, int(self.sample_rate * duration))
            weight = numpy.sin(2 * numpy.pi * 40 * t_sample) * numpy.exp(-25.0 * t_sample)
            brown_noise = numpy.cumsum(numpy.random.normal(0, 0.05, len(t_sample)))
            brown_noise -= numpy.mean(brown_noise) 
            rumble = brown_noise * numpy.exp(-35.0 * t_sample)
            impact = numpy.sin(2 * numpy.pi * 150 * t_sample) * numpy.exp(-120.0 * t_sample) * 0.2
            self.clack_sample = ((weight + rumble + impact) / numpy.max(numpy.abs(weight + rumble + impact))) * 0.7
        # Start background audio device output stream
        self.audio_stream = sounddevice.OutputStream(channels=2, callback=self.audio_callback,
                                                     samplerate=self.sample_rate, blocksize=8192)
        self.audio_stream.start()
        self.next_physics_loop_event = self.root_window.after(100, self.update_physics)
        library.request_loco_session(self.dcc_address, callback=self.handle_prototype_session)

    def handle_prototype_session(self, dcc_address:int, session_id:int):
        self.session_id = session_id

    def update_video_stream(self):
        # UI main-thread loop to fetch and render incoming network frames
        if not self.video_running or self.cap is None:
            return
        # grab moves the socket buffer forward; retrieve decodes the image frame
        if self.cap.grab():
            ret, frame = self.cap.retrieve()
            if ret and frame is not None:
                frame = cv2.resize(frame, (480, 270))
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_screen.imgtk = imgtk
                self.video_screen.configure(image=imgtk)
        if self.video_running:
            self.next_video_loop_event = self.after(30, self.update_video_stream)

    def mass_updated(self):
        self.load_mass = self.load_mass_entry.get()
        self.mass = self.loco_mass + self.load_mass

    def on_close(self):
        # Shut down loop flags and cancel pending Tkinter task execution loops
        self.video_running = False
        if self.next_video_loop_event: 
            self.after_cancel(self.next_video_loop_event)
        if self.next_physics_loop_event: 
            self.root_window.after_cancel(self.next_physics_loop_event)
        # Release the C library video capture structure safely on the same thread
        if self.cap:
            self.cap.release()
            self.cap = None
        # Terminate DCC controller sessions and stop sound card device processing
        if self.session_id is not None:
            try:
                library.release_loco_session(self.session_id)
            except Exception:
                pass
            self.session_id = None
        self.audio_stream.abort()
        self.destroy()
        
    def update_physics(self):
        # Scale current throttle input to simulated notches
        raw_val = float(self.throttle_demand.get())
        if raw_val < 5:
            self.target_throttle = 0
        else:
            notch = round((raw_val / 100) * 8)
            self.target_throttle = (notch / 8) * 100
        # Simulate mechanical engine speed delay responses
        if self.target_throttle > self.actual_power:
            self.actual_power += (self.target_throttle - self.actual_power) * 0.01
        else:
            self.actual_power += (self.target_throttle - self.actual_power) * 0.1
        # Track brake pipe reservoir air pressure discharge rates
        target_pressure = 100.0 - float(self.brake_demand.get())
        self.actual_brake_pressure += (target_pressure - self.actual_brake_pressure) * 0.015
        # Compute available tractive effort based on diesel speed crossovers
        throttle_pct = self.actual_power / 100.0
        crossover_speed = 3.5
        if self.current_speed < crossover_speed:
            available_te = throttle_pct * self.max_te
        else:
            hp_limited_te = (2600 * 375 * throttle_pct) / self.current_speed
            available_te = min(hp_limited_te, throttle_pct * self.max_te)
        # Apply standard Davis Equation coefficients to determine rolling friction forces
        if self.current_speed < 0.01:
            total_resistance = 0.0
        else:
            speed_scaler = min(1.0, self.current_speed)
            res_a = (self.mass * 8.0) * speed_scaler
            res_b = (self.current_speed * (self.mass * 0.4))
            res_c = (self.current_speed**2) * 2.0
            total_resistance = res_a + res_b + res_c
        # Factor in total braking forces and balance net force limitations
        brake_perc = (100.0 - self.actual_brake_pressure) / 100.0
        braking_force_lbf = brake_perc * 35000
        net_lbf = available_te - (total_resistance + braking_force_lbf)
        if self.current_speed < 0.01 and net_lbf < 0:
            net_lbf = 0.0
        # Calculate resulting velocity changes based on total trailing weight limits
        accel_mph_per_sec = (net_lbf / (self.mass * 1.2)) * 0.01097
        self.current_speed += accel_mph_per_sec * 0.1
        # Track track layout distances to schedule rhythmic wheel joint clacks
        if self.axle_offsets is not None and self.current_speed > 0.01:
            fps = self.current_speed * 1.46667
            self.track_distance += fps * 0.1
            for i, offset in enumerate(self.axle_offsets):
                axle_pos = self.track_distance - offset
                current_joint = int(axle_pos // self.joint_spacing)
                if current_joint > self.axle_joint_indices[i]:
                    vol = min(1.3, self.current_speed / 40.0)
                    with self.clack_lock:
                        self.pending_clacks.append([0, vol])
                    self.axle_joint_indices[i] = current_joint
        if self.current_speed < 0.01: self.current_speed = 0
        if self.current_speed > self.max_speed: self.current_speed = self.max_speed
        # Refresh analog dashboard instrument displays
        self.speed_dial.update_dial(self.current_speed)
        self.power_dial.update_dial(self.actual_power)
        self.brake_dial.update_dial(self.actual_brake_pressure)
        # Issue updated locomotive speed updates to the physical DCC station framework
        new_speed_value = int((self.current_speed / self.max_speed) * 127)
        if self.session_id is not None and self.dcc_speed_value != new_speed_value:
            library.set_loco_speed_and_direction(self.session_id, new_speed_value, self.dcc_direction)        
        self.dcc_speed_value = new_speed_value
        # Print diagnostic logging outputs to stdout every 10 iterations (1 second)
        self.iterations += 1
        if self.iterations % 10 == 0:
            brk_dem = float(self.brake_demand.get())
            log_line = (
                f"{self.name:<9} | "
                f"Speed: {self.current_speed:>5.2f} mph | "
                f"Thrt Dem: {self.target_throttle:>3.0f}% ({self.actual_power:>3.0f}% Act) | "
                f"TE: {available_te:>5.0f} lbs | "
                f"Brake Dem: {brk_dem:>3.0f}% (Pipe: {self.actual_brake_pressure:>5.1f}% -> {braking_force_lbf:>5.0f} lbs) | "
                f"Res: {total_resistance:>5.0f} lbs | "
                f"Net: {net_lbf:>6.0f} lbs")
            print(log_line)
        if self.video_running:
            self.next_physics_loop_event = self.root_window.after(100, self.update_physics)

    def audio_callback(self, outdata, frames, time, status):
        outdata[:] = self.generate_engine_frame(frames)

    def generate_engine_frame(self, frames):
        # Synthesize real-time diesel engine roar from frequency-modulated square/sine configurations
        sr = self.sample_rate
        pwr = self.actual_power / 100.0
        t = (numpy.arange(frames) + self.audio_sample_index) / sr
        self.audio_sample_index += frames
        engine_audio = 0.3 * numpy.sign(numpy.sin(2 * numpy.pi * (15 + pwr * 35) * t) - 0.4) 
        engine_audio *= (0.7 + 0.3 * numpy.sin(2 * numpy.pi * (3 + pwr * 8) * t)) * (0.12 + (pwr * 0.25))
        # Layer continuous brake valve white-noise hiss adjustments onto Left track channel
        hiss_audio = self.stereo_buffer[:frames, 0] 
        hiss_audio[:] = 0.0
        pressure_diff = self.actual_brake_pressure - (100.0 - float(self.brake_demand.get()))
        if pressure_diff > 0.5:
            start_idx = numpy.random.randint(0, self.hiss_buffer_len - frames)
            hiss_audio = self.pre_baked_hiss[start_idx : start_idx + frames]
        # Dequeue track joint clacks and overlap them across sample boundaries
        clack_audio = self.stereo_buffer[:frames, 1] 
        clack_audio[:] = 0.0
        if self.pending_clacks:
            with self.clack_lock:
                self.active_clacks.extend(self.pending_clacks)
                self.pending_clacks.clear()
        ducking_factor = 1.0
        for clack in self.active_clacks:
            idx, vol = clack[0], clack[1]
            remaining_samples = len(self.clack_sample) - idx
            play_len = min(frames, remaining_samples)
            clack_audio[:play_len] += self.clack_sample[idx : idx + play_len] * vol
            clack[0] += play_len 
            if idx < (sr * 0.15): 
                ducking_factor = 0.35
        self.active_clacks = [c for c in self.active_clacks if c[0] < len(self.clack_sample)]
        # Interleave synthesized assets into standard two-channel stereo fields and apply hard safety clipping bounds
        self.stereo_buffer[:frames, :] = 0.0
        d_eng = engine_audio * ducking_factor
        self.stereo_buffer[:frames, 0] = d_eng + clack_audio + (hiss_audio * 0.3)
        self.stereo_buffer[:frames, 1] = (d_eng * 0.4) + clack_audio + (hiss_audio * 1.0)
        return numpy.clip(self.stereo_buffer[:frames], -1.0, 1.0)
    
#----------------------------------------------------------------------------------
# Main Code begins here
#----------------------------------------------------------------------------------

# A heavy Class 66 Freight - Takes ages to build power and dump air (for braking)
# Mass is in Metric Tonnes, Max speed is in MPH, Tractive effort is in Pounds-force (lbf)
# Responsiveness parameters are now calibrated for 100ms (0.1s) update intervals:
# - traction_responsiveness: 0.01 gives ~10-15 second spool-up time
# - brake_responsiveness: 0.03 gives realistic air brake response
# The axel offsets are only used to generate the clackity-clack sounds

def test_complex_throttle(root):
    if complex_throttle_enabled:
        heavy_freight = complex_throttle(root_window=root, name="Class 66", mass=129, max_speed=75, max_te=93000,
                        traction_responsiveness=0.01, brake_responsiveness=0.03, dcc_address=3,
                        axle_offsets=[0.0, 8.5, 42.0, 50.5], stream_url="http://192.168.1.149:8080")

# other = complex_throttle(root_window=root, name="Class 66", mass=129, max_speed=75, max_te=93000,
#                 traction_responsiveness=0.01, brake_responsiveness=0.03)

