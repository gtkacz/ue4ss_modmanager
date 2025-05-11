# UE4SS Mod Manager

A simple GUI application for managing [UE4SS](https://github.com/UE4SS-RE/RE-UE4SS) mods in Unreal Engine games.

![UE4SS Logo](assets/img/ue.svg)

## Features

- Enable/disable mods with a single click
- Toggle all mods on/off with one button
- Configurable save options:
  - Individual enabled.txt files
  - mods.json for UE4SS
  - mods.txt for UE4SS
- Modern dark mode UI
- Simple, intuitive interface

## Installation

### Option 1: Pre-built executable

1. Download the latest release from the [Releases page](https://github.com/gmtkacz/ue4ss_modmanager/releases)
2. Place the executable in your game's `UE4SS/Mods` folder
3. Run the executable

### Option 2: Run from source

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python src/main.py
   ```

## Usage

1. Launch the application
2. All mods in your UE4SS/Mods folder are automatically detected
3. Enable/disable mods by checking/unchecking their boxes
4. Use "Toggle All" to enable/disable all mods at once
5. Configure save options:
   - "Save enabled.txt" - Updates individual enabled.txt files in each mod folder
   - "Save mods.json" - Updates the mods.json file used by UE4SS
   - "Save mods.txt" - Updates the mods.txt file used by UE4SS
6. Click "Save Changes" to apply your configuration

## How It Works

- The manager looks for mod folders in the UE4SS/Mods directory
- Each mod must have a scripts folder with at least one main.lua file
- Enabling a mod creates an enabled.txt file in its folder and adds entries to mods.json and mods.txt
- Disabling a mod removes these entries

## Requirements

- Windows 10/11
- UE4SS installed in your game directory

## Development

### Setup Development Environment

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -r requirements.dev.txt
   ```
3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Building from Source

See the [Building Guide](BUILDING.md) for instructions on compiling to an executable.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch: `git create -c feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Security

For security issues, please see [SECURITY.md](SECURITY.md).