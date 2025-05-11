from pathlib import Path

import customtkinter as ctk
from PIL import Image

from src.common.mod import UE4SSMod
from src.common.mod_manager import UE4SSModManager


class ModManagerGUI(ctk.CTk):
	"""A GUI for managing UE4SS mods."""

	def __init__(
		self,
		mod_manager: UE4SSModManager,
		logo_path: Path | None = None,
		icon_path: Path | None = None,
	) -> None:
		"""
		Initialize the ModManagerGUI.

		Args:
			mod_manager: An instance of UE4SSModManager
			logo_path: Path to the logo image file
			icon_path: Path to the icon file (.ico)
		"""
		super().__init__()

		self.mod_manager = mod_manager

		self.title("UE4SS Mod Manager")
		self.geometry("600x500")
		self.minsize(400, 300)

		if icon_path and icon_path.exists():
			try:
				self.iconbitmap(icon_path)
				# logger.debug(f"Set window icon: {icon_path}")
			except Exception:
				pass
				# logger.error(f"Failed to set window icon: {e}")

		ctk.set_appearance_mode("dark")
		ctk.set_default_color_theme("blue")

		self.main_frame = ctk.CTkFrame(self)
		self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

		if logo_path and logo_path.exists():
			try:
				pil_image = Image.open(logo_path)
				logo_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(200, 60))

				self.logo_label = ctk.CTkLabel(self.main_frame, image=logo_image, text="")
				self.logo_label.pack(pady=(0, 20))
				# logger.debug(f"Set logo image: {logo_path}")
			except Exception:
				# logger.error(f"Failed to load logo image: {e}")
				self.title_label = ctk.CTkLabel(
					self.main_frame,
					text="UE4SS Mod Manager",
					font=ctk.CTkFont(size=24, weight="bold"),
				)
				self.title_label.pack(pady=(0, 20))
		else:
			self.title_label = ctk.CTkLabel(
				self.main_frame,
				text="UE4SS Mod Manager",
				font=ctk.CTkFont(size=24, weight="bold"),
			)
			self.title_label.pack(pady=(0, 20))

		self.mod_list_frame = ctk.CTkScrollableFrame(self.main_frame)
		self.mod_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

		self.mod_checkboxes = {}

		self.populate_mod_list()

		self.save_options_frame = ctk.CTkFrame(self.main_frame)
		self.save_options_frame.pack(fill="x", padx=10, pady=(10, 0))

		self.save_enabled_txt_var = ctk.BooleanVar(value=True)
		self.save_enabled_txt = ctk.CTkCheckBox(
			self.save_options_frame,
			text="Save enabled.txt",
			variable=self.save_enabled_txt_var,
			onvalue=True,
			offvalue=False,
			command=self.update_save_button_state,  # Add callback
		)
		self.save_enabled_txt.pack(side="left", padx=10, pady=10)

		self.save_mods_json_var = ctk.BooleanVar(value=False)
		self.save_mods_json = ctk.CTkCheckBox(
			self.save_options_frame,
			text="Save mods.json",
			variable=self.save_mods_json_var,
			onvalue=True,
			offvalue=False,
			command=self.update_save_button_state,  # Add callback
		)
		self.save_mods_json.pack(side="left", padx=10, pady=10)

		self.save_mods_txt_var = ctk.BooleanVar(value=False)
		self.save_mods_txt = ctk.CTkCheckBox(
			self.save_options_frame,
			text="Save mods.txt",
			variable=self.save_mods_txt_var,
			onvalue=True,
			offvalue=False,
			command=self.update_save_button_state,  # Add callback
		)
		self.save_mods_txt.pack(side="left", padx=10, pady=10)

		self.button_frame = ctk.CTkFrame(self.main_frame)
		self.button_frame.pack(fill="x", padx=10, pady=(10, 0))

		self.toggle_all_button = ctk.CTkButton(
			self.button_frame,
			text="Toggle All",
			command=self.toggle_all_mods,
			width=120,
		)
		self.toggle_all_button.pack(side="left", padx=10, pady=10)

		self.spacer = ctk.CTkLabel(self.button_frame, text="")
		self.spacer.pack(side="left", fill="x", expand=True)

		self.save_button = ctk.CTkButton(self.button_frame, text="Save Changes", command=self.save_changes, width=120)
		self.save_button.pack(side="right", padx=10, pady=10)

		self.status_bar = ctk.CTkLabel(
			self.main_frame,
			text=f"Loaded {len(self.mod_manager.mods)} mods",
			font=ctk.CTkFont(size=12),
		)
		self.status_bar.pack(pady=(50, 0), anchor="w")

		self.update_save_button_state()

	def update_save_button_state(self) -> None:
		"""Update the save button state based on save options."""
		if not (self.save_enabled_txt_var.get() or self.save_mods_json_var.get() or self.save_mods_txt_var.get()):
			self.save_button.configure(state="disabled")
		else:
			self.save_button.configure(state="normal")

	def populate_mod_list(self) -> None:
		"""Populate the mod list with checkboxes for each mod."""
		for widget in self.mod_list_frame.winfo_children():
			widget.destroy()

		self.mod_checkboxes = {}

		for mod in self.mod_manager.mods:
			frame = ctk.CTkFrame(self.mod_list_frame)
			frame.pack(fill="x", padx=5, pady=2)

			checkbox = ctk.CTkCheckBox(
				frame,
				text=mod.name,
				variable=ctk.BooleanVar(value=mod.enabled),
				onvalue=True,
				offvalue=False,
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

	def get_mod_status(self) -> list[UE4SSMod]:
		"""
		Get the current status of all mods from the checkboxes.

		Returns:
			A list of UE4SSMod objects with updated enabled status
		"""
		updated_mods = []

		for mod in self.mod_manager.mods:
			checkbox = self.mod_checkboxes.get(mod.name)
			if checkbox:
				updated_mod = UE4SSMod(name=mod.name, path=mod.path, enabled=checkbox.get(), scripts=mod.scripts)
				updated_mods.append(updated_mod)

		return updated_mods

	def save_changes(self) -> None:
		"""Save the changes to the mods."""
		try:
			updated_mods = self.get_mod_status()
			self.mod_manager.parse_mods(
				mods=updated_mods,
				save_enabled_txt=self.save_enabled_txt_var.get(),
				save_mods_json=self.save_mods_json_var.get(),
				save_mods_txt=self.save_mods_txt_var.get(),
			)

			enabled_count = sum(1 for mod in updated_mods if mod.enabled)
			self.status_bar.configure(text=f"Changes saved. {enabled_count}/{len(updated_mods)} mods enabled.")

			# logger.info(f"Saved changes to {len(updated_mods)} mods.")

		except Exception as e:
			# logger.exception(f"Error saving changes: {e}")
			self.show_error("Error Saving Changes", str(e))

	def toggle_all_mods(self) -> None:
		"""Toggle all mods on or off."""
		enabled_count = sum(1 for checkbox in self.mod_checkboxes.values() if checkbox.get())
		total_count = len(self.mod_checkboxes)
		new_state = enabled_count <= total_count / 2

		for checkbox in self.mod_checkboxes.values():
			checkbox.select() if new_state else checkbox.deselect()

		self.status_bar.configure(text=f"All mods {'enabled' if new_state else 'disabled'}. Click Save to apply.")

	def show_error(self, title: str, message: str) -> None:
		"""Show an error popup with the given title and message."""
		error_window = ctk.CTkToplevel(self)
		error_window.title(title)
		error_window.geometry("400x200")
		error_window.transient(self)
		error_window.grab_set()

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
	app = ModManagerGUI(mod_manager, logo_path, icon_path)
	app.mainloop()
