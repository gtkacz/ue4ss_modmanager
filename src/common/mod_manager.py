from pathlib import Path

from loguru import logger

from src.common.exceptions import InvalidModFolderException
from src.common.mod import UE4SSMod


class UE4SSModManager:
	"""Manages the loading and enabling/disabling of UE4SS mods."""

	def __init__(self, path: Path) -> None:
		"""
		Initializes the UE4SSModManager with the given path.

		Args:
			path: The path to the mod folder.

		Raises:
			InvalidModFolderException: If the path is not a directory or does not have the correct folder structure.
		"""
		self.path = path

		if not path.is_dir() or not path.exists() or not self._has_right_folder_structure(path):
			raise InvalidModFolderException(f"Path {path} is not a directory.")

		self.mods = self.load_mods()

	@staticmethod
	def _has_right_folder_structure(path: Path) -> bool:
		"""
		Checks if the given path has the correct folder structure for the root mod folder.

		Args:
			path: The path to check.

		Returns:
			Whether the path has the correct folder structure.
		"""
		return path.stem.upper() == "MODS" and path.parent.stem.upper() == "UE4SS"

	def load_mods(self) -> list[UE4SSMod]:
		"""
		Loads all mods from the specified path.

		Returns:
			A list of UE4SSMod objects representing the mods in the directory.
		"""
		output = []

		for mod_path in self.path.iterdir():
			if mod_path.is_dir():
				try:
					mod = UE4SSMod.from_path(mod_path)
					if mod:
						output.append(mod)
				except Exception as e:
					logger.exception(f"Failed to load mod {mod_path}: {e}")

		return output

	def enable_mods(self, mod_names: list[str]) -> None:
		"""Enables the specified mods by creating enabled.txt files."""
		for mod in self.mods:
			if mod.name in mod_names:
				mod.enable()

	def disable_mods(self, mod_names: list[str]) -> None:
		"""Disables the specified mods by deleting enabled.txt files."""
		for mod in self.mods:
			if mod.name in mod_names:
				mod.disable()

	def parse_mods(self, mods: list[UE4SSMod]) -> None:
		"""
		Parses the mods and sets their enabled status.

		Args:
			mods: A list of UE4SSMod objects to parse.
		"""
		for mod in mods:
			if mod not in self.mods:
				logger.warning(f"Mod {mod.name} not found.")
				continue

			if mod.enabled:
				self.enable_mods([mod.name])

			else:
				self.disable_mods([mod.name])
		logger.debug(f"Parsed {len(mods)} mods.")

	@property
	def enabled_mods(self) -> list[UE4SSMod]:
		"""Returns a list of enabled mods."""
		return [mod.name for mod in self.mods if mod.enabled]

	@property
	def disabled_mods(self) -> list[UE4SSMod]:
		"""Returns a list of disabled mods."""
		return [mod.name for mod in self.mods if not mod.enabled]

	@property
	def all_mods(self) -> list[UE4SSMod]:
		"""Returns a list of all mods."""
		return [mod.name for mod in self.mods]
