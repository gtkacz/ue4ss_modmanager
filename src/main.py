#!/usr/bin/env python3
import sys
from pathlib import Path

from src.common.exceptions import InvalidModException, InvalidModFolderException
from src.common.gui import start_gui
from src.common.mod_manager import UE4SSModManager


def find_mods_folder() -> Path:
	"""
	Find the mods folder path.

	Returns:
		The path to the mods folder.
	"""
	base_path = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent.parent

	if base_path.name.upper() == "MODS" and base_path.parent.name.upper() == "UE4SS":
		return base_path

	if base_path.name.upper() == "UE4SS":
		mods_path = base_path / "Mods"
		if mods_path.exists() and mods_path.is_dir():
			return mods_path

	current = base_path
	for _ in range(4):
		if current.name.upper() == "MODS" and current.parent.name.upper() == "UE4SS":
			return current

		mods_path = current / "Mods"
		if mods_path.exists() and mods_path.is_dir() and (mods_path.parent.name.upper() == "UE4SS"):
			return mods_path

		ue4ss_path = current / "UE4SS" / "Mods"
		if ue4ss_path.exists() and ue4ss_path.is_dir():
			return ue4ss_path

			break
		current = current.parent

	return None


def find_assets() -> tuple[Path, Path]:
	"""
	Find the paths to the logo and icon assets.

	Returns:
		A tuple containing the paths to the logo and icon assets.
	"""
	base_path = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent.parent

	possible_locations = [
		base_path / "assets" / "img",
		base_path.parent / "assets" / "img",
		base_path / "img",
		base_path.parent / "img",
	]

	logo_path = None
	icon_path = None

	for location in possible_locations:
		if (location / "ue.svg").exists():
			logo_path = location / "ue.svg"

		if (location / "ue.ico").exists():
			icon_path = location / "ue.ico"

		if logo_path and icon_path:
			break

	return logo_path, icon_path


def main() -> None:
	"""Main entry point for the application."""
	try:
		mods_folder = find_mods_folder()
		if not mods_folder:
			import customtkinter as ctk

			ctk.set_appearance_mode("dark")
			app = ctk.CTk()
			app.withdraw()  # Hide the main window

			dialog = ctk.CTkToplevel(app)
			dialog.title("Error")
			dialog.geometry("400x75")
			dialog.minsize(400, 75)
			dialog.attributes("-topmost", True)

			frame = ctk.CTkFrame(dialog)
			frame.pack(fill="both", expand=True, padx=20, pady=20)

			error_message = (
				"Could not find the UE4SS Mods folder.\nPlease place this executable in the UE4SS/Mods folder."
			)
			error_label = ctk.CTkLabel(frame, text=error_message, wraplength=360)
			error_label.pack(padx=10, pady=(10, 20))

			ok_button = ctk.CTkButton(
				frame,
				text="OK",
				command=lambda: (dialog.destroy(), app.destroy(), sys.exit(1)),
				width=100,
			)
			ok_button.pack(pady=(0, 10))

			dialog.protocol("WM_DELETE_WINDOW", lambda: (dialog.destroy(), app.destroy(), sys.exit(1)))

			dialog.update_idletasks()
			width = dialog.winfo_width()
			height = dialog.winfo_height()
			x = (dialog.winfo_screenwidth() // 2) - (width // 2)
			y = (dialog.winfo_screenheight() // 2) - (height // 2)
			dialog.geometry(f"{width}x{height}+{x}+{y}")

			app.mainloop()
			return

		logo_path, icon_path = find_assets()

		try:
			mod_manager = UE4SSModManager(mods_folder)
		except (InvalidModFolderException, InvalidModException) as e:
			import customtkinter as ctk

			app = ctk.CTk()

			dialog = ctk.CTkToplevel(app)
			dialog.title("Error")
			dialog.geometry("400x150")
			dialog.transient(app)
			dialog.grab_set()

			frame = ctk.CTkFrame(dialog)
			frame.pack(fill="both", expand=True, padx=20, pady=20)

			error_label = ctk.CTkLabel(frame, text=str(e), wraplength=360)
			error_label.pack(padx=10, pady=(10, 20))

			ok_button = ctk.CTkButton(
				frame,
				text="OK",
				command=lambda: (dialog.destroy(), app.destroy(), sys.exit(1)),
				width=100,
			)
			ok_button.pack(pady=(0, 10))

			dialog.protocol("WM_DELETE_WINDOW", lambda: (dialog.destroy(), app.destroy(), sys.exit(1)))

			dialog.update_idletasks()
			width = dialog.winfo_width()
			height = dialog.winfo_height()
			x = (dialog.winfo_screenwidth() // 2) - (width // 2)
			y = (dialog.winfo_screenheight() // 2) - (height // 2)
			dialog.geometry(f"{width}x{height}+{x}+{y}")

			app.mainloop()
			return

		start_gui(mod_manager, logo_path, icon_path)

	except Exception as e:
		import customtkinter as ctk

		app = ctk.CTk()

		dialog = ctk.CTkToplevel(app)
		dialog.title("Error")
		dialog.geometry("400x200")
		dialog.transient(app)
		dialog.grab_set()

		frame = ctk.CTkFrame(dialog)
		frame.pack(fill="both", expand=True, padx=20, pady=20)

		error_label = ctk.CTkLabel(frame, text=f"An unexpected error occurred:\n{e}", wraplength=360)
		error_label.pack(padx=10, pady=(10, 20))

		ok_button = ctk.CTkButton(
			frame,
			text="OK",
			command=lambda: (dialog.destroy(), app.destroy(), sys.exit(1)),
			width=100,
		)
		ok_button.pack(pady=(0, 10))

		dialog.protocol("WM_DELETE_WINDOW", lambda: (dialog.destroy(), app.destroy(), sys.exit(1)))

		dialog.update_idletasks()
		width = dialog.winfo_width()
		height = dialog.winfo_height()
		x = (dialog.winfo_screenwidth() // 2) - (width // 2)
		y = (dialog.winfo_screenheight() // 2) - (height // 2)
		dialog.geometry(f"{width}x{height}+{x}+{y}")

		app.mainloop()


if __name__ == "__main__":
	main()
