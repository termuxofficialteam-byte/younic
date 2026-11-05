# YOUNIC — AI Developer Studio

YOUNIC is an experimental terminal-based AI coding assistant for Termux, Linux, and Windows. It uses the Google Gemini API to generate and edit source files, then provides basic syntax checks, run/build helpers, project backups, exports, and generated-tool management.

## Requirements

- Python 3.8 or newer.
- Git, for cloning and updating this repository.
- A Google Gemini API key accepted by the model configured in YOUNIC.
- No third-party Python package is required to run YOUNIC itself; it uses Python's standard library. There is no `requirements.txt` for the application.

Optional language checks and runs need the relevant tools installed separately, such as Clang/Clang++, Node.js, TypeScript, PHP, Ruby, Perl, Lua, Go, Rust, or Java. These are not needed just to launch YOUNIC.

## Install in Termux

Open Termux and run these commands:

```sh
pkg update -y && pkg upgrade -y
pkg install -y python git
```

Clone the public repository:

```sh
cd ~
git clone https://github.com/termuxofficialteam-byte/younic.git
cd ~/younic
```

## Configure and run

Start the application from its repository folder:

```sh
python younic2.py
```

On the first launch, YOUNIC asks for a Gemini API key in the terminal. Get your own key through Google AI Studio and paste it only at that local prompt. YOUNIC saves the key in `~/codex/.apikey` and attempts to restrict the file permissions. Keep the key private. This version does not read `GEMINI_API_KEY` from the environment; use the prompt instead.

To update an existing checkout and launch the updated app:

```sh
cd ~/younic
git pull
python younic2.py
```

On Windows, install Python and Git, clone the same repository, open a terminal in the cloned folder, and run `python younic2.py`. On Linux, install Python 3 and Git using your distribution's package manager, then follow the same `git clone` and `python younic2.py` steps.

## Optional Android storage setup

To let `/save` export files to shared Android storage, run this once and approve the Android permission prompt:

```sh
termux-setup-storage
```

The default export folder on Termux is `/sdcard/Codex`. YOUNIC keeps projects in `~/codex/projects`, backups in `~/codex/backups`, preferences in `~/codex/config.json`, and the API key in `~/codex/.apikey`.

## Security notice

**Educational and experimental use only. YOUNIC is not a secure sandbox, production IDE, or security scanner.** AI-generated code is untrusted and may be incorrect or harmful. `/run`, `/fix`, and the generated-tool workflow can execute code on the device with the permissions of the current user. `/tool` may also install packages listed in a generated `requirements.txt`. Review every generated file and dependency before running or installing it. Use a disposable, unprivileged environment and do not keep sensitive files or credentials in it.

Prompts and source code submitted for generation or AI review are sent to the configured Google API. Do not send passwords, API keys, personal data, or confidential source code unless you are authorized and accept the provider's data-handling terms. Never commit `.apikey`, other credentials, personal data, or private project files to GitHub.

## Commands

Commands are entered at YOUNIC's terminal prompt. Plain-language requests create a generated tool.

| Command | Purpose |
| --- | --- |
| `/new` | Start a fresh conversation; does not delete files. |
| `/paste` | Paste code, save it as a project file, and enter edit-loop mode. |
| `/open <file>` | Load a project file. |
| `/show [file]` | Display the active or named file. |
| `/list` | List project files. |
| `/edit [request]` | Ask AI to edit the active file. |
| `/fix` | Check/build the active file and request an AI repair if a check fails. |
| `/advise` | Run local heuristic analysis and optionally request AI review or changes. |
| `/loop` | Make repeated edits to the active file. |
| `/run` | Run/open the active file. |
| `/save` | Export the active file to the configured output folder. |
| `/undo` | Restore the latest matching project backup. |
| `/tool <request>` | Generate a multi-file tool; may install dependencies and run the tool to test it. |
| `/tool <name> <request>` | Create or upgrade a named registered tool. |
| `/tools` | List registered generated tools. |
| `/launch <name>` | Launch a generated tool. |
| `/runmode auto\|newterm\|same\|vscode` | Select the generated-tool launch mode. |
| `/key` | Replace the locally saved API key. |
| `/model [name]` | Show or set the model identifier. |
| `/outdir [path]` | Show or set the export directory. |
| `/speed [preset]` | Change terminal typewriter speed. |
| `/anim on\|off` | Toggle animations. |
| `/stats` | Show session counters and uptime. |
| `/menu`, `/guide`, `/help`, `/about` | Open the menu, help topics, command list, or app information. |
| `/clear` | Clear the terminal and replay the intro. |
| `/quit` | Exit YOUNIC. |

## Function map

The code is organized into these main function groups:

- **Terminal interface:** `w`, `cls`, `cols`, `banner`, `boot_sequence`, `goodbye_screen`, `green_wave`, `matrix_rain`, `pulse_line`, `shade_bar`, `typewriter`, `box`, `notify`, `Loader`, `timed_stage`, `pipeline_panel`, `render_line`, and `type_line` handle terminal output, animation, progress, and code display.
- **API and settings:** `get_key`, `load_model`, `save_model`, `load_outdir`, `save_outdir`, `load_speed`, `save_speed`, `load_anim`, `save_anim`, `_save_config`, `stream_ai`, `ask_ai`, and `extract` manage API access, configuration, response streaming, and parsing.
- **Project files and code changes:** `show_file`, `show_diff`, `backup`, `export`, `live_write`, `pipeline`, `multiline`, `edit_loop`, and `run_file` display, save, back up, export, generate, edit, test, and run project files.
- **Checks and debugging:** `_run_cmd`, `_test_run`, `check_only`, `build`, `parse_error_lines`, and `debug_view` perform basic per-language checks, execution/build attempts, and error display. These checks do not prove code is safe.
- **Advice and help:** `analyze_code`, `show_advice`, `ai_review`, `qoder_advise`, `select_menu`, `pick_menu`, `show_guide`, `show_help`, `show_about`, and `stats` implement local heuristics, optional AI review, selectors, guidance, and status displays.
- **Generated tools:** `safe_rel`, `slugify`, `tool_dir`, `load_registry`, `save_registry`, `extract_files`, `plan_tool`, `gen_file`, `write_tool_file`, `install_requirements`, `test_tool`, `fix_tool`, `route_request`, `preview_code`, and `build_tool` handle generated-tool planning, files, dependencies, testing, upgrades, and registry entries.
- **Launching and startup:** `is_termux`, `run_mode`, `make_run_script`, `launch_tool`, `show_tools`, `write_tool_readme`, and `main` manage platform detection, generated-tool launching, tool listings/documentation, and the command loop.

`if __name__ == "__main__": main()` starts the interactive application when the file is run directly.

## Copyright and permissions

Copyright (c) 2026 Termux Developer. All rights reserved. See [`LICENSE`](LICENSE). This repository is public for viewing, but no permission to copy, modify, redistribute, or sell the software is granted except where applicable law or the GitHub platform's own terms require otherwise. For written permission, contact `termuxofficialteam@gmail.com`.
