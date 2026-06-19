import sounddevice  ############################### This is a new import
import numpy
import tkinter as Tk
from datetime import datetime


import tkinter as Tk
import math

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
                         text=label, fill="#888", font=("Arial", int(size/15), "bold"))
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
                                 fill="gray", font=("Arial", int(self.size/20)))

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
    def __init__(self, root_window, name, mass, max_speed, max_te,
                 traction_responsiveness, brake_responsiveness, axle_offsets=None):
        super().__init__(root_window)
        self.name = name
        self.title(self.name)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        # MASS ELEMENTS & BIG SPEED DIAL (Top Frame)
        speed_frame = Tk.Frame(self)
        speed_frame.pack(side=Tk.TOP, pady=0)
        self.mass_frame = Tk.Frame(speed_frame)
        self.mass_frame.pack()
        self.loco_mass = Tk.Label(self.mass_frame, text=f"{name} ({mass} Tonnes) +")
        self.loco_mass.pack(side=Tk.LEFT)
        self.load_mass_entry = integer_entry_box(self.mass_frame, width=5, callback=self.mass_updated)
        self.load_mass_entry.pack(side=Tk.LEFT)
        self.label2 = Tk.Label(self.mass_frame,text=" Tonnes")
        self.label2.pack(side=Tk.LEFT)
        # Speed Dial
        self.speed_dial = dial(speed_frame, 220, "MPH", 0, max_speed, 10, "orange")
        self.speed_dial.pack()
        # THROTTLE CONTROL GROUP
        throttle_frame = Tk.Frame(self)
        throttle_frame.pack(side=Tk.LEFT, padx=25, pady=10)
        # Power Dial
        self.power_dial = dial(throttle_frame, 100, "PWR %", 0, 100, 25, "cyan")
        self.power_dial.pack(pady=0)
        # Throttle - 8 Notch snap (resolution 12.5), visual notch numbers but no live value
        Tk.Label(throttle_frame, text="THROTTLE", font=('Arial', 10, 'bold')).pack(side=Tk.TOP)
        self.throttle_demand = Tk.DoubleVar(value=0)
        self.throttle = Tk.Scale(throttle_frame, from_=100, to=0, orient="vertical", width=60, length=400, 
                                 sliderlength=45, variable=self.throttle_demand, resolution=12.5, tickinterval=12.5, showvalue=0)
        self.throttle.pack(side=Tk.TOP)
        # BRAKE CONTROL GROUP
        brake_frame = Tk.Frame(self)
        brake_frame.pack(side=Tk.LEFT, padx=25, pady=10)
        # Brake Dial
        self.brake_dial = dial(brake_frame, 100, "PSI / %", 0, 100, 20, "red")
        self.brake_dial.pack(pady=0)
        # Brake - finer control with clearer markings
        Tk.Label(brake_frame, text="BRAKE", font=('Arial', 10, 'bold')).pack(side=Tk.TOP)
        self.brake_demand = Tk.DoubleVar(value=0)
        self.brake = Tk.Scale(brake_frame, from_=100, to=0, orient="vertical", width=60, length=400, 
                              sliderlength=45, variable=self.brake_demand, resolution=5, tickinterval=20, showvalue=0)
        self.brake.pack(side=Tk.TOP)
        # Set the Loco characteristics for this throttle class
        self.name = name
        self.loco_mass = mass
        self.load_mass = 0
        self.mass = self.loco_mass + self.load_mass
        self.max_speed = max_speed
        self.max_te = max_te
        self.traction_responsiveness = traction_responsiveness
        self.brake_responsiveness = brake_responsiveness
        self.axle_offsets = axle_offsets
        # Target values (The 'Input' from the Sliders)
        self.target_throttle = 0.0
        self.target_brake = 0.0
        # Current Actuals (The 'Output' for the Dials)
        self.actual_power = 0.0
        self.actual_brake_pressure = 100.0  # 100% = Full Release, 0% = Full Application
        self.current_speed = 0.0
        # Friction constant: how much the train slows down naturally
        self.rolling_resistance = 0.05
        # Add a counter to keep track of iterations (for temp logging) #####
        self.iterations = 0
        # Configure the audio output
        self.sample_rate = 44100
        # This block ititialises the Clackity-Clack sounds
        self.active_clacks = []   
        self.track_distance = 0.0
        self.joint_spacing = 120.0
        if axle_offsets is None:
            self.axle_joint_indices = []
            self.clack_sample = numpy.array([])
        else:
            # Initialize each axle's last-passed joint to -1
            self.axle_joint_indices = [-1] * len(axle_offsets)
            # Audio sound for the 'clack' as the wheels go over rail joints 
            duration = 0.5 
            t_sample = numpy.linspace(0, duration, int(self.sample_rate * duration))
            # THE WEIGHT (40Hz Thump) - This provides the 'thump'
            weight = numpy.sin(2 * numpy.pi * 40 * t_sample) * numpy.exp(-25.0 * t_sample)
            # THE RUMBLE (Filtered Brown Noise - much deeper than white noise )
            brown_noise = numpy.cumsum(numpy.random.normal(0, 0.05, len(t_sample)))
            brown_noise -= numpy.mean(brown_noise) # Center it
            rumble = brown_noise * numpy.exp(-35.0 * t_sample)
            # THE IMPACT (Dull Clank) - a very low-volume 'ping' that is instantly muffled
            impact = numpy.sin(2 * numpy.pi * 150 * t_sample) * numpy.exp(-120.0 * t_sample) * 0.2
            # Combine and Normalize
            raw_clack = weight + rumble + impact
            # We normalize to 0.7 to leave 'headroom' so multiple axles don't clip
            self.clack_sample = (raw_clack / numpy.max(numpy.abs(raw_clack))) * 0.7
            # Keep track of playing sounds: each entry is [current_sample_index, volume]
            # The track distance is updated by the 'generate_engine_frame' function
            self.active_clacks = [] 
            self.track_distance = 0.0
            self.joint_spacing = 120.0 
        # Start the Audio output stream
        self.audio_stream = sounddevice.OutputStream(channels=2, callback=self.audio_callback,
                                samplerate=self.sample_rate, blocksize=8192)
        self.audio_stream.start()
        # Start the 'loop' to keep the throttle updated (100ms = 10Hz)
        self.next_physics_loop_event = root.after(100, self.update_physics)
        
    def mass_updated(self):
        self.load_mass = self.load_mass_entry.get()
        self.mass = self.loco_mass + self.load_mass

    def on_close(self):
        # Cancel any pending physics loop events and the audio stream 
        self.after_cancel(self.next_physics_loop_event)
        self.audio_stream.abort()
        self.destroy()
        
    def update_physics(self):
        # 1) INPUTS & SPOOLING
        raw_val = float(self.throttle_demand.get())
        if raw_val < 5:
            self.target_throttle = 0
        else:
            notch = round((raw_val / 100) * 8)
            self.target_throttle = (notch / 8) * 100
        # ASYMMETRIC SPOOLING:
        # Slow spool-UP (gradual power application)
        # Fast spool-DOWN (immediate fuel cutoff)
        if self.target_throttle > self.actual_power:
            # Spooling up - slow (0.002)
            self.actual_power += (self.target_throttle - self.actual_power) * 0.01
        else:
            # Spooling down - fast (0.1) - almost instant
            self.actual_power += (self.target_throttle - self.actual_power) * 0.1
        # Brake Pipe - slower response to prevent overshoot
        target_pressure = 100.0 - float(self.brake_demand.get())
        self.actual_brake_pressure += (target_pressure - self.actual_brake_pressure) * 0.015
        # 2) TRACTIVE EFFORT (lbf)
        throttle_pct = self.actual_power / 100.0
        crossover_speed = 3.5
        if self.current_speed < crossover_speed:
            available_te = throttle_pct * self.max_te
        else:
            hp_limited_te = (2600 * 375 * throttle_pct) / self.current_speed
            available_te = min(hp_limited_te, throttle_pct * self.max_te)
        # 3) RESISTANCE (Davis Equation with smooth low-speed scaling)
        if self.current_speed < 0.01:
            total_resistance = 0.0
        else:
            # Scale resistance smoothly from 0 to 1 mph to prevent the 21,000 lbs jump
            speed_scaler = min(1.0, self.current_speed)
            res_a = (self.mass * 8.0) * speed_scaler
            res_b = (self.current_speed * (self.mass * 0.4))
            res_c = (self.current_speed**2) * 2.0
            total_resistance = res_a + res_b + res_c
        # 4) BRAKING (lbf)
        brake_perc = (100.0 - self.actual_brake_pressure) / 100.0
        braking_force_lbf = brake_perc * 35000
        # 5) NET FORCE & STATIONARY CLAMPING
        net_lbf = available_te - (total_resistance + braking_force_lbf)
        # If stationary and braking/resistance forces outweigh tractive effort,
        # the locomotive is held securely and shouldn't generate negative forces.
        if self.current_speed < 0.01 and net_lbf < 0:
            net_lbf = 0.0
        # 6) ACCELERATION
        accel_mph_per_sec = (net_lbf / (self.mass * 1.2)) * 0.01097
        # Apply time step (dt = 0.1 seconds)
        self.current_speed += accel_mph_per_sec * 0.1
        # 7)CLAMPING & UPDATES
        if self.current_speed < 0.01: 
            self.current_speed = 0
        if self.current_speed > self.max_speed: 
            self.current_speed = self.max_speed
        self.speed_dial.update_dial(self.current_speed)
        self.power_dial.update_dial(self.actual_power)
        self.brake_dial.update_dial(self.actual_brake_pressure)
        # Improved logging (includes brake metrics for clear evaluation)
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
        # Schedule the next update
        self.next_physics_loop_event = root.after(100, self.update_physics)

    def audio_callback(self, outdata, frames, time, status):
        # Generate the frame - now returning a 2D array [frames, channels]
        outdata[:] = self.generate_engine_frame(frames, time.currentTime)

    def generate_engine_frame(self, frames, current_time):
        sr = self.sample_rate
        fps = self.current_speed * 1.46667
        pwr = self.actual_power / 100.0
        # PRE-CALCULATE ENGINE & HISS (Standard)
        t = (numpy.arange(frames) + current_time * sr) / sr
        engine_audio = 0.3 * numpy.sign(numpy.sin(2 * numpy.pi * (15 + pwr * 35) * t) - 0.4) 
        engine_audio *= (0.7 + 0.3 * numpy.sin(2 * numpy.pi * (3 + pwr * 8) * t)) * (0.12 + (pwr * 0.25))
        hiss_audio = numpy.zeros(frames)
        pressure_diff = self.actual_brake_pressure - (100.0 - float(self.brake_demand.get()))
        if pressure_diff > 0.5:
            hiss_audio = numpy.random.normal(0, 0.12, frames) * 0.2
        # SUB-SAMPLED TRIGGER LOGIC & MIXING (Only runs if axle_offsets are provided)
        clack_audio = numpy.zeros(frames)
        ducking_factor = 1.0
        if self.axle_offsets is not None and len(self.axle_offsets) > 0:
            steps = 16
            frames_per_step = frames // steps
            dist_step = (fps * frames_per_step) / sr
            for s in range(steps):
                step_start_idx = s * frames_per_step
                if self.current_speed > 1.0:
                    for i, offset in enumerate(self.axle_offsets):
                        axle_pos = self.track_distance - offset
                        current_joint = int(axle_pos // self.joint_spacing)
                        if current_joint > self.axle_joint_indices[i]:
                            vol = min(1.3, self.current_speed / 40.0)
                            self.active_clacks.append([0, vol, step_start_idx]) 
                            self.axle_joint_indices[i] = current_joint
                    self.track_distance += dist_step
            # MIX ACTIVE CLACKS
            remaining_clacks = []
            for idx, vol, buffer_offset in self.active_clacks:
                remaining_samples = len(self.clack_sample) - idx
                available_space = frames - buffer_offset
                if available_space > 0:
                    play_len = min(available_space, remaining_samples)
                    clack_audio[buffer_offset : buffer_offset + play_len] += \
                        self.clack_sample[idx : idx + play_len] * vol
                    new_idx = idx + play_len
                    if new_idx < len(self.clack_sample):
                        remaining_clacks.append([new_idx, vol, 0]) 
                        if idx < (sr * 0.15): 
                            ducking_factor = 0.35
            self.active_clacks = remaining_clacks
        # STEREO MIX (If clacks are missing, clack_audio remains a clean zero-array)
        stereo_out = numpy.zeros((frames, 2))
        d_eng = engine_audio * ducking_factor
        stereo_out[:, 0] = d_eng + clack_audio + (hiss_audio * 0.3)
        stereo_out[:, 1] = (d_eng * 0.4) + clack_audio + (hiss_audio * 1.0)
        return (numpy.clip(stereo_out, -1.0, 1.0))

#----------------------------------------------------------------------------------
# Main Code begins here
#----------------------------------------------------------------------------------

root = Tk.Tk()
# A heavy Class 66 Freight - Takes ages to build power and dump air (for braking)
# Mass is in Metric Tonnes, Max speed is in MPH, Tractive effort is in Pounds-force (lbf)
# Responsiveness parameters are now calibrated for 100ms (0.1s) update intervals:
# - traction_responsiveness: 0.01 gives ~10-15 second spool-up time
# - brake_responsiveness: 0.03 gives realistic air brake response
# The axel offsets are only used to generate the clackity-clack sounds

heavy_freight = complex_throttle(root_window=root, name="Class 66", mass=129, max_speed=75, max_te=93000,
                traction_responsiveness=0.01, brake_responsiveness=0.03, axle_offsets=[0.0, 8.5, 42.0, 50.5])

# other = complex_throttle(root_window=root, name="Class 66", mass=129, max_speed=75, max_te=93000,
#                 traction_responsiveness=0.01, brake_responsiveness=0.03)

root.mainloop()
