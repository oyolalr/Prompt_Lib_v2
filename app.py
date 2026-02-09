import streamlit as st
import pandas as pd
import re
from utils.data_handler import load_data, add_item, export_library, import_library, save_blueprint, add_to_history
from utils.ui_components import render_style_injection, render_component_card, render_add_form
from utils.analytics import get_library_stats

# Page Config
st.set_page_config(
    page_title="Prompt Library",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Theme Configuration
    # We store theme in session state to persist
    if 'theme' not in st.session_state:
        st.session_state.theme = 'standard'
    
    # Inject Custom CSS
    render_style_injection(st.session_state.theme)
    
    # Navigation
    app_mode = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Assembler", "Saved Prompts", "Roles", "Goals", "Context", "Output", "Library Management"]
    )
    
    # Theme Toggle
    st.sidebar.markdown("---")
    use_tactical = st.sidebar.toggle("Tactical Mode", value=(st.session_state.theme == 'tactical'))
    if use_tactical != (st.session_state.theme == 'tactical'):
        st.session_state.theme = 'tactical' if use_tactical else 'standard'
        st.rerun()

    # Global Search
    search_query = st.sidebar.text_input("🔍 Global Search", placeholder="Find components...")
    if search_query:
        render_search_results(search_query)
        return
    
    if app_mode == "Dashboard":
        render_dashboard()
    elif app_mode == "Assembler":
        render_assembler()
    elif app_mode == "Saved Prompts":
        render_crud_interface("Saved_Prompts")
    elif app_mode == "Library Management":
        render_library_page()
    else:
        render_crud_interface(app_mode)

    st.sidebar.markdown("---")
    st.sidebar.markdown("---")
    st.sidebar.markdown("v2.3 USMC Advanced Edition")

def render_dashboard():
    """Renders the Analytics Dashboard."""
    st.title("Command Dashboard 📊")
    
    stats = get_library_stats()
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Components", stats["total_items"])
    col2.metric("Saved Prompts", stats["counts"].get("saved_prompts", 0))
    col3.metric("Roles Defined", stats["counts"].get("roles", 0))
    col4.metric("Favorites ⭐", stats["favorites"])
    
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Library Distribution")
        # Bar chart of counts
        chart_data = pd.DataFrame({
            "Type": list(stats["counts"].keys()),
            "Count": list(stats["counts"].values())
        }).set_index("Type")
        st.bar_chart(chart_data)
        
    with c2:
        st.subheader("Top Tags")
        if stats["top_tags"]:
            tag_data = pd.DataFrame({
                "Tag": list(stats["top_tags"].keys()),
                "Frequency": list(stats["top_tags"].values())
            }).set_index("Tag")
            st.bar_chart(tag_data)
        else:
            st.info("No tags used yet.")

    # Recent Activity (Placeholder for now since we don't have timestamps for all items)
    # Could use history logic here if needed.


def render_crud_interface(data_type_label: str):
    """Generic interface for managing Roles, Goals, etc."""
    # Map label to internal data type string (lowercase)
    data_type = data_type_label.lower().replace(" ", "_")
    
    st.header(f"{data_type_label.replace('_', ' ')} Manager")
    
    # 1. Add New Item Form
    render_add_form(data_type)
    
    st.markdown("---")
    
    # 2. List Existing Items
    items = load_data(data_type)
    
    if not items:
        st.info(f"No {data_type.replace('_', ' ')} found. Add one above!")
    else:
        st.subheader(f"Existing {data_type_label.replace('_', ' ')} ({len(items)})")
        # Display in a grid or list
        for item in items:
            render_component_card(item, data_type)

def render_library_page():
    """Page for importing and exporting the library."""
    st.title("Library Management 💾")
    
    st.subheader("Export Library")
    st.markdown("Download your entire library (Roles, Goals, Templates, etc.) as a JSON file.")
    
    json_data = export_library()
    st.download_button(
        label="Download Library JSON",
        data=json_data,
        file_name="prompt_library_export.json",
        mime="application/json"
    )
    
    st.markdown("---")
    st.subheader("Import Library")
    st.warning("Importing will merge new items. Existing items with the same ID will be skipped.")
    
    uploaded_file = st.file_uploader("Upload Library JSON", type=["json"])
    if uploaded_file is not None:
        string_data = uploaded_file.getvalue().decode("utf-8")
        if st.button("Import Data"):
            if import_library(string_data):
                st.success("Library imported successfully!")
            else:
                st.error("Failed to import library. Check file format.")

def render_assembler():
    """The main interface to build prompts."""
    st.title("Prompt Assembler 🛠️")
    
    # Load all data
    roles = load_data("roles")
    goals = load_data("goals")
    context = load_data("context")
    outputs = load_data("output")

    # Sort by favorites (favorites first)
    sort_key = lambda x: not x.get('is_favorite', False)
    roles = sorted(roles, key=sort_key)
    goals = sorted(goals, key=sort_key)
    context = sorted(context, key=sort_key)
    outputs = sorted(outputs, key=sort_key)

    # --- Blueprints (Recipes) ---
    blueprints = load_data("blueprints")
    
    # Helper to find index by ID
    def get_index_by_id(items, item_id):
        for idx, item in enumerate(items):
            if item['id'] == item_id:
                return idx
        return None

    # State for selections
    if 'role_select' not in st.session_state: st.session_state.role_select = None
    if 'goal_select' not in st.session_state: st.session_state.goal_select = None
    if 'output_select' not in st.session_state: st.session_state.output_select = None
    if 'context_select' not in st.session_state: st.session_state.context_select = []

    col_bp, col_btn = st.columns([3, 1])
    with col_bp:
        selected_bp = st.selectbox(
            "📂 Load Blueprint (Recipe)",
            options=blueprints,
            format_func=lambda x: x['title'],
            index=None,
            placeholder="Select a saved recipe...",
            key="bp_selector"
        )
    with col_btn:
        st.write("") # Spacer
        st.write("") 
        if st.button("Load", use_container_width=True):
            if selected_bp:
                # Find matching items by ID to ensure we have the correct object reference
                found_role = next((i for i in roles if i['id'] == selected_bp['role_id']), None)
                found_goal = next((i for i in goals if i['id'] == selected_bp['goal_id']), None)
                found_output = next((i for i in outputs if i['id'] == selected_bp['output_id']), None)
                found_context = [i for i in context if i['id'] in selected_bp['context_ids']]
                
                st.session_state.role_select = found_role
                st.session_state.goal_select = found_goal
                st.session_state.output_select = found_output
                st.session_state.context_select = found_context
                
                st.success(f"Loaded '{selected_bp['title']}'")
                st.rerun()

    # --- Tag Filtering ---
    sorted_tags = sorted(list({tag for cat in [roles, goals, context, outputs] for item in cat for tag in item.get('tags', [])}))
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Select Components")
        selected_tags = st.multiselect("Filter by Tags", options=sorted_tags)
        
        def get_options(items, current_selection):
            """Returns filtered items, ensuring current selection is always included."""
            # Start with a copy or filtered list
            if selected_tags:
                filtered = [i for i in items if i.get('tags') and any(tag in selected_tags for tag in i['tags'])]
            else:
                filtered = list(items)
            
            # Ensure the currently selected item is in the list (to avoid Streamlit errors)
            # current_selection can be a single item or list (for multiselect)
            if isinstance(current_selection, list):
                for sel in current_selection:
                    if sel and sel not in filtered:
                        filtered.append(sel)
            else:
                if current_selection and current_selection not in filtered:
                    filtered.append(current_selection)
            
            return filtered

        selected_role = st.selectbox(
            "Role", 
            options=get_options(roles, st.session_state.role_select), 
            format_func=lambda x: f"{'⭐ ' if x.get('is_favorite') else ''}{x['title']}",
            placeholder="Select a Role...",
            key="role_select",
            index=None
        )
        
        selected_goal = st.selectbox(
            "Goal", 
            options=get_options(goals, st.session_state.goal_select), 
            format_func=lambda x: f"{'⭐ ' if x.get('is_favorite') else ''}{x['title']}",
            placeholder="Select a Goal...",
            key="goal_select",
            index=None
        )
        
        selected_context = st.multiselect(
            "Context", 
            options=get_options(context, st.session_state.context_select), 
            format_func=lambda x: f"{'⭐ ' if x.get('is_favorite') else ''}{x['title']}",
            key="context_select",
            default=None 
        )
        
        selected_output = st.selectbox(
            "Output Format", 
            options=get_options(outputs, st.session_state.output_select), 
            format_func=lambda x: f"{'⭐ ' if x.get('is_favorite') else ''}{x['title']}",
            placeholder="Select Output format...",
            key="output_select",
            index=None
        )
        
        custom_instructions = st.text_area("Additional Instructions", height=100)

        # Save Blueprint Button
        with st.expander("💾 Save as Blueprint"):
            bp_title = st.text_input("Blueprint Name")
            if st.button("Save Blueprint"):
                if bp_title and selected_role and selected_goal and selected_output:
                    save_blueprint(
                        bp_title, 
                        selected_role['id'], 
                        selected_goal['id'], 
                        [c['id'] for c in selected_context], 
                        selected_output['id']
                    )
                    st.success("Blueprint saved!")
                    st.rerun()
                else:
                    st.error("Missing title or components.")

    with col2:
        st.subheader("Live Preview")
        
        # Construct the detailed prompt
        preview_text_parts = []
        
        if selected_role:
            preview_text_parts.append(f"**Role:**\n{selected_role['content']}")
        
        if selected_goal:
            preview_text_parts.append(f"**Goal:**\n{selected_goal['content']}")
            
        if selected_context:
            preview_text_parts.append("**Context:**")
            for c in selected_context:
                preview_text_parts.append(f"- {c['content']}")
        
        if selected_output:
            preview_text_parts.append(f"**Output Format:**\n{selected_output['content']}")
            
        if custom_instructions:
            preview_text_parts.append(f"**Additional Instructions:**\n{custom_instructions}")
            
        final_prompt_display_base = "\n\n".join(preview_text_parts)
        
        # --- Placeholder Filling ---
        placeholders = re.findall(r'\{\{(.*?)\}\}', final_prompt_display_base)
        unique_placeholders = sorted(list(set(placeholders)))
        
        final_prompt_filled = final_prompt_display_base
        
        if unique_placeholders:
            st.info("Start typing to fill in the placeholders found in your template.")
            for ph in unique_placeholders:
                val = st.text_input(f"Value for {ph}", key=f"ph_{ph}")
                if val:
                    final_prompt_filled = final_prompt_filled.replace(f"{{{{{ph}}}}}", val)

        
        # For actual raw text copy
        final_prompt_raw = final_prompt_filled.replace("**Role:**\n", "").replace("**Goal:**\n", "").replace("**Context:**", "Context:").replace("**Output Format:**\n", "").replace("**Additional Instructions:**\n", "")

        st.markdown(
            f'<div style="background-color:#f8f9fa; padding:15px; border-radius:5px; border:1px solid #ddd; min-height:400px; white-space: pre-wrap;">{final_prompt_filled if final_prompt_filled else "Select components to build your prompt..."}</div>', 
            unsafe_allow_html=True
        )
        
        if final_prompt_display_base:
            st.code(final_prompt_raw, language=None)
            st.caption("Copy the code block above")
            
            # --- Auto-Save to History ---
            # We want to save to history when the prompt is distinct enough or user clicks something?
            # Or just when they click "Save" or "Copy"? Since "Copy" is browser-side, we can't hook it easily.
            # Best is to just save on every valid render? No, too spammy.
            # Maybe add a dedicated "Generate & Log" button?
            # Or just implicitly save when the prompt changes?
            
            # Let's add a "Log to History" button for now to be explicit, or hook into "Save Prompt".
            # Actually, user asked for "generated prompts". 
            # I'll add a database check: if this exact content isn't the most recent in history, add it?
            # For simplicity: Add a "Snap to History" button or similar.
            
            if st.button("📝 Log to History"):
                add_to_history(final_prompt_raw)
                st.success("Logged to history.")

            # --- External Links ---
            st.markdown("### Open in...")
            l_col1, l_col2, l_col3 = st.columns(3)
            l_col1.link_button("ChatGPT", "https://chatgpt.com")
            l_col2.link_button("Claude", "https://claude.ai")
            l_col3.link_button("Gemini", "https://gemini.google.com")
            
            st.markdown("---")
            st.subheader("Save Prompt")
            save_name = st.text_input("Name this prompt", placeholder="e.g. My Custom Prompt")
            if st.button("Save to Library"):
                if save_name:
                    add_item("saved_prompts", save_name, final_prompt_raw)
                    add_to_history(final_prompt_raw) # Also log to history on save
                    st.success(f"Saved '{save_name}' to Saved Prompts!")
                else:
                    st.error("Please provide a name for the prompt.")

    # --- History Panel ---
    st.markdown("---")
    with st.expander("🕒 Recent History (Last 20)", expanded=False):
        history = load_data("history")
        if not history:
            st.info("No history yet.")
        else:
            for item in history:
                st.text_area(f"From {item.get('timestamp', 'Unknown')}", value=item['content'], height=100, key=f"hist_{item['id']}")

def render_search_results(query: str):
    """Search across all data types."""
    st.title(f"Search Results for '{query}'")
    
    query = query.lower()
    
    found_any = False
    
    for dtype in ["roles", "goals", "context", "output", "saved_prompts"]:
        items = load_data(dtype)
        matching = [
            i for i in items 
            if query in i['title'].lower() 
            or query in i['content'].lower()
            or any(query in t.lower() for t in i.get('tags', []))
        ]
        
        if matching:
            found_any = True
            st.subheader(dtype.replace("_", " ").title())
            for item in matching:
                render_component_card(item, dtype)
    
    if not found_any:
        st.warning("No matches found.")

if __name__ == "__main__":
    main()
