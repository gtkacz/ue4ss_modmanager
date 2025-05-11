import customtkinter as ctk
from loguru import logger

from src.common.mod import UE4SSMod
from src.common.mod_manager import UE4SSModManager


class ModManagerGUI(ctk.CTk):
	"""A GUI for managing UE4SS mods."""

	def __init__(self, mod_manager: UE4SSModManager) -> None:
		"""
		Initialize the ModManagerGUI.

		Args:
			mod_manager: An instance of UE4SSModManager
		"""
		super().__init__()

		self.mod_manager = mod_manager

		self.title("UE4SS Mod Manager")
		self.geometry("600x500")
		self.minsize(400, 300)

		ctk.set_appearance_mode("dark")
		ctk.set_default_color_theme("blue")

		self.main_frame = ctk.CTkFrame(self)
		self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

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
		self.status_bar.pack(pady=(10, 0), anchor="w")

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
		updated_mods = self.get_mod_status()
		self.mod_manager.parse_mods(updated_mods)

		enabled_count = sum(1 for mod in updated_mods if mod.enabled)
		self.status_bar.configure(text=f"Changes saved. {enabled_count}/{len(updated_mods)} mods enabled.")

		logger.info(f"Saved changes to {len(updated_mods)} mods.")

	def toggle_all_mods(self) -> None:
		"""Toggle all mods on or off."""
		enabled_count = sum(1 for checkbox in self.mod_checkboxes.values() if checkbox.get())
		total_count = len(self.mod_checkboxes)
		new_state = enabled_count <= total_count / 2

		for checkbox in self.mod_checkboxes.values():
			checkbox.select() if new_state else checkbox.deselect()

		self.status_bar.configure(text=f"All mods {'enabled' if new_state else 'disabled'}. Click Save to apply.")


def start_gui(mod_manager: UE4SSModManager) -> None:
	"""
	Start the GUI with the given mod manager.

	Args:
		mod_manager: An instance of UE4SSModManager
	"""
	app = ModManagerGUI(mod_manager)
	app.mainloop()
