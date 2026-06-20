# AI Translation Bridge

A powerful Windows Desktop Application designed to automate and manage bulk translation tasks using multiple AI models.

## Overview
AI Translation Bridge streamlines the translation of batch terms from CSV/Excel files. It natively integrates with popular AI endpoints and features a unique **Hybrid Web Automation Mode** that connects to a dedicated Chrome Extension via WebSockets to drive translation directly on web interfaces (like Gemini).

## Key Features
- **Multi-Model Support**: Direct REST API integration with Google Gemini, OpenAI ChatGPT, Anthropic Claude, xAI Grok, and Gemini CLI proxies.
- **Hybrid Web Automation**: Automate translation tasks directly inside your browser through a bundled Manifest V3 Chrome Extension Bridge.
- **Bulk Batch Processing**: Read large CSV/Excel files, split them into optimal batches, parse responses automatically, and track progress seamlessly.
- **Smart Resumes**: Interrupted translations are safely preserved. The app auto-detects completed entries and resumes exactly where it left off.
- **Security First**: All API keys and sensitive settings are encrypted at rest using machine-specific cryptography before being stored locally.
- **Auto-Updates**: Built-in update manager that checks GitHub Releases and safely applies patches to your installation.

## Installation & Usage
1. Head over to the [Releases](https://github.com/LittleKai/AI-Translation-Bridge/releases) page.
2. Download the latest `AI_Translation_Bridge.zip`.
3. Extract the contents to your desired folder.
4. Run `AI Translation Bridge.exe`.

*Note: For Hybrid Web Automation features, follow the in-app instructions to load the bundled unpacked Chrome extension (`/extension` folder) into your browser.*

## Data Formats
- **Input File**: Must be a `.csv` or `.xlsx` file containing at least `id` and `text` columns.
- **Language Detection**: Automatically configures translation directions by looking for language tags (e.g., `JP`, `EN`, `KR`, `CN`, `VI`) in the input filename.
- **Output File**: Exports with `id`, `raw`, `edit`, and `status` columns.

## Tech Stack
Built with Python 3.10+, Tkinter/ttk for the GUI, and websockets for the Chrome extension bridge.
