# Prompt Library V2 (USMC Advanced Edition)

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Python](https://img.shields.io/badge/python-3.8%2B-blue) ![Streamlit](https://img.shields.io/badge/streamlit-1.30%2B-FF4B4B)

## 📌 Project Overview

**Prompt Library V2** is a centralized, local-first application designed to modularize, store, and assemble AI prompts. It allows users to build complex prompts by combining reusable components (Roles, Goals, Context, Outputs) and provides a "Tactical" interface for high-focus environments.

This tool is built to comply with **USMC TECOM / TRNGCMD** standards for training and operations support.

> **Acknowledgement**: The original idea for this project is derived from [Kyle Moschetto's Prompt Library](https://github.com/kylemoschetto/kmo-prompt-library).

### ✨ Key Features

*   **Modular Prompt Building**: Create and manage Roles, Goals, Contexts, and Output formats independently.
*   **Prompt Assembler**: Drag-and-drop style interface to construct final prompts from your library.
*   **Blueprints (Recipes)**: Save your favorite combinations of components as reusable templates.
*   **Dynamic Placeholders**: Use `{{variable}}` syntax in your components to create fillable forms in the Assembler.
*   **Tactical Dark Mode**: A custom high-contrast, low-strain UI theme.
*   **Library Management**: Export and Import your entire library as JSON for backup or sharing.
*   **"Open in..." Integration**: One-click buttons to open your assembled prompt in ChatGPT, Claude, DeepSeek, or Gemini.
*   **Analytics Dashboard**: Track your most used components and library growth.

## 🚀 Getting Started

### Prerequisites

*   **Python 3.8** or higher
*   **Git** (for version control)

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/prompt-library-v2.git
    cd prompt-library-v2
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

**Option 1: The Easy Way (Windows)**
Double-click the `start.bat` file in the project folder.

**Option 2: via Terminal**
```bash
python -m streamlit run app.py
```

The application will automatically open in your default web browser at `http://localhost:8501`.

## 📖 Usage Guide

### 1. Creating Components
Navigate to the **Roles**, **Goals**, **Context**, or **Output** tabs in the sidebar.
*   Click **"Add New"** to create a component.
*   **Tip**: Add `{{variable}}` in your content to create a dynamic placeholder (e.g., "Write a blog post about {{topic}}").

### 2. Assembling a Prompt
Go to the **Assembler** tab.
1.  Select a Role, Goal, Context, and Output format from the dropdowns.
2.  If your components have placeholders, a form will appear for you to fill them in.
3.  The **Live Preview** will show your final prompt.
4.  Click **"Copy to Clipboard"** or use the **"Open in..."** buttons to use your prompt immediately.

### 3. Saving Blueprints
In the Assembler, once you have a good combination selected, expand the **"Save as Blueprint"** section, give it a name, and save. You can essentially "load" this entire configuration later with one click.

### 4. Search
Use the **Global Search** in the sidebar to find any component or saved prompt instantly.

## 📂 Project Structure

```
Prompt_Lib_v2/
├── app.py                 # Main Streamlit application entry point
├── start.bat              # Windows startup script
├── content/               # (Legacy)
├── data/                  # JSON storage for all library items
│   ├── roles.json
│   ├── goals.json
│   └── ...
├── utils/                 # Helper modules
│   ├── data_handler.py    # JSON CRUD operations
│   ├── ui_components.py   # Reusable UI widgets
│   └── analytics.py       # Stats and charts logic
├── assets/                # Images and static assets
└── requirements.txt       # Python dependencies
```

## 🛡️ Compliance

This application adheres to local operational security protocols for data handling. All data is stored locally on the machine in plain JSON text files. No data is sent to external servers unless the user explicitly clicks an external link provider.

## 🤝 Contributing

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

---
*Created by [Your Name/Unit] - 2024*
