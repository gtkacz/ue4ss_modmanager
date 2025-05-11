from pathlib import Path

from loguru import logger

from src.common.mod import UE4SSMod


class UE4SSModManager:
	def __init__(self, path: Path):
		self.path = path
		self.mods = self.load_mods()

	def load_mods(self) -> list[UE4SSMod]:
		output = []

		for mod_path in self.path.iterdir():
			if mod_path.is_dir():
				try:
					mod = UE4SSMod.from_path(mod_path)
					if mod:
						output.append(mod)
				except Exception as e:
					logger.error(f"Failed to load mod {mod_path}: {e}")

		return output
