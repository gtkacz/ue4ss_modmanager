from pathlib import Path

import customtkinter as ctk
from loguru import logger
from PIL import Image

from src.common.mod import UE4SSMod
from src.common.mod_manager import UE4SSModManager


class UE4SSModManagerGUI(ctk.CTk):
	"""A GUI for managing UE4SS mods."""

	def __init__(
		self,
		mod_manager: UE4SSModManager,
		logo_path: Path | None = None,
		icon_path: Path | None = None,
	) -> None:
		"""Initialize the UE4SSModManagerGUI."""
		super().__init__()

		self.mod_manager = mod_manager
		self.initial_mod_states = {mod.name: mod.enabled for mod in mod_manager.mods}
		self.mod_checkboxes = {}
		self.show_native_warning_shown = False

		self._setup_window(icon_path)
		self._setup_theme()

		self.main_frame = ctk.CTkFrame(self)
		self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)

		self._create_header(logo_path)
		self._create_search_filter()
		self._create_controls()
		self._create_mod_list()
		self._create_save_options()
		self._create_status_bar()

		self.populate_mod_list()
		self.update_save_button_state()

	def _setup_window(self, icon_path: Path | None = None) -> None:
		"""Configure the window properties."""
		self.title("UE4SS Mod Manager")

		# Make window size dynamic based on screen size
		screen_width = self.winfo_screenwidth()
		screen_height = self.winfo_screenheight()
		window_width = int(screen_width * 0.6)
		window_height = int(screen_height * 0.6)
		self.minsize(window_width, window_height)

		self.attributes("-topmost", True)
		self.after(100, lambda: self.attributes("-topmost", False))
		self.center_window()

		if icon_path and icon_path.exists():
			try:
				self.iconbitmap(icon_path)
				logger.debug(f"Set window icon: {icon_path}")
			except Exception as e:
				logger.error(f"Failed to set window icon: {e}")

	@staticmethod
	def _setup_theme() -> None:
		"""Set up the application theme."""
		ctk.set_appearance_mode("dark")
		ctk.set_default_color_theme("blue")

	def _create_header(self, logo_path: Path | None = None) -> None:
		"""Create the header with logo or title."""
		if logo_path and logo_path.exists():
			try:
				pil_image = Image.open(logo_path)
				logo_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(180, 54))
				self.logo_label = ctk.CTkLabel(self.main_frame, image=logo_image, text="")
				self.logo_label.pack(pady=(0, 15))
				logger.debug(f"Set logo image: {logo_path}")
			except Exception as e:
				logger.error(f"Failed to load logo image: {e}")
				self._create_title_label()
		else:
			self._create_title_label()

		self.header_frame = ctk.CTkFrame(self.main_frame)
		self.header_frame.pack(fill="x", padx=10, pady=(0, 5))
		self.separator1 = ctk.CTkFrame(self.main_frame, height=1, fg_color="gray30")
		self.separator1.pack(fill="x", padx=10, pady=3)

	def _create_title_label(self) -> None:
		"""Create the title label if no logo is available."""
		self.title_label = ctk.CTkLabel(
			self.main_frame,
			text="UE4SS Mod Manager",
			font=ctk.CTkFont(size=24, weight="bold"),
		)
		self.title_label.pack(pady=(0, 15))

	def _create_search_filter(self) -> None:
		"""Create the search filter components."""
		self.list_label = ctk.CTkLabel(
			self.header_frame,
			text="Available Mods:",
			font=ctk.CTkFont(size=16, weight="bold"),
		)
		self.list_label.pack(side="left", padx=10, pady=5)

		self.search_var = ctk.StringVar()
		self.search_var.trace_add("write", lambda *_: self.filter_mods())
		self.search_entry = ctk.CTkEntry(
			self.header_frame,
			placeholder_text="Search mods...",
			textvariable=self.search_var,
			width=200,
		)
		self.search_entry.pack(side="left", padx=10, pady=5)

		self.show_native_mods_var = ctk.BooleanVar(value=False)
		self.show_native_switch = ctk.CTkSwitch(
			self.header_frame,
			text="Show Native Mods",
			variable=self.show_native_mods_var,
			onvalue=True,
			offvalue=False,
			command=self.toggle_native_mods_visibility,
		)
		self.show_native_switch.pack(side="right", padx=10, pady=5)

	def _create_controls(self) -> None:
		"""Create the control buttons section."""
		self.controls_frame = ctk.CTkFrame(self.main_frame)
		self.controls_frame.pack(fill="x", padx=10, pady=(0, 5))

		self.toggle_all_var = ctk.BooleanVar(value=False)
		self.toggle_all_checkbox = ctk.CTkCheckBox(
			self.controls_frame,
			text="Toggle All",
			variable=self.toggle_all_var,
			onvalue=True,
			offvalue=False,
			command=self.toggle_all_mods,
			width=24,
		)
		self.toggle_all_checkbox.pack(side="left", padx=10, pady=5)

		self.refresh_button = ctk.CTkButton(
			self.controls_frame,
			text="Refresh",
			command=self.refresh_mods,
			width=80,
		)
		self.refresh_button.pack(side="right", padx=5, pady=5)

		self.reset_button = ctk.CTkButton(
			self.controls_frame,
			text="Reset",
			command=self.reset_mods,
			width=80,
		)
		self.reset_button.pack(side="right", padx=5, pady=5)

	def _create_mod_list(self) -> None:
		"""Create the scrollable mod list area."""
		self.mod_list_frame = ctk.CTkScrollableFrame(self.main_frame)
		self.mod_list_frame.pack(fill="both", expand=True, padx=10, pady=8)
		self.separator2 = ctk.CTkFrame(self.main_frame, height=1, fg_color="gray30")
		self.separator2.pack(fill="x", padx=10, pady=3)

	def _create_save_options(self) -> None:
		"""Create the save options section."""
		self.save_options_frame = ctk.CTkFrame(self.main_frame)
		self.save_options_frame.pack(fill="x", padx=10, pady=(8, 0))

		self.save_enabled_txt_var = ctk.BooleanVar(value=True)
		self.save_enabled_txt = ctk.CTkSwitch(
			self.save_options_frame,
			text="Save enabled.txt",
			variable=self.save_enabled_txt_var,
			onvalue=True,
			offvalue=False,
			command=self.update_save_button_state,
			width=24,
		)
		self.save_enabled_txt.pack(side="left", padx=10, pady=8)

		self.save_mods_json_var = ctk.BooleanVar(value=False)
		self.save_mods_json = ctk.CTkSwitch(
			self.save_options_frame,
			text="Save mods.json",
			variable=self.save_mods_json_var,
			onvalue=True,
			offvalue=False,
			command=lambda: self.handle_save_option_change(self.save_mods_json_var),
			width=24,
		)
		self.save_mods_json.pack(side="left", padx=10, pady=8)

		self.save_mods_txt_var = ctk.BooleanVar(value=False)
		self.save_mods_txt = ctk.CTkSwitch(
			self.save_options_frame,
			text="Save mods.txt",
			variable=self.save_mods_txt_var,
			onvalue=True,
			offvalue=False,
			command=lambda: self.handle_save_option_change(self.save_mods_txt_var),
			width=24,
		)
		self.save_mods_txt.pack(side="left", padx=10, pady=8)

		self.spacer = ctk.CTkLabel(self.save_options_frame, text="")
		self.spacer.pack(side="left", fill="x", expand=True)

		self.save_button = ctk.CTkButton(
			self.save_options_frame, text="Save Changes", command=self.save_changes, width=120, state="disabled"
		)
		self.save_button.pack(side="right", padx=10, pady=8)

	def _create_status_bar(self) -> None:
		"""Create the status bar at the bottom."""
		self.status_bar = ctk.CTkLabel(
			self.main_frame,
			text=f"Loaded {len(self.mod_manager.mods)} mods",
			font=ctk.CTkFont(size=12),
		)
		self.status_bar.pack(pady=(8, 0), anchor="w")

	def toggle_native_mods_visibility(self) -> None:
		"""Toggle visibility of native mods with a warning."""
		if self.show_native_mods_var.get() and not self.show_native_warning_shown:
			self.show_warning(
				"Warning",
				"You should be absolutely sure about toggling UE4SS native mods. "
				"Disabling essential native mods may break UE4SS functionality.",
				self.populate_mod_list,
				lambda: self.show_native_mods_var.set(False),
			)
			self.show_native_warning_shown = True
		else:
			self.populate_mod_list()

	def update_save_button_state(self) -> None:
		"""Update the save button state based on save options."""
		if (
			not (self.save_enabled_txt_var.get() or self.save_mods_json_var.get() or self.save_mods_txt_var.get())
			or self.initial_mod_states == self.get_mod_status()
		):
			self.save_button.configure(state="disabled")
		else:
			self.save_button.configure(state="normal")

	def refresh_mods(self) -> None:
		"""Reload mods from disk."""
		try:
			self.mod_manager.mods = self.mod_manager.load_mods()
			self.initial_mod_states = {mod.name: mod.enabled for mod in self.mod_manager.mods}
			self.populate_mod_list()

			self.status_bar.configure(text=f"Refreshed {len(self.mod_manager.mods)} mods")

		except Exception as e:
			logger.exception(f"Error refreshing mods: {e}")
			self.show_error("Error Refreshing Mods", str(e))

	def populate_mod_list(self) -> None:
		"""Populate the mod list with checkboxes for each mod."""
		try:
			for widget in self.mod_list_frame.winfo_children():
				widget.destroy()

			self.mod_checkboxes = {}

			for mod in self.mod_manager.mods:
				if not self.show_native_mods_var.get() and mod.is_native:
					continue

				frame = ctk.CTkFrame(self.mod_list_frame)
				frame.pack(fill="x", padx=5, pady=2)

				checkbox = ctk.CTkCheckBox(
					frame,
					text=f"{'[NATIVE] ' if mod.is_native else ''}{mod.name}",
					variable=ctk.BooleanVar(value=mod.enabled),
					command=self.update_save_button_state,
					onvalue=True,
					offvalue=False,
					width=24,
				)
				checkbox.pack(side="left", padx=10, pady=5)

				script_count = ctk.CTkLabel(
					frame,
					text=f"{len(mod.scripts)} script(s)",
					font=ctk.CTkFont(size=12),
					text_color="gray",
				)
				script_count.pack(side="right", padx=10, pady=5)

				self.mod_checkboxes[mod.name] = checkbox

			visible_count = sum(
				1 for mod in self.mod_manager.mods if not mod.is_native or self.show_native_mods_var.get()
			)
			enabled_count = sum(
				1
				for mod in self.mod_manager.mods
				if mod.enabled and (not mod.is_native or self.show_native_mods_var.get())
			)
			self.status_bar.configure(text=f"Showing {visible_count} mods ({enabled_count} enabled)")

		except Exception as e:
			logger.exception(f"Error saving changes: {e}")
			self.show_error("Error Saving Changes", str(e))

	def handle_save_option_change(self, var: ctk.BooleanVar) -> None:
		"""Handle changes to save options with warnings."""
		if var.get():
			self.show_warning(
				"Warning",
				"Are you absolutely sure about writing to these files? "
				"This can potentially break your UE4SS installation.",
				lambda: None,  # Do nothing on OK
				lambda: var.set(False),  # Reset on Cancel
			)

		self.update_save_button_state()

	def reset_mods(self) -> None:
		"""Reset mods to their initial states when the app was launched."""
		try:
			for mod_name, checkbox in self.mod_checkboxes.items():
				initial_state = self.initial_mod_states.get(mod_name, False)
				if initial_state:
					checkbox.select()
				else:
					checkbox.deselect()

			self.status_bar.configure(text="Mods reset to initial state. Click Save to apply.")

		except Exception as e:
			logger.exception(f"Error resetting mods: {e}")
			self.show_error("Error Resetting Mods", str(e))

	def show_warning(self, title: str, message: str, on_ok: callable, on_cancel: callable) -> None:
		"""Show a warning popup with OK and Cancel buttons."""
		warning_window = ctk.CTkToplevel(self)
		warning_window.title(title)
		warning_window.geometry("450x200")
		warning_window.transient(self)
		warning_window.grab_set()
		warning_window.attributes("-topmost", True)
		warning_window.after(100, lambda: warning_window.attributes("-topmost", False))
		warning_window.update_idletasks()
		width = warning_window.winfo_width()
		height = warning_window.winfo_height()
		x = (warning_window.winfo_screenwidth() // 2) - (width // 2)
		y = (warning_window.winfo_screenheight() // 2) - (height // 2)
		warning_window.geometry(f"{width}x{height}+{x}+{y}")

		frame = ctk.CTkFrame(warning_window)
		frame.pack(fill="both", expand=True, padx=20, pady=20)

		warning_label = ctk.CTkLabel(frame, text=message, wraplength=410, justify="left")
		warning_label.pack(padx=10, pady=(10, 20))

		button_frame = ctk.CTkFrame(frame)
		button_frame.pack(fill="x", padx=10, pady=(0, 10))

		cancel_button = ctk.CTkButton(
			button_frame,
			text="Cancel",
			command=lambda: (on_cancel(), warning_window.destroy()),
			width=100,
		)
		cancel_button.pack(side="left", padx=10, pady=10)

		ok_button = ctk.CTkButton(
			button_frame,
			text="OK",
			command=lambda: (on_ok(), warning_window.destroy()),
			width=100,
		)
		ok_button.pack(side="right", padx=10, pady=10)

	def get_mod_status(self) -> dict[str, bool]:
		"""
		Get the current status of all mods from the checkboxes.

		Returns:
			A mapping with mod names as keys and their enabled status as values.
		"""
		try:
			mod_status = {}
			for mod in self.mod_manager.mods:
				checkbox = self.mod_checkboxes.get(mod.name)
				if checkbox:
					mod_status[mod.name] = checkbox.get()

		except Exception as e:
			logger.exception(f"Error getting mod status: {e}")
			self.show_error("Error Getting Mod Status", str(e))
			return {}

		else:
			return mod_status

	def get_mod_objects(self) -> list[UE4SSMod]:
		"""
		Get the current status of all mods from the checkboxes.

		Returns:
			A list of UE4SSMod objects with updated enabled status
		"""
		try:
			updated_mods = []

			for mod in self.mod_manager.mods:
				checkbox = self.mod_checkboxes.get(mod.name)

				if checkbox:
					logger.debug(f"Mod: {mod.name}, Enabled: {checkbox.get()}")
					updated_mod = UE4SSMod(name=mod.name, path=mod.path, enabled=checkbox.get(), scripts=mod.scripts)
					updated_mods.append(updated_mod)

		except Exception as e:
			logger.exception(f"Error saving changes: {e}")
			self.show_error("Error Saving Changes", str(e))
			return []

		else:
			return updated_mods

	def save_changes(self) -> None:
		"""Save the changes to the mods."""
		try:
			updated_mods = self.get_mod_objects()
			self.mod_manager.parse_mods(
				mods=updated_mods,
				save_enabled_txt=self.save_enabled_txt_var.get(),
				save_mods_json=self.save_mods_json_var.get(),
				save_mods_txt=self.save_mods_txt_var.get(),
			)

			enabled_count = sum(1 for mod in updated_mods if mod.enabled)
			self.status_bar.configure(text=f"Changes saved. {enabled_count}/{len(updated_mods)} mods enabled.")

			self.initial_mod_states = self.get_mod_status()
			self.update_save_button_state()

		except Exception as e:
			logger.exception(f"Error saving changes: {e}")
			self.show_error("Error Saving Changes", str(e))

	def toggle_all_mods(self) -> None:
		"""Toggle all mods on or off based on the Toggle All checkbox."""
		try:
			new_state = self.toggle_all_var.get()

			for checkbox in self.mod_checkboxes.values():
				if new_state:
					checkbox.select()
				else:
					checkbox.deselect()

			self.status_bar.configure(text=f"All mods {'enabled' if new_state else 'disabled'}. Click Save to apply.")

		except Exception as e:
			logger.exception(f"Error toggling mods: {e}")
			self.show_error("Error Toggling Mods", str(e))

	def filter_mods(self) -> None:
		"""Filter mods based on search text."""
		search_text = self.search_var.get().lower()

		for mod_name, checkbox in self.mod_checkboxes.items():
			parent_frame = checkbox.master
			if search_text in mod_name.lower():
				parent_frame.pack(fill="x", padx=5, pady=2)
			else:
				parent_frame.pack_forget()

	def center_window(self) -> None:
		"""Center the window on the screen."""
		self.update_idletasks()
		width = self.winfo_width()
		height = self.winfo_height()
		x = (self.winfo_screenwidth() // 2) - (width // 2)
		y = (self.winfo_screenheight() // 2) - (height // 2)
		self.geometry(f"{width}x{height}+{x}+{y}")

	def show_error(self, title: str, message: str) -> None:
		"""Show an error popup with the given title and message."""
		error_window = ctk.CTkToplevel(self)
		error_window.title(title)
		error_window.geometry("400x200")
		error_window.transient(self)
		error_window.grab_set()
		error_window.attributes("-topmost", True)
		error_window.after(100, lambda: error_window.attributes("-topmost", False))
		error_window.update_idletasks()
		width = error_window.winfo_width()
		height = error_window.winfo_height()
		x = (error_window.winfo_screenwidth() // 2) - (width // 2)
		y = (error_window.winfo_screenheight() // 2) - (height // 2)
		error_window.geometry(f"{width}x{height}+{x}+{y}")

		frame = ctk.CTkFrame(error_window)
		frame.pack(fill="both", expand=True, padx=20, pady=20)

		error_label = ctk.CTkLabel(frame, text=message, wraplength=360, justify="left")
		error_label.pack(padx=10, pady=(10, 20))

		ok_button = ctk.CTkButton(frame, text="OK", command=error_window.destroy, width=100)
		ok_button.pack(pady=(0, 10))


def start_gui(mod_manager: UE4SSModManager, logo_path: Path | None = None, icon_path: Path | None = None) -> None:
	"""
	Start the GUI with the given mod manager.

	Args:
		mod_manager: An instance of UE4SSModManager
		logo_path: Path to the logo image file
		icon_path: Path to the icon file (.ico)
	"""
	app = UE4SSModManagerGUI(mod_manager, logo_path, icon_path)
	app.mainloop()
