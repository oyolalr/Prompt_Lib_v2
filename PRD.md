# Product Requirements Document (PRD): Prompt Library

## 1. Project Overview
**Project Name:** Prompt Library
**Objective:** A local, web-based tool to modularize prompt engineering by creating and storing reusable prompt components (Roles, Goals, Context, and Output) and assembling them into a final string.
**Platform:** Streamlit (Python)
**Environment:** Localhost, no authentication required.

## 2. Technical Specifications
* **Framework:** Streamlit
* **Storage:** Local JSON files (e.g., `data/roles.json`, `data/goals.json`, etc.)
* **Styling:** Custom CSS injection for a **Blue and Orange** color scheme.
* **Architecture:** Single-page application with a sidebar for navigation or a tabbed main interface.

## 3. Core Features & Requirements

### 3.1 Component Management (CRUD)
The application will have four distinct tabs/sections to manage the building blocks of a prompt:
* **Roles:** Define the persona (e.g., "Senior Python Developer").
* **Goals:** Define the objective (e.g., "Refactor this function for performance").
* **Context:** Provide background info (e.g., "This is for a high-traffic API").
* **Output:** Define the format (e.g., "Markdown table" or "JSON").

**Functionality for each tab:**
* Input fields for a "Title" and "Content".
* "Save" button to write to the respective JSON file.
* Display of existing items with "Edit" or "Delete" capabilities.

### 3.2 Prompt Assembler Screen
A dedicated interface to construct the final prompt:
* **Selection:** Dropdowns or multi-select widgets populated from the local JSON files.
* **Live Preview:** A dynamic text area showing the combined prompt strings.
* **Order Management:** Ability to arrange the sequence of the components.
* **Clipboard:** A "Copy to Clipboard" button for easy use in LLMs.

### 3.3 UI/UX Design
* **Color Palette:** * Primary Blue: Headers, buttons, and active states.
    * Accent Orange: Highlighting, warnings, or "Copy" actions.
* **Layout:** Clean, minimalist interface optimized for desktop use.

## 4. Data Structure (JSON Example)
```json
{
  "items": [
    {
      "id": "uuid-string",
      "title": "Data Scientist",
      "content": "You are a world-class data scientist specializing in NLP."
    }
  ]
}