# yt_downloader_app.py - Chunk 1/3

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import yt_dlp
import os
import re
import math
from tkinter import Canvas

# --- Global Application Settings ---
APP_NAME = "YT Downloader"
APP_VERSION = "v1.0"
DEFAULT_THEME = "dark-blue" # Options: "blue", "green", "dark-blue"
MONOSPACE_FONT = ("Consolas", 11) # For logs and potentially other areas

# --- Theme & Appearance Setup ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme(DEFAULT_THEME)

# --- New Futuristic Theme Constants ---
FUTURISTIC_THEME = {
    "bg_color": "#0f1520",          # Dark blue-black background
    "card_bg": "#162030",           # Slightly lighter card background
    "accent_primary": "#00a8ff",    # Bright blue accent
    "accent_secondary": "#6b38fb",  # Purple accent
    "success_color": "#00ffc3",     # Cyan-green for success
    "warning_color": "#ffbb00",     # Amber for warnings
    "error_color": "#ff5252",       # Red for errors
    "text_primary": "#ffffff",      # White text
    "text_secondary": "#8f9bbc",    # Light blue-gray text
    "glow_intensity": 0.15,         # Controls the intensity of glow effects
}

# --- Circular Progress Widget ---
class CircularProgress(ctk.CTkFrame):
    """A futuristic circular progress indicator with glow effects."""
    
    def __init__(self, master, size=120, fg_color="#00a8ff",
                 bg_color="#162030", text_color="#ffffff", glow_color=None,
                 ring_width=8, **kwargs):
        # Default to semi-transparent frame
        if "fg_color" not in kwargs:
            kwargs["fg_color"] = "transparent"

        super().__init__(master, width=size, height=size, **kwargs)

        self.size = size
        self.fg_color = fg_color      # Primary color for filled progress
        self.bg_color = bg_color      # Background color
        self.text_color = text_color  # Color for percentage text
        self.glow_color = glow_color or fg_color  # Color for glow effect
        self.ring_width = ring_width  # Width of the progress ring

        # State variables
        self.progress = 0.0  # 0.0 to 1.0

        # Create canvas for drawing
        self.canvas = Canvas(self, width=size, height=size,
                            bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Text display for percentage
        self.percentage_var = ctk.StringVar(value="0%")

        # Initial draw
        self._draw_progress()
        
    def _draw_progress(self):
        """Redraw the circular progress indicator."""
        self.canvas.delete("all")
        
        # Calculate dimensions
        center_x = center_y = self.size / 2
        # Outer and inner radius of the progress ring
        outer_radius = (self.size / 2) - 5
        inner_radius = outer_radius - self.ring_width
        
        # Draw subtle background glow (more intense when progress is higher)
        glow_radius = outer_radius + (10 * self.progress)
        glow_alpha = int(min(120, 40 + (80 * self.progress)))
        glow_color = self._adjust_color_alpha(self.glow_color, glow_alpha)
        
        # Create gradient glow effect
        for i in range(5):
            r = glow_radius - (i * 2)
            alpha = max(0, glow_alpha - (i * 25))
            color = self._adjust_color_alpha(self.glow_color, alpha)
            if r > 0:  
                self.canvas.create_oval(
                    center_x - r, center_y - r, 
                    center_x + r, center_y + r,
                    outline=color, width=1, fill=""
                )
        
        # Draw background circle (track)
        track_color = self._darken_color(self.fg_color, 0.3)
        self.canvas.create_oval(
            center_x - outer_radius, center_y - outer_radius,
            center_x + outer_radius, center_y + outer_radius,
            outline=track_color, width=self.ring_width, fill=self.bg_color
        )
        
        # Draw progress arc
        if self.progress > 0:
            # Calculate arc angles for progress
            start_angle = 90  # Start from top (90 degrees)
            extent_angle = -360 * self.progress  # Negative for clockwise
            
            # Draw progress arc
            self.canvas.create_arc(
                center_x - outer_radius, center_y - outer_radius,
                center_x + outer_radius, center_y + outer_radius,
                start=start_angle, extent=extent_angle,
                style="arc", outline=self.fg_color, width=self.ring_width
            )
            
            # Add glow effect to the progress end
            end_angle_rad = math.radians(start_angle + extent_angle)
            end_x = center_x + (outer_radius * math.cos(end_angle_rad))
            end_y = center_y - (outer_radius * math.sin(end_angle_rad))
            
            glow_size = self.ring_width + 2
            
            self.canvas.create_oval(
                end_x - glow_size, end_y - glow_size,
                end_x + glow_size, end_y + glow_size,
                fill=self.fg_color, outline=""
            )
        
        # Draw inner circle (with slight transparency for depth)
        inner_bg = self._adjust_color_alpha(self.bg_color, 200)
        self.canvas.create_oval(
            center_x - inner_radius, center_y - inner_radius,
            center_x + inner_radius, center_y + inner_radius,
            fill=inner_bg, outline=""
        )
        
        # Draw percentage text
        text_size = int(self.size / 5)
        percentage_text = f"{int(self.progress * 100)}%"
        self.canvas.create_text(
            center_x, center_y,
            text=percentage_text,
            fill=self.text_color,
            font=("Arial", text_size, "bold")
        )
        
        # Optional: Additional visual elements can be added for more futuristic style
        # For example, small tick marks, digital readouts, etc.
        self._draw_tick_marks(center_x, center_y, outer_radius)

    def _draw_tick_marks(self, cx, cy, radius):
        """Draw small tick marks around the circle for futuristic style."""
        num_ticks = 60  # One per 6 degrees
        tick_length_major = 6
        tick_length_minor = 3
        
        for i in range(num_ticks):
            angle_rad = math.radians(i * (360 / num_ticks))
            is_major = i % 5 == 0  # Major tick every 5 ticks (30 degrees)
            
            tick_length = tick_length_major if is_major else tick_length_minor
            tick_color = self.fg_color if is_major else self._adjust_color_alpha(self.fg_color, 100)
            
            # Calculate outer point of tick
            outer_x = cx + (radius + 2) * math.cos(angle_rad)
            outer_y = cy + (radius + 2) * math.sin(angle_rad)
            
            # Calculate inner point of tick
            inner_x = cx + (radius + 2 + tick_length) * math.cos(angle_rad)
            inner_y = cy + (radius + 2 + tick_length) * math.sin(angle_rad)
            
            # Draw tick line
            self.canvas.create_line(
                outer_x, outer_y, inner_x, inner_y,
                fill=tick_color, width=1
            )
    
    def set_progress(self, value):
        """Set the progress value (0.0 to 1.0) and redraw."""
        # Ensure value is between 0 and 1
        self.progress = max(0.0, min(1.0, float(value)))

        # Update percentage text
        self.percentage_var.set(f"{int(self.progress * 100)}%")

        # Redraw the progress indicator
        self._draw_progress()
        return self.progress

        
    def _adjust_color_alpha(self, hex_color, alpha):
        """Convert hex color to a lighter version to simulate alpha."""
        # Strip # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert hex to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Instead of using alpha directly (which Tkinter doesn't support),
        # blend with background color based on alpha value
        alpha_ratio = alpha / 255
        
        # Get background color
        bg_hex = self.bg_color.lstrip('#')
        bg_r = int(bg_hex[0:2], 16) if len(bg_hex) >= 6 else 0
        bg_g = int(bg_hex[2:4], 16) if len(bg_hex) >= 6 else 0
        bg_b = int(bg_hex[4:6], 16) if len(bg_hex) >= 6 else 0
        
        # Blend colors
        r = int(r * alpha_ratio + bg_r * (1 - alpha_ratio))
        g = int(g * alpha_ratio + bg_g * (1 - alpha_ratio))
        b = int(b * alpha_ratio + bg_b * (1 - alpha_ratio))
        
        # Return as hex without alpha component
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _darken_color(self, hex_color, factor=0.7):
        """Darken a hex color by a factor (0.0-1.0)."""
        # Strip # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert hex to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Darken
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        
        # Return as hex
        return f'#{r:02x}{g:02x}{b:02x}'

# --- Futuristic Card Frame ---
class FuturisticCard(ctk.CTkFrame):
    """A stylized frame with subtle glow effects and rounded edges."""
    
    def __init__(self, master, title=None, icon=None, accent_color="#00a8ff", 
                 fg_color=FUTURISTIC_THEME["card_bg"], 
                 text_color=FUTURISTIC_THEME["text_primary"], 
                 height=None, **kwargs):
                 
        # Set border width and corner radius for futuristic look
        if "border_width" not in kwargs:
            kwargs["border_width"] = 1
        if "corner_radius" not in kwargs:
            kwargs["corner_radius"] = 10
        if "border_color" not in kwargs:
            kwargs["border_color"] = self._adjust_color_brightness(accent_color, 0.5)
            
        super().__init__(master, fg_color=fg_color, **kwargs)
        
        self.accent_color = accent_color
        self.text_color = text_color
        self.title = title
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Create title bar if title is provided
        if title:
            title_height = 30
            title_bar = ctk.CTkFrame(self, height=title_height, 
                                   fg_color=self._adjust_color_brightness(accent_color, 0.2),
                                   corner_radius=kwargs.get("corner_radius", 10))
            title_bar.grid(row=0, column=0, sticky="ew", padx=1, pady=(1, 0))
            title_bar.grid_columnconfigure(0, weight=1)
            
            title_label = ctk.CTkLabel(title_bar, text=title, text_color=text_color,
                                     font=("Arial", 12, "bold"))
            title_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
            
            # Content frame below the title bar
            self.content_frame = ctk.CTkFrame(self, fg_color=fg_color, corner_radius=0)
            self.content_frame.grid(row=1, column=0, sticky="nsew", padx=1, pady=(0, 1))
            self.content_frame.grid_columnconfigure(0, weight=1)
            
            # Make content area expandable
            self.grid_rowconfigure(1, weight=1)
        else:
            # If no title, the entire frame is the content area
            self.content_frame = self
    
    def _adjust_color_brightness(self, hex_color, factor):
        """Adjust color brightness - factor > 1 brightens, < 1 darkens."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        r = min(255, max(0, int(r * factor)))
        g = min(255, max(0, int(g * factor)))
        b = min(255, max(0, int(b * factor)))
        
        return f'#{r:02x}{g:02x}{b:02x}'

# --- Custom Logger for yt-dlp integration ---
class YdlLogger:
    def __init__(self, app_instance):
        self.app = app_instance

    def debug(self, msg):
        # Filter out common verbose messages, or messages handled by progress hook
        if "Extracting URL" in msg or "Downloading webpage" in msg \
           or msg.startswith('[download] Destination:'): # Progress hook will handle destination
            return
        # You can uncomment below to see more detailed debug logs if needed
        # self.app.log_message(f"DEBUG: {msg}", level="debug")

    def info(self, msg):
        # yt-dlp info messages can be useful, e.g., when it identifies a playlist
        self.app.log_message(f"{msg}", level="info")

    def warning(self, msg):
        self.app.log_message(f"WARN: {msg}", level="warning")

    def error(self, msg):
        self.app.log_message(f"ERROR: {msg}", level="error")


# --- Main Application Window ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.apply_futuristic_theme()

        # --- State Variables ---
        self.current_fetched_info = {} # Stores {url: {'title': ..., 'formats': ..., 'is_playlist': ...}}
        self.is_operation_running = False
        self.available_resolutions = ["Best"] # Default/fallback

        # --- Configure Grid Layout for the main window ---
        self.grid_columnconfigure(0, weight=1)
        # Row weights: URL Input (0), Options (1), Actions (2), Progress (3), Log (4)
        self.grid_rowconfigure(4, weight=1) # Log area expands

        # --- 1. URL Input Section ---
        url_input_frame = ctk.CTkFrame(self)
        url_input_frame.grid(row=0, column=0, padx=15, pady=(15, 7), sticky="ew")
        url_input_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(url_input_frame, text="YouTube URL(s) (one per line for batch):", font=("Roboto", 13, "bold")) \
            .grid(row=0, column=0, padx=10, pady=(10,5), sticky="w")

        self.url_entry = ctk.CTkTextbox(url_input_frame, height=100, wrap="none", font=("Arial", 12))
        self.url_entry.grid(row=1, column=0, padx=10, pady=(0,10), sticky="ew")
        self.url_entry.bind("<KeyRelease>", lambda event: self.check_if_getinfo_ready())


        # --- 2. Options Section ---
        options_main_frame = ctk.CTkFrame(self)
        options_main_frame.grid(row=1, column=0, padx=15, pady=7, sticky="ew")
        options_main_frame.grid_columnconfigure(0, weight=1) # Allow path selection to expand

        # --- 2a. Download Type and Format ---
        type_format_frame = ctk.CTkFrame(options_main_frame, fg_color="transparent")
        type_format_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(type_format_frame, text="Download Type:", font=("Roboto", 12)).grid(row=0, column=0, padx=(0,10), pady=5, sticky="w")
        self.download_type_var = ctk.StringVar(value="Video")
        self.radio_video = ctk.CTkRadioButton(type_format_frame, text="Video (MP4)", variable=self.download_type_var, value="Video", command=self.update_ui_for_type_change)
        self.radio_video.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.radio_audio = ctk.CTkRadioButton(type_format_frame, text="Audio (MP3)", variable=self.download_type_var, value="Audio", command=self.update_ui_for_type_change)
        self.radio_audio.grid(row=0, column=2, padx=15, pady=5, sticky="w")

        ctk.CTkLabel(type_format_frame, text="Format/Quality:", font=("Roboto", 12)).grid(row=0, column=3, padx=(20,10), pady=5, sticky="w")
        self.resolution_var = ctk.StringVar(value="Best")
        self.resolution_dropdown = ctk.CTkOptionMenu(type_format_frame, variable=self.resolution_var, values=["Best"], state="disabled", width=140)
        self.resolution_dropdown.grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.resolution_dropdown.set("Best") # Ensure default is visually selected

        # --- 2b. Download Path Selection ---
        path_frame = ctk.CTkFrame(options_main_frame, fg_color="transparent")
        path_frame.grid(row=1, column=0, padx=10, pady=(5,10), sticky="ew")
        path_frame.grid_columnconfigure(1, weight=1) # Path entry expands

        ctk.CTkLabel(path_frame, text="Save To:", font=("Roboto", 12)).grid(row=0, column=0, padx=(0,10), pady=5, sticky="w")
        default_dl_path = os.path.join(os.path.expanduser("~"), "Downloads", APP_NAME)
        os.makedirs(default_dl_path, exist_ok=True) # Create app-specific download folder
        self.download_path_var = ctk.StringVar(value=default_dl_path)
        self.path_entry = ctk.CTkEntry(path_frame, textvariable=self.download_path_var, state="readonly", font=("Arial", 11))
        self.path_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.browse_button = ctk.CTkButton(path_frame, text="Browse", command=self.browse_path, width=100)
        self.browse_button.grid(row=0, column=2, padx=(5,0), pady=5, sticky="e")

        # --- 3. Action Buttons Section (Placeholder for now) ---
        action_frame = ctk.CTkFrame(self)
        action_frame.grid(row=2, column=0, padx=15, pady=7, sticky="ew")
        action_frame.grid_columnconfigure((0, 1), weight=1) # Distribute space for buttons

        self.getinfo_button = ctk.CTkButton(action_frame, text="Fetch Info & Formats", command=self.start_getinfo_thread, height=35, font=("Roboto", 13, "bold"), state="disabled")
        self.getinfo_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.download_button = ctk.CTkButton(action_frame, text="Download", command=self.start_download_thread, height=35, font=("Roboto", 13, "bold"), state="disabled")
        self.download_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # --- 4. Progress & Status Display Section (Placeholder for now) ---
        status_progress_frame = FuturisticCard(self, title="Download Status")
        status_progress_frame.grid(row=3, column=0, padx=15, pady=7, sticky="ew")
        status_progress_frame.content_frame.grid_columnconfigure((0, 1), weight=1)

        # Left side: status text and linear progress
        status_left = ctk.CTkFrame(status_progress_frame.content_frame, fg_color="transparent")
        status_left.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        status_left.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            status_left, 
            text="Status: Idle. Enter URL(s) and click 'Fetch Info'.", 
            anchor="w", 
            wraplength=400, 
            font=("Arial", 11),
            text_color=self.text_color
        )
        self.status_label.grid(row=0, column=0, padx=0, pady=(0, 10), sticky="ew")

    
        # Progress percentage text
        self.progress_text_label = ctk.CTkLabel(
            status_left, 
            text="0%", 
            font=("Arial", 10),
            text_color=self.text_secondary
        )
        self.progress_text_label.grid(row=2, column=0, padx=0, pady=0, sticky="w")
        
        # Right side: circular progress indicator
        status_right = ctk.CTkFrame(status_progress_frame.content_frame, fg_color="transparent")
        status_right.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.circular_progress = CircularProgress(
            status_right,
            size=130,
            fg_color=self.accent_color,
            bg_color=self._darken_color(self.card_bg, 0.9),
            text_color=self.text_color,
            glow_color=self.accent_color
        )
        self.circular_progress.pack(padx=10, pady=10)

        # --- 5. Log Output Section (Placeholder for now) ---
        self.log_textbox = ctk.CTkTextbox(self, state="disabled", wrap="word", font=MONOSPACE_FONT, height=150)
        self.log_textbox.grid(row=4, column=0, padx=15, pady=(7,15), sticky="nsew")

        # --- Initial UI State Call ---
        self.update_ui_for_type_change() # Set initial state of resolution dropdown
        self.check_if_getinfo_ready() # Set initial state of getinfo button

    def apply_futuristic_theme(self):       
                """Apply the futuristic theme to the application."""
                # Store theme colors as instance variables for easy access
                self.bg_color = FUTURISTIC_THEME["bg_color"]
                self.card_bg = FUTURISTIC_THEME["card_bg"]
                self.accent_color = FUTURISTIC_THEME["accent_primary"]
                self.accent_secondary = FUTURISTIC_THEME["accent_secondary"]
                self.text_color = FUTURISTIC_THEME["text_primary"]
                self.text_secondary = FUTURISTIC_THEME["text_secondary"]
                
                # Configure app background
                self.configure(fg_color=self.bg_color)
                
                # Set dark appearance mode
                ctk.set_appearance_mode("Dark")

                self.title(f"{APP_NAME} - {APP_VERSION}")
                self.geometry("850x750") # Adjusted for better layout
                self.minsize(700, 600)

    # --- Placeholder methods to be fully defined in subsequent chunks ---
    def check_if_getinfo_ready(self):
        # Basic check to enable getinfo button if URL entry has text
        if hasattr(self, 'url_entry') and hasattr(self, 'getinfo_button'): # Ensure widgets exist
            if self.url_entry.get("1.0", "end-1c").strip() and not self.is_operation_running:
                self.getinfo_button.configure(state="normal")
            else:
                self.getinfo_button.configure(state="disabled")

    def update_ui_for_type_change(self):
        # This will be expanded to handle resolution dropdown state
        if hasattr(self, 'download_type_var') and hasattr(self, 'resolution_dropdown'):
            is_video = self.download_type_var.get() == "Video"
            # Enable resolution dropdown only if video type AND info has been fetched
            # (This logic will be more robust later when self.current_fetched_info is used)
            if is_video and self.available_resolutions and len(self.available_resolutions) > 1:
                 self.resolution_dropdown.configure(state="normal", values=self.available_resolutions)
            elif is_video: # Video type, but no specific resolutions yet (e.g. before Get Info)
                 self.resolution_dropdown.configure(state="disabled", values=["Best"])
                 self.resolution_var.set("Best")
            else: # Audio
                self.resolution_dropdown.configure(state="disabled", values=["MP3 (Best)"])
                self.resolution_var.set("MP3 (Best)") # For audio, "Best" implies best audio quality for MP3
        self.check_download_button_state()

    def browse_path(self):
        """Opens a directory chooser and updates the path entry."""
        if self.is_operation_running:
            self.show_tooltip("Cannot change path during an operation.")
            return
        
        current_path = self.download_path_var.get()
        foldername = filedialog.askdirectory(initialdir=current_path, title="Select Download Folder")
        
        if foldername and foldername != current_path:
            self.download_path_var.set(foldername)
            self.log_message(f"Download path set to: {foldername}", level="info")
            self.check_download_button_state()
        elif not foldername:
             self.log_message("Path selection cancelled.", level="info")

    def update_ui_for_type_change(self):
        """Updates resolution dropdown state based on selected download type and fetched info."""
        if not hasattr(self, 'download_type_var'): return # Avoid error during init
        
        is_video = self.download_type_var.get() == "Video"
        
        if is_video:
            # If resolutions have been fetched (more than just 'Best')
            if self.available_resolutions and len(self.available_resolutions) > 1:
                self.resolution_dropdown.configure(state="normal", values=self.available_resolutions)
                # Try to keep the current selection if it's valid, otherwise default to 'Best'
                if self.resolution_var.get() not in self.available_resolutions:
                    self.resolution_var.set("Best")
            else: # Video type selected, but no specific resolutions fetched yet
                self.resolution_dropdown.configure(state="disabled", values=["Best"])
                self.resolution_var.set("Best")
        else: # Audio type selected
            self.resolution_dropdown.configure(state="disabled", values=["MP3 (Best)"])
            self.resolution_var.set("MP3 (Best)")
            
        self.check_download_button_state() # Update download button readiness

    def check_if_getinfo_ready(self):
        """Enables 'Fetch Info' button only if URL entry has text and no operation is running."""
        if hasattr(self, 'url_entry') and hasattr(self, 'getinfo_button'):
             can_fetch = bool(self.url_entry.get("1.0", "end-1c").strip()) and not self.is_operation_running
             self.getinfo_button.configure(state="normal" if can_fetch else "disabled")

    def check_download_button_state(self):
        """Enables 'Download' button based on prerequisites."""
        if not hasattr(self, 'url_entry'): return # Avoid error during init
        
        urls_present = bool(self.url_entry.get("1.0", "end-1c").strip())
        path_valid = bool(self.download_path_var.get() and os.path.isdir(self.download_path_var.get()))
        info_fetched = bool(self.current_fetched_info) # Check if info for *any* URL was successfully fetched

        can_download = False
        if urls_present and path_valid and not self.is_operation_running:
            if self.download_type_var.get() == "Audio":
                can_download = True # Audio download doesn't strictly need prior 'Get Info'
            elif self.download_type_var.get() == "Video":
                # Video needs info to have been fetched (implies resolutions populated)
                can_download = info_fetched and self.resolution_dropdown.cget("state") == "normal"

        self.download_button.configure(state="normal" if can_download else "disabled")


    def set_ui_state(self, is_running):
        """Disables/Enables UI elements during operations."""
        self.is_operation_running = is_running
        state = "disabled" if is_running else "normal"
        
        self.url_entry.configure(state="normal" if not is_running else "disabled")
        self.radio_video.configure(state=state)
        self.radio_audio.configure(state=state)
        self.browse_button.configure(state=state)
        
        # Always update button states based on conditions, even after enabling
        self.check_if_getinfo_ready()
        self.update_ui_for_type_change() # This implicitly calls check_download_button_state

    def update_status(self, message, progress=None, progress_text=None):
        """Updates the status label and optionally the progress bar (thread-safe)."""
        def _update():
            self.status_label.configure(text=f"Status: {message}")

        self.after(0, _update) # Schedule the update on the main GUI thread

    def log_message(self, msg, level="info", clear=False):
        """Appends a message to the log textbox (thread-safe). Handles basic cleaning."""
        # Simple level styling (could be more sophisticated)
        prefix = f"[{level.upper()}] " if level != "info" else ""
        
        # Clean potential ANSI escape codes left over
        clean_msg = re.sub(r'\x1b\[[0-9;?]*[a-zA-Z]', '', str(msg))

        def _log():
            self.log_textbox.configure(state="normal")
            if clear:
                self.log_textbox.delete("1.0", "end")
            self.log_textbox.insert("end", f"{prefix}{clean_msg}\n")
            self.log_textbox.configure(state="disabled")
            self.log_textbox.see("end") # Auto-scroll

        # Schedule the logging action in the main GUI thread
        self.after(0, _log)

    def show_error(self, title, message):
        """Displays an error message box (thread-safe)."""
        self.after(0, lambda: messagebox.showerror(title, message))

    def show_tooltip(self, message):
        """Rudimentary tooltip - display in status bar for a short time."""
        original_status = self.status_label.cget("text")
        self.status_label.configure(text=f"Info: {message}")
        # Reset status after a delay
        self.after(3000, lambda: self.status_label.configure(text=original_status))

    # --- Update the update_status method to update both progress indicators ---
    def update_status(self, message, progress=None, progress_text=None):
        """Updates the status label and optionally the progress indicators (thread-safe)."""
        def _update():
            self.status_label.configure(text=f"Status: {message}")
            if progress is not None:
                # Update both linear and circular progress
                self.circular_progress.set_progress(progress)
                
                # Update text percentage
                percent_text = progress_text or f"{int(progress * 100)}%"
                self.progress_text_label.configure(text=percent_text)
                
        self.after(0, _update)  # Schedule the update on the main GUI thread

    # --- Add Color Utility Methods to the App class ---
    def _darken_color(self, hex_color, factor=0.7):
        """Darken a hex color by a factor (0.0-1.0)."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        
        return f'#{r:02x}{g:02x}{b:02x}'

    def _lighten_color(self, hex_color, factor=1.3):
        """Lighten a hex color by a factor (>1.0)."""
        hex_color = hex_color.lstrip('#')
        r = min(255, int(int(hex_color[0:2], 16) * factor))
        g = min(255, int(int(hex_color[2:4], 16) * factor))
        b = min(255, int(int(hex_color[4:6], 16) * factor))
        
        return f'#{r:02x}{g:02x}{b:02x}'

    # --- Enhance other UI sections with the futuristic theme ---

    # For the URL Input Section:
    def create_url_input_section(self):
        url_input_frame = FuturisticCard(self, title="Video URL")
        url_input_frame.grid(row=0, column=0, padx=15, pady=(15, 7), sticky="ew")
        url_input_frame.content_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            url_input_frame.content_frame, 
            text="YouTube URL(s) (one per line for batch):", 
            font=("Roboto", 12),
            text_color=self.text_color
        ).grid(row=0, column=0, padx=10, pady=(5,5), sticky="w")

        self.url_entry = ctk.CTkTextbox(
            url_input_frame.content_frame, 
            height=100, 
            wrap="none", 
            font=("Arial", 12),
            fg_color=self._darken_color(self.card_bg, 0.9),
            border_color=self._lighten_color(self.card_bg, 1.2),
            border_width=1,
            text_color=self.text_color
        )
        self.url_entry.grid(row=1, column=0, padx=10, pady=(0,10), sticky="ew")
        self.url_entry.bind("<KeyRelease>", lambda event: self.check_if_getinfo_ready())

    # For the Action Buttons Section:
    def create_action_buttons(self):
        action_frame = FuturisticCard(self, title="Actions")
        action_frame.grid(row=2, column=0, padx=15, pady=7, sticky="ew")
        action_frame.content_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.getinfo_button = ctk.CTkButton(
            action_frame.content_frame, 
            text="Fetch Info & Formats", 
            command=self.start_getinfo_thread, 
            height=40, 
            font=("Roboto", 13, "bold"), 
            state="disabled",
            fg_color=self.accent_secondary,
            hover_color=self._lighten_color(self.accent_secondary, 1.2)
        )
        self.getinfo_button.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        
        self.download_button = ctk.CTkButton(
            action_frame.content_frame, 
            text="Download", 
            command=self.start_download_thread, 
            height=40, 
            font=("Roboto", 13, "bold"), 
            state="disabled",
            fg_color=self.accent_color,
            hover_color=self._lighten_color(self.accent_color, 1.2)
        )
        self.download_button.grid(row=0, column=1, padx=15, pady=15, sticky="ew")

    # For the Log Section:
    def create_log_section(self):
        log_frame = FuturisticCard(self, title="Activity Log")
        log_frame.grid(row=5, column=0, padx=15, pady=(7,15), sticky="nsew")
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.content_frame.grid_rowconfigure(0, weight=1)
        log_frame.content_frame.grid_columnconfigure(0, weight=1)
        
        self.log_textbox = ctk.CTkTextbox(
            log_frame.content_frame, 
            state="disabled", 
            wrap="word", 
            font=MONOSPACE_FONT, 
            height=150,
            fg_color=self._darken_color(self.card_bg, 0.9),
            text_color=self.text_secondary
        )
        self.log_textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # --- Enhanced Progress Hook with Dynamic Color Based on Status ---
    def progress_hook(self, d):
        """Enhanced progress hook with dynamic color effects."""
        # Get context if available (for batch downloads)
        ctx = getattr(self, 'current_download_context', None)
        file_progress_prefix = f"File {ctx['file_num']}/{ctx['total_files']}: " if ctx else ""

        if d['status'] == 'downloading':
            filename = d.get('filename', 'N/A').split(os.sep)[-1] # Get base filename
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded_bytes = d.get('downloaded_bytes')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            percent_str = d.get('_percent_str', '0.0%')
            
            try:
                # Clean percentage string (remove ANSI codes if any slip through)
                percent_str_cleaned = re.sub(r'\x1b\[[0-9;?]*[a-zA-Z]', '', percent_str)
                progress_value = float(percent_str_cleaned.replace('%','').strip()) / 100.0
                
                # Change color dynamically based on progress
                progress_color = self._blend_colors(self.accent_secondary, self.accent_color, progress_value)
                
                # Update circular progress color (if implemented)
                if hasattr(self, 'circular_progress'):
                    self.circular_progress.fg_color = progress_color
                    self.circular_progress.glow_color = progress_color
                
            except ValueError:
                progress_value = 0.0 # Default if parsing fails

            # Update status bar and progress bar (schedule on main thread)
            status_msg = f"{file_progress_prefix}Downloading '{filename}' - {percent_str.strip()} ({speed} ETA: {eta})"
            self.update_status(status_msg, progress=progress_value)

        elif d['status'] == 'finished':
            filename = d.get('filename', 'N/A').split(os.sep)[-1]
            self.log_message(f"{file_progress_prefix}Finished downloading '{filename}'")
            
            # Set success color for completed downloads
            if hasattr(self, 'circular_progress'):
                self.circular_progress.fg_color = FUTURISTIC_THEME["success_color"] 
                self.circular_progress.glow_color = FUTURISTIC_THEME["success_color"]
                
            # Update status
            self.update_status(f"{file_progress_prefix}Finished '{filename}'. Preparing next...", progress=1.0)

        elif d['status'] == 'error':
            filename = d.get('filename', 'N/A').split(os.sep)[-1]
            self.log_message(f"{file_progress_prefix}Error downloading '{filename}'. See logs above.", level="error")
            
            # Set error color
            if hasattr(self, 'circular_progress'):
                self.circular_progress.fg_color = FUTURISTIC_THEME["error_color"]
                self.circular_progress.glow_color = FUTURISTIC_THEME["error_color"]
                
            # Update status
            self.update_status(f"{file_progress_prefix}Error downloading '{filename}'. Check log.", progress=0)

    # Helper method to blend colors for progress effects
    def _blend_colors(self, color1, color2, ratio):
        """Blend two hex colors based on ratio."""
        # Convert hex to RGB
        color1 = color1.lstrip('#')
        color2 = color2.lstrip('#')
        
        r1, g1, b1 = int(color1[0:2], 16), int(color1[2:4], 16), int(color1[4:6], 16)
        r2, g2, b2 = int(color2[0:2], 16), int(color2[2:4], 16), int(color2[4:6], 16)
        
        # Blend
        r = int(r1 * (1-ratio) + r2 * ratio)
        g = int(g1 * (1-ratio) + g2 * ratio)
        b = int(b1 * (1-ratio) + b2 * ratio)
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"



    # --- Threading Wrappers ---

    def start_getinfo_thread(self):
        """Initiates the process of fetching video info in a background thread."""
        if self.is_operation_running:
            self.show_tooltip("An operation is already in progress.")
            return

        urls_text = self.url_entry.get("1.0", "end-1c").strip()
        if not urls_text:
            self.show_error("Input Error", "Please enter at least one YouTube URL.")
            return

        urls = [url.strip() for url in urls_text.splitlines() if url.strip() and ("youtube.com" in url or "youtu.be" in url)]
        if not urls:
            self.show_error("Input Error", "No valid YouTube URLs found.")
            return

        self.set_ui_state(is_running=True)
        self.current_fetched_info = {} # Clear previous info
        self.available_resolutions = ["Best"] # Reset resolutions
        self.update_ui_for_type_change() # Reflect reset in UI
        self.update_status("Fetching information...", progress=0)
        self.log_message(f"--- Fetching info for {len(urls)} URL(s) ---", clear=True)

        # Start the worker thread
        thread = threading.Thread(target=self.get_info_worker, args=(urls,), daemon=True)
        thread.start()

    def start_download_thread(self):
        """Initiates the download process in a background thread."""
        if self.is_operation_running:
            self.show_tooltip("An operation is already in progress.")
            return

        urls_to_download = list(self.current_fetched_info.keys()) # Download based on fetched info
        if not urls_to_download:
             # Allow download even if info wasn't fetched (e.g., for audio, or if user forces it)
             urls_text = self.url_entry.get("1.0", "end-1c").strip()
             urls_to_download = [url.strip() for url in urls_text.splitlines() if url.strip() and ("youtube.com" in url or "youtu.be" in url)]
             if not urls_to_download:
                 self.show_error("Download Error", "No URLs to download. Fetch info or enter URLs.")
                 return
             self.log_message("Warning: Downloading without pre-fetched info. Using best available formats.", level="warning")

        download_path = self.download_path_var.get()
        if not os.path.isdir(download_path):
             self.show_error("Download Error", f"Invalid download path: {download_path}")
             return

        download_type = self.download_type_var.get()
        selected_resolution = self.resolution_var.get()

        self.set_ui_state(is_running=True)
        self.update_status(f"Preparing to download {len(urls_to_download)} item(s)...", progress=0)
        self.log_message(f"--- Starting Download ---", clear=False) # Append to info log

        # Start the worker thread
        thread = threading.Thread(target=self.download_worker,
                                  args=(urls_to_download, download_path, download_type, selected_resolution),
                                  daemon=True)
        thread.start()


    # --- Worker Functions (run in threads) ---

    def get_info_worker(self, urls):
        """Fetches video/playlist information using yt-dlp."""
        ydl_opts = {
            'quiet': True,              # Suppress most console output (we use logger/hooks)
            'extract_flat': 'in_playlist', # Faster for playlists, get individual video info later if needed
            'skip_download': True,      # Don't download anything yet
            'logger': YdlLogger(self),  # Use our custom logger
            'forcejson': False,         # Get Python dict directly
            'ignoreerrors': True,       # Try to continue if one URL fails
            'noplaylist': True,
            # 'simulate': True,         # Useful for debugging without hitting network
        }
        
        all_resolutions_found = set(["Best"]) # Collect unique resolutions across all valid videos
        fetched_any_success = False

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                for i, url in enumerate(urls):
                    self.update_status(f"Processing URL {i+1}/{len(urls)}: {url.split('v=')[-1]}") # Show progress
                    try:
                        info_dict = ydl.extract_info(url, download=False)
                        
                        if not info_dict: # Handle cases where yt-dlp returns None for a bad URL
                            self.log_message(f"Failed to get info for URL: {url}", level="error")
                            continue
                            
                        entry_info = info_dict # Assume single video initially
                        is_playlist = info_dict.get('_type') == 'playlist'

                        if is_playlist:
                            # Log playlist info, but process entries individually if needed later for formats
                            pl_title = info_dict.get('title', 'Unknown Playlist')
                            num_entries = len(info_dict.get('entries', []))
                            self.log_message(f"Found Playlist: '{pl_title}' ({num_entries} items)")
                            # Store playlist marker, actual format extraction might happen during download
                            self.current_fetched_info[url] = {'title': pl_title, 'is_playlist': True, 'entries': num_entries, 'formats': []} # Placeholder formats
                            # For playlists, 'Best' is often the only practical resolution choice initially
                            # unless we fetch info for the *first* item specifically. Let's keep it simple for now.
                            fetched_any_success = True # Mark success even for playlist marker
                            
                        else: # Single video
                            title = entry_info.get('title', 'Unknown Title')
                            self.log_message(f"Found Video: '{title}'")
                            
                            formats = entry_info.get('formats', [])
                            video_formats = [
                                f for f in formats 
                                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('height') and f.get('ext') == 'mp4' # Prefer mp4 directly
                            ]
                            # Fallback if no combined mp4: check formats needing merge
                            if not video_formats:
                                video_formats = [
                                    f for f in formats 
                                    if f.get('vcodec') != 'none' and f.get('height')
                                ]

                            # Extract unique heights (resolutions)
                            vid_resolutions = sorted(list(set(f.get('height') for f in video_formats if f.get('height'))), reverse=True)
                            for res in vid_resolutions:
                                all_resolutions_found.add(f"{res}p")
                                
                            # Store info for this URL
                            self.current_fetched_info[url] = {'title': title, 'is_playlist': False, 'formats': formats} # Store raw formats
                            fetched_any_success = True

                    except yt_dlp.utils.DownloadError as e:
                        self.log_message(f"Error fetching info for {url}: {e}", level="error")
                    except Exception as e: # Catch other potential errors
                        self.log_message(f"Unexpected error processing {url}: {e}", level="error")
                        import traceback
                        self.log_message(traceback.format_exc(), level="debug") # Log stack trace for debugging

            # --- Post-processing after loop ---
            if fetched_any_success:
                # Update available resolutions list (sorted)
                self.available_resolutions = sorted(list(all_resolutions_found), key=lambda x: int(x[:-1]) if x != 'Best' and x[:-1].isdigit() else 0, reverse=True)
                self.log_message(f"Available video resolutions found: {', '.join(self.available_resolutions)}")
            else:
                 self.log_message("Failed to fetch information for any URL.", level="error")
                 self.available_resolutions = ["Best"] # Reset to default if all failed


        except Exception as e:
            self.log_message(f"Core yt-dlp error during info fetching: {e}", level="error")
            import traceback
            self.log_message(traceback.format_exc(), level="debug")
            self.show_error("Info Fetch Error", f"An error occurred: {e}")

        finally:
            # --- Final UI Updates (run on main thread) ---
            def _finalize_ui():
                self.set_ui_state(is_running=False) # Re-enable UI
                if fetched_any_success:
                    self.update_status("Information fetched successfully. Select options and click Download.", progress=1.0)
                else:
                    self.update_status("Info fetching finished with errors. Check log.", progress=0) # Indicate failure
                self.update_ui_for_type_change() # Update dropdown with new resolutions
                # check_download_button_state is called within update_ui_for_type_change

            self.after(0, _finalize_ui)


    # --- Placeholder for download worker (Chunk 3) ---
    def download_worker(self, urls, download_path, download_type, selected_resolution):
        self.log_message("Download worker placeholder...", level="debug")
        # Simulate work
        import time
        time.sleep(2)
        # Make sure to call set_ui_state(is_running=False) and update status in the finally block
        self.after(0, lambda: self.set_ui_state(is_running=False))
        self.after(0, lambda: self.update_status("Download placeholder finished.", progress=1.0))
        pass

    def download_worker(self, urls, download_path, download_type, selected_resolution):
        """Performs the actual download using yt-dlp options based on GUI selections."""
        
        total_files = len(urls)
        downloaded_count = 0
        errors_occurred = False

        try:
            for i, url in enumerate(urls):
                current_file_num = i + 1
                self.log_message(f"--- Starting download {current_file_num}/{total_files}: {url} ---")
                self.update_status(f"Preparing download {current_file_num}/{total_files}...", progress=0)
                
                # --- Construct yt-dlp Options ---
                output_template = os.path.join(download_path, '%(title)s [%(id)s].%(ext)s')
                
                ydl_opts = {
                    'logger': YdlLogger(self),
                    'progress_hooks': [self.progress_hook],
                    'ignoreerrors': True, # Continue batch even if one file fails
                    'outtmpl': output_template,
                    'format_sort': ['+res', '+fps', '+tbr'],
                    'noplaylist': True, # Prioritize resolution, mp4/m4a, then size
                    'postprocessors': [],
                    # 'ffmpeg_location': '/path/to/your/ffmpeg', # Optional: Uncomment and set if ffmpeg isn't in PATH
                    'verbose': False, # Keep output clean, rely on logger/hooks
                    'quiet': True,    # Suppress console output further
                    'no_warnings': True, # Suppress common warnings if desired
                }

                # --- Format Selection Logic ---
                if download_type == "Video":
                    resolution_query = ""
                    if selected_resolution != "Best":
                        try:
                             # Extract numeric height
                             height = int(selected_resolution.replace('p', ''))
                             # Flexible format selection: best video up to height + best audio, merged by yt-dlp
                             # Prefer mp4 container where possible
                             resolution_query = f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={height}]+bestaudio/best[height<={height}]/best'
                        except ValueError:
                             self.log_message(f"Invalid resolution format '{selected_resolution}'. Falling back to 'Best'.", level="warning")
                             resolution_query = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best' # Standard best if format invalid
                    else: # 'Best' selected
                        resolution_query = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best'
                    
                    ydl_opts['format'] = resolution_query
                    ydl_opts['postprocessors'].extend([
                        {'key': 'FFmpegMetadata', 'add_metadata': True}, # Embed metadata like title, artist (uploader)
                        {'key': 'EmbedThumbnail', 'already_have_thumbnail': False}, # Embed thumbnail as cover art
                        # yt-dlp often merges to mp4 automatically with the format string above.
                        # Explicit conversion might be needed only in specific cases.
                        # {'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}, 
                    ])
                    
                elif download_type == "Audio":
                    ydl_opts['format'] = 'bestaudio/best' # Select best audio stream
                    ydl_opts['postprocessors'].extend([
                         {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}, # Convert to MP3, 192kbps default
                         {'key': 'FFmpegMetadata', 'add_metadata': True},
                         {'key': 'EmbedThumbnail', 'already_have_thumbnail': False},
                    ])

                # --- Execute Download for current URL ---
                try:
                    # Store context for progress hook
                    self.current_download_context = {'file_num': current_file_num, 'total_files': total_files}
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                    # Check if an error occurred *during* this specific download via hooks/logger?
                    # For simplicity, we rely on the outer try/except for now.
                    downloaded_count += 1
                    self.log_message(f"--- Finished download {current_file_num}/{total_files} ---")

                except yt_dlp.utils.DownloadError as e:
                    self.log_message(f"Failed to download {url}: {e}", level="error")
                    errors_occurred = True
                except Exception as e: # Catch unexpected errors during download for one file
                    self.log_message(f"Unexpected error downloading {url}: {e}", level="error")
                    import traceback
                    self.log_message(traceback.format_exc(), level="debug")
                    errors_occurred = True
                finally:
                    self.current_download_context = None # Clear context


        except Exception as e: # Catch broader errors (e.g., during option setup)
            self.log_message(f"Core yt-dlp error during download process: {e}", level="error")
            import traceback
            self.log_message(traceback.format_exc(), level="debug")
            self.show_error("Download Error", f"A critical error occurred: {e}")
            errors_occurred = True

        finally:
            # --- Final UI Updates after all downloads (run on main thread) ---
            def _finalize_ui():
                final_message = ""
                if downloaded_count == total_files:
                    final_message = f"All {total_files} item(s) downloaded successfully."
                    self.update_status(final_message, progress=1.0)
                elif downloaded_count > 0:
                     final_message = f"Finished batch. Downloaded {downloaded_count}/{total_files} item(s) with some errors."
                     self.update_status(final_message, progress=1.0) # Show completion, but indicate errors
                else: # 0 downloaded
                     final_message = "Download failed for all items. Check log for details."
                     self.update_status(final_message, progress=0) # Show failure
                
                self.log_message(f"--- Download Process Ended: {final_message} ---")
                self.set_ui_state(is_running=False) # Re-enable UI

            self.after(0, _finalize_ui)


    def progress_hook(self, d):
        """Callback function executed by yt-dlp during download progress."""
        
        # Get context if available (for batch downloads)
        ctx = getattr(self, 'current_download_context', None)
        file_progress_prefix = f"File {ctx['file_num']}/{ctx['total_files']}: " if ctx else ""

        if d['status'] == 'downloading':
            filename = d.get('filename', 'N/A').split(os.sep)[-1] # Get base filename
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded_bytes = d.get('downloaded_bytes')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            percent_str = d.get('_percent_str', '0.0%')
            
            try:
                # Clean percentage string (remove ANSI codes if any slip through)
                percent_str_cleaned = re.sub(r'\x1b\[[0-9;?]*[a-zA-Z]', '', percent_str)
                progress_value = float(percent_str_cleaned.replace('%','').strip()) / 100.0
            except ValueError:
                progress_value = 0.0 # Default if parsing fails

            # Update status bar and progress bar (schedule on main thread)
            status_msg = f"{file_progress_prefix}Downloading '{filename}' - {percent_str.strip()} ({speed} ETA: {eta})"
            self.update_status(status_msg, progress=progress_value)

        elif d['status'] == 'finished':
            filename = d.get('filename', 'N/A').split(os.sep)[-1]
            self.log_message(f"{file_progress_prefix}Finished downloading '{filename}'")
            # Optional: Briefly show finished status before next file starts or final message appears
            self.update_status(f"{file_progress_prefix}Finished '{filename}'. Preparing next...", progress=1.0) 
            # Reset progress bar slightly *before* next file (or keep at 1.0 if it's the last)
            # The download_worker loop handles the main status updates between files.

        elif d['status'] == 'error':
            filename = d.get('filename', 'N/A').split(os.sep)[-1]
            self.log_message(f"{file_progress_prefix}Error downloading '{filename}'. See logs above.", level="error")
            # Optionally update status bar to reflect the error briefly
            self.update_status(f"{file_progress_prefix}Error downloading '{filename}'. Check log.", progress=0) # Reset progress bar on error? Or leave as is?

# --- Main Execution Block ---
if __name__ == "__main__":
    # Add a check for FFmpeg (optional but helpful)
    ffmpeg_path = None
    try:
        # Try getting path using shutil (Python 3.3+)
        from shutil import which
        ffmpeg_path = which('ffmpeg')
    except ImportError:
        # Basic check in common locations or PATH (less reliable)
        pass 

    if not ffmpeg_path and not os.path.exists('ffmpeg.exe'): # Also check current dir
         print("WARNING: FFmpeg executable not found in PATH or current directory.")
         print("         MP3 conversion and merging some video formats might fail.")
         print("         Download FFmpeg from https://ffmpeg.org/download.html")
         print("         Place ffmpeg.exe in this directory or add its 'bin' folder to your system PATH.")
         # Could show a messagebox if GUI is already initializable, but this runs before App()
         # For simplicity, print warning to console where the script is launched.

    # --- Create and run the application ---
    app = App()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        print("\nApplication closed by user.")