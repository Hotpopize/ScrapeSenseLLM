import streamlit as st
import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.db_helpers import save_coded_data, log_action
from modules import ollama_client as ollama

def render():
    st.header("LLM-Assisted Thematic Coding 🤖 ")
    
    st.info("""
    This module uses **Local LLMs via Ollama** to ensure academic replicability and privacy.
    
    **Requirements:**
    - Ollama must be running (`ollama serve`)
    - You must have at least one model pulled (e.g., `ollama pull llama3`)
    """)
    
    # Check Connection
    if not ollama.is_ollama_running():
        st.error("⚠️ **Ollama is not reachable.** Please ensure Ollama is running on localhost:11434.")
        st.code("ollama serve", language="bash")
        return
        
    # Get Models
    available_models = ollama.get_available_models()
    if not available_models:
        st.warning("⚠️ **No models found.** Please pull a model using your terminal.")
        st.code("ollama pull llama3", language="bash")
        return
    
    if not st.session_state.collected_data:
        st.warning("⚠️ No data collected yet. Please collect data from the Reddit Data Collection module first.")
        return
    
    st.divider()
    
    st.subheader("⚙️ Coding Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        coding_approach = st.selectbox(
            "Coding Approach",
            ["Deductive (PPM Framework Only)", "Inductive (Emergent Themes Only)", "Mixed (PPM + Emergent Themes)"]
        )
        
        # Prioritize "Packaged" models
        packaged_models = ["llama3.1", "gemma3:12b"]
        
        # Sort: Packaged models first, then others alphabetically
        available_models.sort(key=lambda x: (x not in packaged_models, x))
        
        # Find index of first packaged model available to set as default
        default_index = 0
        for idx, m in enumerate(available_models):
            if m in packaged_models:
                default_index = idx
                break

        model_selection = st.selectbox(
            "Local LLM Model",
            available_models,
            index=default_index if available_models else None,
            help="Select a model installed in Ollama. 'Packaged' models (llama3.1, gemma3:12b) are prioritized."
        )
    
    with col2:
        batch_size = st.number_input(
            "Batch Size for Coding",
            min_value=1,
            max_value=50,
            value=10,
            help="Number of items to code at once"
        )
        
        include_already_coded = st.checkbox(
            "Re-code already coded items",
            value=False,
            help="Check this to override previous coding"
        )
    
    st.divider()
    
    with st.expander("📖 View PPM Framework Definitions"):
        st.markdown("""
        ### Push Factors (Dissatisfaction with Current State)
        - Cognitive decline or perceived decline
        - Stress, anxiety, or mental fatigue
        - Poor focus or concentration
        - Memory issues
        - Academic or professional pressure
        - Dissatisfaction with pharmaceutical options
        
        ### Pull Factors (Attraction to Natural Nootropics)
        - Perceived cognitive benefits
        - Natural/organic ingredients preference
        - Positive testimonials or reviews
        - Scientific evidence or studies
        - Brand reputation
        - Specific ingredient efficacy
        
        ### Mooring Factors (Anchoring Elements)
        - Cost and affordability
        - Accessibility and availability
        - Trust in sources (brands, influencers, community)
        - Regulatory concerns or safety
        - Existing habits or routines
        - Side effects concerns
        """)
    
    if st.button("🚀 Start Local LLM Coding", type="primary"):
        uncoded_data = [item for item in st.session_state.collected_data 
                       if include_already_coded or item.get('id') not in [c.get('id') for c in st.session_state.coded_data]]
        
        if not uncoded_data:
            st.info("All items have been coded. Enable 're-code already coded items' to code again.")
            return
        
        items_to_code = uncoded_data[:batch_size]
        
        st.info(f"🔄 Coding {len(items_to_code)} items using {model_selection}...")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        coded_results = []
        consecutive_errors = 0
        MAX_CONSECUTIVE_ERRORS = 3
        
        for idx, item in enumerate(items_to_code):
            # Safe Stop if too many errors
            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                st.error(f"🛑 **Process Stopped Early**: Encountered {MAX_CONSECUTIVE_ERRORS} consecutive errors. Stopping to prevent infinite retries/loops.")
                break

            status_text.text(f"Coding item {idx + 1} of {len(items_to_code)}...")
            
            try:
                prompt = create_coding_prompt(item, coding_approach)
                system_prompt = "You are an academic research assistant specialized in qualitative thematic coding. You effectively output only valid JSON without markdown formatting."
                
                # Call Ollama
                coding_result = ollama.generate_completion(model_selection, prompt, system_prompt)
                
                # Sanitize response
                if "```json" in coding_result:
                    coding_result = coding_result.split("```json")[1].split("```")[0]
                elif "```" in coding_result:
                    coding_result = coding_result.split("```")[1].split("```")[0]
                
                coding_data = json.loads(coding_result)
                
                is_relevant = coding_data.get('is_relevant', True) # Default to true if missing for backward compat
                
                if not is_relevant:
                     coded_item = {
                        **item,
                        'ppm_category': 'Excluded (Irrelevant)',
                        'ppm_subcodes': [],
                        'themes': [],
                        'evidence_quotes': [],
                        'confidence': 'High',
                        'coded_at': datetime.now().isoformat(),
                        'coded_by': f"Ollama-{model_selection}",
                        'coding_approach': coding_approach,
                        'rationale': coding_data.get('rationale', 'Does not meet inclusion criteria')
                    }
                else:
                    coded_item = {
                        **item,
                        'ppm_category': coding_data.get('ppm_category', 'Unknown'),
                        'ppm_subcodes': coding_data.get('ppm_subcodes', []),
                        'themes': coding_data.get('emergent_themes', []),
                        'evidence_quotes': coding_data.get('evidence_quotes', []),
                        'confidence': coding_data.get('confidence', 'Medium'),
                        'coded_at': datetime.now().isoformat(),
                        'coded_by': f"Ollama-{model_selection}",
                        'coding_approach': coding_approach,
                         'rationale': coding_data.get('rationale', '')
                    }
                
                coded_results.append(coded_item)
                consecutive_errors = 0 # Reset on success
                
            except Exception as e:
                consecutive_errors += 1
                st.warning(f"⚠️ Error coding item {item.get('id')}: {str(e)} (Consecutive Errors: {consecutive_errors}/{MAX_CONSECUTIVE_ERRORS})")
                # Continue process to next item check
            
            progress_bar.progress((idx + 1) / len(items_to_code))
        
        if include_already_coded:
            st.session_state.coded_data = [c for c in st.session_state.coded_data 
                                          if c.get('id') not in [r.get('id') for r in coded_results]]
        
        st.session_state.coded_data.extend(coded_results)
        
        saved_count = save_coded_data(coded_results, st.session_state.session_id)
        
        log_action(
            action='llm_coding_ollama',
            session_id=st.session_state.session_id,
            details={
                'model': model_selection,
                'coding_approach': coding_approach,
                'items_coded': len(coded_results),
                'saved_to_db': saved_count
            }
        )
        
        status_text.empty()
        progress_bar.empty()
        
        st.success(f"✅ Successfully coded and saved {saved_count} items")
        
        st.subheader("📊 Coding Results Summary")
        
        ppm_dist = {}
        for item in coded_results:
            cat = item.get('ppm_category', 'Unknown')
            ppm_dist[cat] = ppm_dist.get(cat, 0) + 1
        
        st.write("**PPM Category Distribution:**")
        st.bar_chart(ppm_dist)
        
        all_themes = []
        for item in coded_results:
            all_themes.extend(item.get('themes', []))
        
        if all_themes:
            from collections import Counter
            theme_counts = Counter(all_themes)
            st.write("**Most Common Emergent Themes:**")
            st.write(theme_counts.most_common(10))
    
    st.divider()
    
    if st.session_state.coded_data:
        st.subheader("📋 Coded Data Preview")
        
        st.write(f"**Total Coded Items:** {len(st.session_state.coded_data)}")
        
        for item in st.session_state.coded_data[:5]:
            with st.expander(f"{item.get('type', 'item').upper()}: {item.get('title', 'No title')[:100]}..."):
                st.write(f"**Text:** {item.get('text', 'No text')[:500]}...")
                st.write(f"**PPM Category:** {item.get('ppm_category', 'N/A')}")
                st.write(f"**Subcodes:** {', '.join(item.get('ppm_subcodes', []))}")
                st.write(f"**Emergent Themes:** {', '.join(item.get('themes', []))}")
                st.write(f"**Evidence Quotes:** {item.get('evidence_quotes', [])}")
                st.write(f"**Confidence:** {item.get('confidence', 'N/A')}")
                st.write(f"**Coded By:** {item.get('coded_by', 'N/A')} at {item.get('coded_at', 'N/A')}")

def create_coding_prompt(item, approach):
    text_content = f"Title: {item.get('title', '')}\nContent: {item.get('text', '')}"
    
    # --- Helper to format codebook sections ---
    def format_codebook_section(category_key):
        if 'codebook' not in st.session_state or category_key not in st.session_state.codebook:
            return "- No codes defined."
            
        codes = st.session_state.codebook[category_key]
        if not codes:
            return "- No codes defined."
            
        formatted = []
        for c in codes:
            meta = c.get('metadata', {})
            code_id = meta.get('id', 'N/A')
            name = c['name']
            defn = c['definition']
            include = meta.get('include', '')
            exclude = meta.get('exclude', '')
            
            entry = f"{code_id}: {name} - {defn}"
            if include:
                 entry += f" (INCLUDE: {include})"
            if exclude:
                 entry += f" (EXCLUDE: {exclude})"
            formatted.append(entry)
            
        return "\n".join(formatted)

    # --- Build Prompts ---
    push_section = format_codebook_section('push_factors')
    pull_section = format_codebook_section('pull_factors')
    moor_section = format_codebook_section('mooring_factors') # Facilitators & Inhibitors in one list if structured that way or update codebook structure
    
    # Note: If mooring has subsections in UI but flat list in codebook, handled by flat list above.
    
    if approach == "Deductive (PPM Framework Only)":
        prompt = f"""Analyze the following Reddit post/comment about cognitive supplements.

TEXT:
{text_content}

INCLUSION CRITERIA Check:
Does this text discuss experiences with BOTH conventional cognitive enhancers (e.g., caffeine, adderall) AND natural alternatives (e.g., lions mane, ashwagandha, nootropics), articulating a transition, comparison, or supplement strategy?
If NO, set "is_relevant": false and stop.

TASK:
1. Determine Relevance based on inclusion criteria.
2. If Relevant: Assign PPM codes based on the definitions below.
   - You may assign multiple codes.
   - Use the exact IDs (e.g., PUSH-01).

--- CODEBOOK DEFINITIONS ---

PUSH FACTORS (Dissatisfaction):
{push_section}

PULL FACTORS (Attraction):
{pull_section}

MOORING FACTORS (Facilitators/Inhibitors):
{moor_section}

----------------------------

Respond in Strict JSON format:
{{
  "is_relevant": true|false,
  "ppm_category": "Push|Pull|Mooring|Mixed", 
  "ppm_subcodes": ["PUSH-01: Acute Side Effects", "MOOR-I02: Financial Costs"],
  "evidence_quotes": ["quote 1", "quote 2"],
  "confidence": "High|Medium|Low",
  "rationale": "brief explanation"
}}"""
    
    elif approach == "Inductive (Emergent Themes Only)":
        prompt = f"""Analyze the text for emergent themes not covered by standard PPM theory.

TEXT:
{text_content}

Respond in Strict JSON format:
{{
  "is_relevant": true|false,
  "emergent_themes": ["theme 1", "theme 2"],
  "evidence_quotes": ["quote 1"],
  "confidence": "High|Medium|Low",
  "rationale": "brief explanation"
}}"""
    
    else: # Mixed
        prompt = f"""Analyze using the PPM framework AND identify new emergent themes.

TEXT:
{text_content}

--- CODEBOOK DEFINITIONS ---
PUSH:
{push_section}

PULL:
{pull_section}

MOORING:
{moor_section}

----------------------------

Respond in Strict JSON format:
{{
  "is_relevant": true|false,
  "ppm_category": "Mixed",
  "ppm_subcodes": ["ID: Name"],
  "emergent_themes": ["new theme"],
  "evidence_quotes": ["quote"],
  "confidence": "High|Medium|Low",
  "rationale": "explanation"
}}"""
    
    return prompt
