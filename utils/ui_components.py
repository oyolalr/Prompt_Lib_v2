import streamlit as st
from utils.data_handler import add_item, update_item, delete_item, toggle_favorite, duplicate_item

def render_style_injection(theme: str = "standard"):
    """Injects the custom CSS based on the selected theme."""
    css_file = 'assets/tactical.css' if theme == "tactical" else 'assets/style.css'
    try:
        with open(css_file) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Theme file {css_file} not found.")

def render_component_card(item: dict, data_type: str):
    """Renders a single component card with Edit/Delete options."""
    
    # Unique key for state management
    card_key = f"card_{data_type}_{item['id']}"
    
    # We use a container to look like a card
    with st.container():
        tags_html = ""
        if item.get('tags'):
            tags_html = f'<div style="margin-top:5px;">{" ".join([f"<span style='background-color:#e9ecef; padding:2px 6px; border-radius:10px; font-size:0.8em; margin-right:5px;'>{tag}</span>" for tag in item["tags"]])}</div>'
            
        st.markdown(f"""
        <div class="prompt-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h4 style="margin:0;">{item['title']} {'⭐' if item.get('is_favorite') else ''}</h4>
            </div>
            {tags_html}
            <div class="content">{item['content']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
        with col1:
             if st.button("Edit", key=f"edit_{card_key}"):
                 st.session_state[f"edit_mode_{item['id']}"] = True
        with col2:
            if st.button("Duplicate", key=f"dup_{card_key}"):
                if duplicate_item(data_type, item['id']):
                    st.success("Duplicated!")
                    st.rerun()
        with col3:
            if st.button("Delete", key=f"delete_{card_key}"):
                if delete_item(data_type, item['id']):
                    st.success("Deleted!")
                    st.rerun()
        with col4:
             # Star button
             is_fav = item.get('is_favorite', False)
             btn_label = "Un-star" if is_fav else "Star"
             if st.button(btn_label, key=f"fav_{card_key}"):
                 toggle_favorite(data_type, item['id'])
                 st.rerun()

    # Edit Form (conditionally rendered)
    if st.session_state.get(f"edit_mode_{item['id']}", False):
        with st.form(key=f"edit_form_{card_key}"):
            st.markdown("### Edit Component")
            new_title = st.text_input("Title", value=item['title'])
            current_tags = ", ".join(item.get('tags', []))
            new_tags_str = st.text_input("Tags (comma-separated)", value=current_tags)
            new_content = st.text_area("Content", value=item['content'])
            
            create_ver = False
            if data_type == "saved_prompts":
                create_ver = st.checkbox("Save as new version", value=False)
            
            c1, c2 = st.columns(2)
            if c1.form_submit_button("Save Changes"):
                new_tags = [t.strip() for t in new_tags_str.split(",") if t.strip()]
                update_item(data_type, item['id'], new_title, new_content, new_tags, create_version=create_ver)
                del st.session_state[f"edit_mode_{item['id']}"]
                st.rerun()
            
            if c2.form_submit_button("Cancel"):
                del st.session_state[f"edit_mode_{item['id']}"]
                st.rerun()
        
        # Version History (Outside Form)
        if data_type == "saved_prompts" and 'versions' in item and item['versions']:
            with st.expander("📜 Version History"):
                for v in reversed(item['versions']):
                    st.markdown(f"**{v['timestamp']}**")
                    st.code(v['content'])
                    if st.button("Restore", key=f"rest_{v['timestamp']}_{card_key}"):
                        # Restore by updating content to this version
                        update_item(data_type, item['id'], item['title'], v['content'], item.get('tags'), create_version=True) 
                        st.rerun()

def render_add_form(data_type: str):
    """Renders a form to add a new component."""
    with st.expander(f"Add New {data_type.capitalize()}", expanded=False):
        with st.form(key=f"add_{data_type}"):
            title = st.text_input("Title")
            tags_str = st.text_input("Tags (comma-separated)", placeholder="e.g. officer, tactical, admin")
            content = st.text_area("Content")
            
            if st.form_submit_button("Add Component"):
                if title and content:
                    tags = [t.strip() for t in tags_str.split(",") if t.strip()]
                    add_item(data_type, title, content, tags)
                    st.success(f"Added new {data_type}!")
                    st.rerun()
                else:
                    st.error("Title and Content are required.")
