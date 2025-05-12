from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from loguru import logger

from src.common.exceptions import InvalidModException


@dataclass
class UE4SSMod:
	"""Represents a UE4SS mod."""

	name: str
	path: Path
	enabled: bool
	scripts: list[str]
	is_native: bool = False
	lang: Literal["lua", "cpp"] = "lua"

	@classmethod
	def from_path(cls, path: Path, *, override_enabled: bool = False) -> "UE4SSMod":
		"""
		Constructs a UE4SSMod object from a given path.

		Args:
			path: The path to the mod directory.
			override_enabled (optional): If True, the mod will be considered enabled even if
				there is no enabled.txt file. Defaults to False.

		Raises:
			InvalidModException: If the mod directory does not contain a main.lua file or if the directory
				is not a directory.

		Returns:
			An instance of the UE4SSMod class with the mod's name, enabled status, and list of scripts.
		"""
		name = path.stem

		if not path.is_dir():
			logger.warning(f"Mod {name} is not a directory.")
			return None

		lua = [
			str(script).replace("/", "").replace("\\", "").split(name)[1][7:]
			for script in path.glob("scripts/*.lua", case_sensitive=False)
		]

		dll = [
			str(script).replace("/", "").replace("\\", "").split(name)[1][7:]
			for script in path.glob("dlls/*.dll", case_sensitive=False)
		]

		scripts = lua + dll

		if not scripts:
			raise InvalidModException(f"Mod {name} has no scripts.")

		if "main.lua" not in scripts and "main.dll" not in scripts:
			raise InvalidModException(f"Mod {name} does not have a main file: {scripts}")

		lang = "lua" if "main.lua" in scripts else "cpp"

		enabled = (path / "enabled.txt").exists() or override_enabled

		logger.debug(f"Mod {name} is {'enabled' if enabled else 'disabled'} with {len(scripts)} script(s)")

		return cls(name=name, enabled=enabled, scripts=scripts, path=path, lang=lang)

	def disable(self) -> None:
		"""Disables the mod by removing the enabled.txt file."""
		enabled_file = self.path / "enabled.txt"

		if enabled_file.exists():
			enabled_file.unlink()
			logger.debug(f"Enabled file {enabled_file} removed.")

		else:
			logger.warning(f"Enabled file {enabled_file} does not exist.")

		self.enabled = False

		logger.debug(f"Mod {self.name} disabled.")

	def enable(self) -> None:
		"""Enables the mod by creating an enabled.txt file."""
		enabled_file = self.path / "enabled.txt"
		enabled_file.touch()

		self.enabled = True

		logger.debug(f"Enabled file {enabled_file} created. Mod {self.name} enabled.")

	def __eq__(self, other: object) -> bool:
		"""
		Checks if two UE4SSMod objects are equal based on their name.

		Args:
			other: The other object to compare with.

		Returns:
			Whether the two objects are equal.
		"""
		if not isinstance(other, UE4SSMod):
			return False

		return self.name == other.name

	def __hash__(self) -> int:
		"""
		Returns the hash of the mod's name.

		Returns:
			The hash of the mod's name.
		"""
		return hash(self.name)
