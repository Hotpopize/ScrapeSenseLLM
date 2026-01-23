import streamlit as st
import json
import pandas as pd
from datetime import datetime
from utils.db_helpers import save_codebook

# --- Default Codebook Definitions ---
DEFAULT_CODEBOOK = {
    'push_factors': [
        {
            'name': 'Acute Side Effects',
            'definition': 'Immediate negative reactions to caffeine or prescription stimulants',
            'examples': 'Jitters, anxiety, palpitations, sleep disruption, crashes',
            'frequency': 0,
            'metadata': {
                'id': 'PUSH-01',
                'include': 'Jitters, anxiety, palpitations, sleep disruption, crashes',
                'exclude': 'Long-term health concerns (→ PUSH-04)',
                'source': 'Fuentes et al. (2024); Dresler et al. (2019); Saiz Garcia et al. (2017)'
            }
        },
        {
            'name': 'Tolerance',
            'definition': 'Diminishing effectiveness requiring dose escalation',
            'examples': '"Doesn\'t work anymore," needing more, reduced response',
            'frequency': 0,
            'metadata': {
                'id': 'PUSH-02',
                'include': '"Doesn\'t work anymore," needing more, reduced response',
                'exclude': 'Dependency language (→ PUSH-03)',
                'source': 'Sharif et al. (2021); Dresler et al. (2019); Cappelletti et al. (2015)'
            }
        },
        {
            'name': 'Dependency/Withdrawal',
            'definition': 'Concern about physical or psychological dependence',
            'examples': 'Withdrawal symptoms, "hooked," cannot function without',
            'frequency': 0,
            'metadata': {
                'id': 'PUSH-03',
                'include': 'Withdrawal symptoms, "hooked," cannot function without',
                'exclude': 'General efficacy doubt (→ PUSH-05)',
                'source': 'Cappelletti et al. (2015) — "cognitive benefits linked to alleviating withdrawal"; Schifano et al. (2022)'
            }
        },
        {
            'name': 'Health Risk Perception',
            'definition': 'Concern about long-term health consequences',
            'examples': 'Cardiovascular fears, neurological damage, unsustainability',
            'frequency': 0,
            'metadata': {
                'id': 'PUSH-04',
                'include': 'Cardiovascular fears, neurological damage, unsustainability',
                'exclude': 'Acute side effects (→ PUSH-01)',
                'source': 'Urban & Gao (2014); Saiz Garcia et al. (2017); Wilms et al. (2019)'
            }
        },
        {
            'name': 'Efficacy Uncertainty',
            'definition': 'Doubt that enhancers actually improve cognition',
            'examples': 'Placebo suspicion, "doesn\'t really help," variable response',
            'frequency': 0,
            'metadata': {
                'id': 'PUSH-05',
                'include': 'Placebo suspicion, "doesn\'t really help," variable response',
                'exclude': 'Tolerance (→ PUSH-02)',
                'source': 'Dresler et al. (2019) — "illusional efficacy"; Bowman et al. (2023) — "smart drugs increase effort level but decrease quality"'
            }
        },
        {
            'name': 'Cost/Access Barriers',
            'definition': 'Financial or legal barriers to conventional enhancers',
            'examples': 'Prescription requirements, expense, legality',
            'frequency': 0,
            'metadata': {
                'id': 'PUSH-06',
                'include': 'Prescription requirements, expense, legality',
                'exclude': 'Natural nootropic costs (→ MOOR-I02)',
                'source': 'Cavaco et al. (2022); Jones & Newton (2024)'
            }
        },
        {
            'name': 'Ethical Objections',
            'definition': 'Moral discomfort with pharmaceuticals or authenticity',
            'examples': 'Big pharma distrust, "unnatural," cheating concerns',
            'frequency': 0,
            'metadata': {
                'id': 'PUSH-07',
                'include': 'Big pharma distrust, "unnatural," cheating concerns',
                'exclude': 'General enhancement ethics (→ MOOR-I06)',
                'source': 'Keary et al. (2023); Schelle et al. (2014); Franke et al. (2012)'
            }
        }
    ],
    'pull_factors': [
        {
            'name': 'Naturalness',
            'definition': 'Valuing "natural," "plant-based," "clean" products',
            'examples': 'Botanical preference, non-synthetic, organic',
            'frequency': 0,
            'metadata': {
                'id': 'PULL-01',
                'include': 'Botanical preference, non-synthetic, organic',
                'exclude': 'Safety claims without naturalness framing (→ PULL-02)',
                'source': 'Roe & Venkataraman (2021); Chiba & Tanemura (2022) — "safe because made from natural ingredients"'
            }
        },
        {
            'name': 'Perceived Safety',
            'definition': 'Belief that natural nootropics are safer',
            'examples': '"Fewer side effects," gentler, non-toxic',
            'frequency': 0,
            'metadata': {
                'id': 'PULL-02',
                'include': '"Fewer side effects," gentler, non-toxic',
                'exclude': 'Efficacy claims (→ PULL-03)',
                'source': 'O\'Hara et al. (2023) — natural nootropics as "safer brain boosters"; Schifano et al. (2022)'
            }
        },
        {
            'name': 'Sustainable Benefits',
            'definition': 'Smooth, sustained effects without crash cycles',
            'examples': '"No crash," cumulative benefits, lasting effects',
            'frequency': 0,
            'metadata': {
                'id': 'PULL-03',
                'include': '"No crash," cumulative benefits, lasting effects',
                'exclude': 'Immediate energy claims',
                'source': 'Grebow (2022) — "shift away from caffeine toward nootropics driven by sustainable cognitive support"'
            }
        },
        {
            'name': 'Holistic Integration',
            'definition': 'Linking cognitive enhancement to broader wellness',
            'examples': 'Sleep, mood, stress, adaptogens, "whole body"',
            'frequency': 0,
            'metadata': {
                'id': 'PULL-04',
                'include': 'Sleep, mood, stress, adaptogens, "whole body"',
                'exclude': 'Single-function claims (→ PULL-07)',
                'source': 'Roe & Venkataraman (2021); Pop et al. (2024)'
            }
        },
        {
            'name': 'Community Endorsement',
            'definition': 'Peer recommendations driving attraction',
            'examples': '"Everyone recommends," stack sharing, trusted reviews',
            'frequency': 0,
            'metadata': {
                'id': 'PULL-05',
                'include': '"Everyone recommends," stack sharing, trusted reviews',
                'exclude': 'Scientific citation (→ information seeking)',
                'source': 'Cox & Piatkowski (2024); Catalani et al. (2021)'
            }
        },
        {
            'name': 'Neuroprotection',
            'definition': 'Long-term brain health and decline prevention',
            'examples': 'Protective, longevity, preventive',
            'frequency': 0,
            'metadata': {
                'id': 'PULL-06',
                'include': 'Protective, longevity, preventive',
                'exclude': 'Immediate performance (→ PULL-07)',
                'source': 'Possemis et al. (2024); Malík & Tlustoš (2022)'
            }
        },
        {
            'name': 'Cognitive Specificity',
            'definition': 'Targeting specific functions (memory, focus, creativity)',
            'examples': '"For focus," memory enhancement, domain-specific',
            'frequency': 0,
            'metadata': {
                'id': 'PULL-07',
                'include': '"For focus," memory enhancement, domain-specific',
                'exclude': 'General "brain boost" (→ PULL-01)',
                'source': 'Suliman et al. (2016); Fuentes et al. (2024)'
            }
        }
    ],
    'mooring_factors': [
        # facilitators
        {
            'name': 'Community Information',
            'definition': 'Online communities reduce uncertainty',
            'examples': '"Found answers here," protocols, harm reduction',
            'frequency': 0,
            'metadata': {
                'id': 'MOOR-F01',
                'include': '"Found answers here," protocols, harm reduction',
                'exclude': '',
                'source': 'Cox & Piatkowski (2024); Bouzoubaa et al. (2023); Krohn & Weninger (2022)'
            }
        },
        {
            'name': 'OTC Accessibility',
            'definition': 'Easy access facilitates switching',
            'examples': 'No prescription, online ordering, store availability',
            'frequency': 0,
            'metadata': {
                'id': 'MOOR-F02',
                'include': 'No prescription, online ordering, store availability',
                'exclude': '',
                'source': 'Fuentes et al. (2024); Turnock & Gibbs (2023)'
            }
        },
        {
            'name': 'Health Consciousness',
            'definition': 'Proactive health orientation drives change',
            'examples': 'Biohacking identity, wellness pursuit',
            'frequency': 0,
            'metadata': {
                'id': 'MOOR-F03',
                'include': 'Biohacking identity, wellness pursuit',
                'exclude': '',
                'source': 'Roe & Venkataraman (2021); Hamilton (2018)'
            }
        },
        {
            'name': 'Low Switching Costs',
            'definition': 'Transition perceived as easy or reversible',
            'examples': '"Easy to try," low commitment',
            'frequency': 0,
            'metadata': {
                'id': 'MOOR-F04',
                'include': '"Easy to try," low commitment',
                'exclude': '',
                'source': 'Wu et al. (2017); Marx (2025)'
            }
        },
        # inhibitors
        {
            'name': 'Habit/Inertia',
            'definition': 'Routines anchor users to conventional enhancers',
            'examples': 'Coffee ritual, "hard to change"',
            'frequency': 0,
            'metadata': {
                'id': 'MOOR-I01',
                'include': 'Coffee ritual, "hard to change"',
                'exclude': '',
                'source': 'Marx (2025); Krishnan & Raghuram (2024)'
            }
        },
        {
            'name': 'Financial Costs',
            'definition': 'Financial barriers to natural alternatives',
            'examples': 'Supplement expense, "too expensive"',
            'frequency': 0,
            'metadata': {
                'id': 'MOOR-I02',
                'include': 'Supplement expense, "too expensive"',
                'exclude': '',
                'source': 'Marx (2025): β = −0.150'
            }
        },
        {
            'name': 'Learning Costs',
            'definition': 'Cognitive effort to understand new substances',
            'examples': 'Complexity, research burden',
            'frequency': 0,
            'metadata': {
                'id': 'MOOR-I03',
                'include': 'Complexity, research burden',
                'exclude': '',
                'source': 'Bansal et al. (2005); Cox & Piatkowski (2024)'
            }
        },
        {
            'name': 'Information Asymmetry',
            'definition': 'Doubt from unverified claims or conflicting information',
            'examples': '"Don\'t know what to trust," lack of research',
            'frequency': 0,
            'metadata': {
                'id': 'MOOR-I04',
                'include': '"Don\'t know what to trust," lack of research',
                'exclude': '',
                'source': 'Fuentes et al. (2024); Napoletano et al. (2020); Nugroho & Wang (2023)'
            }
        },
        {
            'name': 'Social Stigma',
            'definition': 'Peer scepticism or professional stigma',
            'examples': '"People think it\'s weird," workplace concerns',
            'frequency': 0,
            'metadata': {
                'id': 'MOOR-I05',
                'include': '"People think it\'s weird," workplace concerns',
                'exclude': '',
                'source': 'Champagne et al. (2019); Jones & Newton (2024); Janssen et al. (2018)'
            }
        },
        {
            'name': 'Ethical Concerns',
            'definition': 'Moral hesitation about enhancement',
            'examples': '"Is this cheating?", fairness',
            'frequency': 0,
            'metadata': {
                'id': 'MOOR-I06',
                'include': '"Is this cheating?", fairness',
                'exclude': 'Pharmaceutical-specific objections (→ PUSH-07)',
                'source': 'Keary et al. (2023); Bárd (2023); Schelle et al. (2014)'
            }
        }
    ],
    'emergent_themes': []
}

def render():
    st.header("📖 Codebook: Caffeine to Brain Boosts")
    
    st.info("""
    **MSc Thesis Codebook**: Using Online Communities to Understand the Nootropics Market.
    
    This codebook documents the a priori coding framework for thematic analysis of r/Nootropics and r/StackAdvice discourse, operationalising **PPM theory** (Push-Pull-Mooring) for qualitative application.
    
    **PPM Framework Validated in Health Contexts:**
    (Adjie et al., 2023; Nugroho & Wang, 2023; Lai & Wang, 2015)
    """)
    
    with st.expander("📋 Coding Guidelines & Procedure", expanded=False):
        st.markdown("""
        **Procedure**:
        1. Read full post for context
        2. Apply all relevant codes (multi-label)
        3. Code at utterance level
        4. Flag ambiguous cases
        5. Record emergent themes

        **Rules**:
        - Code both push and pull if both present
        - Mooring co-occurs with push/pull
        - Prioritise manifest content

        **Quality**:
        - κ ≥ 0.70 per PPM level
        - Reliability check every 50 posts
        - Document all revisions
        """)
    
    # Initialize/Reset Logic
    if 'codebook' not in st.session_state or not any(st.session_state.codebook.values()):
        if st.button("🚀 Initialize Thesis Codebook Details"):
            st.session_state.codebook = DEFAULT_CODEBOOK
            save_codebook(st.session_state.codebook, st.session_state.session_id)
            st.success("Codebook populated with thesis definitions!")
            st.rerun()
    
    st.divider()
    
    tab1, tab2, tab3, tab4 = st.tabs(["📚 View Codebook", "➕ Add/Edit Codes", "💾 Export Codebook", "📖 References"])
    
    with tab1:
        st.subheader("Current Codebook")
        
        # Helper to render a category
        def render_category(title, codes, description):
            st.markdown(f"### {title}")
            st.markdown(description)
            if codes:
                for code in codes:
                    meta = code.get('metadata', {})
                    code_id = meta.get('id', 'N/A')
                    with st.expander(f"**[{code_id}]** {code['name']}"):
                        st.markdown(f"**Definition:** {code['definition']}")
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            if meta.get('include'):
                                st.markdown(f"**✅ Include:** {meta['include']}")
                        with c2:
                            if meta.get('exclude'):
                                st.markdown(f"**❌ Exclude:** {meta['exclude']}")
                                
                        if code.get('examples'):
                            st.markdown(f"**📝 Examples:**\n{code['examples']}")
                            
                        if meta.get('source'):
                            st.caption(f"**📚 Source:** {meta['source']}")
                            
                        st.markdown(f"**Frequency:** `{code.get('frequency', 0)}` occurrences")
            else:
                st.caption("No codes defined yet.")
            st.markdown("---")

        col1, col2 = st.columns(2)
        
        with col1:
            render_category(
                "Push Factors", 
                st.session_state.codebook['push_factors'], 
                "**Dissatisfaction drivers.** Negative factors pushing consumers from conventional enhancers. Dissatisfaction correlates with switching intention (β = 0.227; Marx, 2025)."
            )
            
            render_category(
                "Pull Factors", 
                st.session_state.codebook['pull_factors'], 
                "**Alternative attractiveness.** Positive factors drawing consumers toward natural nootropics. Strongest predictor of switching (β = 0.416; Marx, 2025)."
            )
        
        with col2:
            render_category(
                "Mooring Factors", 
                st.session_state.codebook['mooring_factors'], 
                "**Facilitators and inhibitors.** Personal and contextual factors that encourage or impede switching. Operate bidirectionally (Bansal et al., 2005; Wu et al., 2017)."
            )
            
            render_category(
                "Emergent Themes", 
                st.session_state.codebook['emergent_themes'], 
                "**Inductive codes** that emerge from your data during analysis."
            )
        
        if st.button("📊 Update Frequencies from Data"):
            update_code_frequencies()
            st.success("✅ Frequencies updated!")
            st.rerun()
            
        with st.expander("⚠️ Reset Codebook"):
            if st.button("Reset to Default Thesis Codebook", type="primary"):
                st.session_state.codebook = DEFAULT_CODEBOOK
                save_codebook(st.session_state.codebook, st.session_state.session_id)
                st.success("Reset complete.")
                st.rerun()
    
    with tab2:
        st.subheader("Add or Edit Code")
        
        code_category = st.selectbox(
            "Code Category",
            ["Push Factors", "Pull Factors", "Mooring Factors", "Emergent Themes"]
        )
        
        c1, c2 = st.columns([1, 3])
        with c1:
            code_id = st.text_input("Code ID", placeholder="e.g. PUSH-01")
        with c2:
            code_name = st.text_input("Label (Name)", placeholder="Short descriptive name")
            
        code_definition = st.text_area("Definition", placeholder="Operational criteria")
        
        c3, c4 = st.columns(2)
        with c3:
            code_include = st.text_area("Include Criteria", placeholder="What qualifies?")
        with c4:
            code_exclude = st.text_area("Exclude Criteria", placeholder="What does not?")
            
        code_examples = st.text_area("Examples (Reddit Excerpt)", placeholder="Paste example quote here")
        code_source = st.text_input("Source (Literature Basis)", placeholder="e.g. Roggiero (2022)")
        
        if st.button("💾 Save Code", type="primary"):
            if code_name and code_definition:
                new_code = {
                    'name': code_name,
                    'definition': code_definition,
                    'examples': code_examples,
                    'added_at': datetime.now().isoformat(),
                    'frequency': 0,
                    'metadata': {
                        'id': code_id,
                        'include': code_include,
                        'exclude': code_exclude,
                        'source': code_source
                    }
                }
                
                category_key = {
                    'Push Factors': 'push_factors',
                    'Pull Factors': 'pull_factors',
                    'Mooring Factors': 'mooring_factors',
                    'Emergent Themes': 'emergent_themes'
                }[code_category]
                
                # Check for existing update by name
                existing_names = [c['name'] for c in st.session_state.codebook[category_key]]
                if code_name in existing_names:
                    idx = existing_names.index(code_name)
                    # Preserve frequency
                    new_code['frequency'] = st.session_state.codebook[category_key][idx].get('frequency', 0)
                    st.session_state.codebook[category_key][idx] = new_code
                    st.success(f"✅ Updated code '{code_name}'")
                else:
                    st.session_state.codebook[category_key].append(new_code)
                    st.success(f"✅ Added new code '{code_name}'")
                
                save_codebook(st.session_state.codebook, st.session_state.session_id)
                st.rerun()
            else:
                st.error("⚠️ Name and Definition are required.")
                
        st.divider()
        with st.expander("🗑️ Delete Code"):
            del_cat = st.selectbox("Category", ["Push Factors", "Pull Factors", "Mooring Factors", "Emergent Themes"], key="del_cat")
            cat_key = del_cat.lower().replace(" ", "_")
            
            codes_in_cat = st.session_state.codebook[cat_key]
            if codes_in_cat:
                code_to_del = st.selectbox("Select Code", [c['name'] for c in codes_in_cat])
                if st.button("Delete Selected Code"):
                    st.session_state.codebook[cat_key] = [c for c in codes_in_cat if c['name'] != code_to_del]
                    save_codebook(st.session_state.codebook, st.session_state.session_id)
                    st.success(f"Deleted {code_to_del}")
                    st.rerun()
            else:
                st.write("No codes in this category.")

    with tab3:
        st.subheader("Export Codebook (Thesis Appendix Format)")
        
        format_opt = st.selectbox("Format", ["Markdown (Detailed)", "CSV (Table)", "JSON"])
        
        if st.button("📥 Generate Export"):
            if format_opt == "Markdown (Detailed)":
                md = f"# Codebook: Caffeine to Brain Boosts\n**Generated:** {datetime.now()}\n\n"
                
                for cat, codes in st.session_state.codebook.items():
                    md += f"## {cat.replace('_', ' ').title()}\n\n"
                    if not codes: md += "*No codes.*\n\n"
                    for c in codes:
                        meta = c.get('metadata', {})
                        md += f"### {meta.get('id', '')} {c['name']}\n"
                        md += f"**Definition:** {c['definition']}\n\n"
                        if meta.get('include'): md += f"- **Include:** {meta['include']}\n"
                        if meta.get('exclude'): md += f"- **Exclude:** {meta['exclude']}\n"
                        if c.get('examples'): md += f"- **Example:** {c['examples']}\n"
                        if meta.get('source'): md += f"- **Source:** {meta['source']}\n"
                        md += "\n---\n"
                        
                st.download_button("Download Markdown", md, "codebook.md")
                
            elif format_opt == "CSV (Table)":
                rows = []
                for cat, codes in st.session_state.codebook.items():
                    for c in codes:
                        meta = c.get('metadata', {})
                        rows.append({
                            'Category': cat,
                            'ID': meta.get('id'),
                            'Label': c['name'],
                            'Definition': c['definition'],
                            'Include': meta.get('include'),
                            'Exclude': meta.get('exclude'),
                            'Example': c.get('examples'),
                            'Source': meta.get('source'),
                            'Frequency': c.get('frequency', 0)
                        })
                df = pd.DataFrame(rows)
                st.download_button("Download CSV", df.to_csv(index=False), "codebook.csv")
                
            elif format_opt == "JSON":
                st.download_button("Download JSON", json.dumps(st.session_state.codebook, indent=2), "codebook.json")

    with tab4:
        st.header("Key Sources")
        
        st.markdown("### PPM Framework")
        st.markdown("""
        - **Marx, T. (2025).** Meta-analytical review. *JSTP, 35*(7).
        - **Krishnan, G., & Raghuram, J. N. V. (2024).** Systematic review. *Multidisciplinary Reviews*.
        - **Bansal, H. S., et al. (2005).** *JAMS, 33*(1), 96-115.
        - **Wu, K., et al. (2017).** Cloud storage switching. *Information & Management*.
        - **Adjie, E. A., et al. (2023).** E-pharmacy switching. *Informatics in Medicine Unlocked, 43*.
        - **Nugroho, A., & Wang, W.-T. (2023).** AR switching. *Computers in Human Behavior, 142*.
        """)
        
        st.markdown("### Enhancement Context")
        st.markdown("""
        - **Dresler, M., et al. (2019).** Hacking the brain. *ACS Chemical Neuroscience, 10*.
        - **Schifano, F., et al. (2022).** Smart drugs. *Drugs, 82*(6).
        - **Sharif, S., et al. (2021).** University students. *Brain Sciences, 11*(3).
        - **Cappelletti, S., et al. (2015).** Caffeine. *Current Neuropharmacology, 13*.
        - **Fuentes, J. B., et al. (2024).** Internet marketing. *PharmaNutrition, 27*.
        - **Urban, K. R., & Gao, W.-J. (2014).** Brain plasticity. *Frontiers in Systems Neuroscience*.
        - **Bowman, E., et al. (2023).** Smart drugs RCT. *Science Advances*.
        - **Saiz Garcia, H., et al. (2017).** Clinical challenges. *European Psychiatry, 41*.
        - **Suliman, N. A., et al. (2016).** Nootropics. *Evidence-Based Complementary Medicine*.
        - **Possemis, N., et al. (2024).** CILTEP elderly. *Journal of Cognitive Enhancement*.
        """)
        
        st.markdown("### Consumer Perception")
        st.markdown("""
        - **Roe, A. L., & Venkataraman, A. (2021).** Botanicals. *Current Neuropharmacology, 19*.
        - **Keary, S., et al. (2023).** Irish students.
        - **Chiba, T., & Tanemura, N. (2022).** Supplement perception. *Nutrients, 14*.
        - **O'Hara, R. B., et al. (2023).** Nootropics vs stimulants. *BJSTR*.
        - **Grebow, J. (2022).** Gen Z brain health. *Nutritional Outlook*.
        - **Bárd, I. (2023).** Neuroenhancement acceptability. PhD thesis, LSE.
        """)
        
        st.markdown("### Online Community/Reddit")
        st.markdown("""
        - **Cox, J., & Piatkowski, T. (2024).** Nootropic influencers. *ETDAH*.
        - **Bouzoubaa, L., et al. (2024).** Reddit narratives. *arXiv:2406.12117*.
        - **Kozinets, R. V., & Gretzel, U. (2024).** Netnography evolved. *Annals of Tourism Research, 104*.
        - **Catalani, V., et al. (2021).** Sport supplement netnography. *ETDAH, 1*.
        - **Krohn, R., & Weninger, T. (2022).** Subreddit links. *ICWSM*.
        - **Pop, I. A., et al. (2024).** Microdosing Reddit. *Social Science & Medicine, 347*.
        """)

        st.markdown("### Methodology/Ethics")
        st.markdown("""
        - **Braun, V., & Clarke, V. (2006).** Thematic analysis. *Qualitative Research in Psychology, 3*(2).
        - **McDermott, H., et al. (2020).** Working smart UK students.
        - **Roggiero, L. (2022).** Instagram health claims. Premaster thesis.
        - **Hamilton, M. (2018).** Cognitive enhancement advertising. MA thesis, Cincinnati.
        - **Benschop, A., et al. (2020).** NPS motives. *J Psychopharmacology, 34*(6).
        """)

def update_code_frequencies():
    """Recalculate frequency of each code based on coded data."""
    # 1. Reset all frequencies to 0
    for category in ['push_factors', 'pull_factors', 'mooring_factors', 'emergent_themes']:
        if category in st.session_state.codebook:
            for code in st.session_state.codebook[category]:
                code['frequency'] = 0
            
    # 2. Iterate through all coded items
    if not st.session_state.coded_data:
        return

    for item in st.session_state.coded_data:
        # A. Count PPM Subcodes (Push, Pull, Mooring)
        # ppm_subcodes list usually contains strings like "PUSH-01: Acute Side Effects" or just "Acute Side Effects"
        for subcode_str in item.get('ppm_subcodes', []):
            subcode_lower = subcode_str.lower()
            
            for category in ['push_factors', 'pull_factors', 'mooring_factors']:
                if category in st.session_state.codebook:
                    for code in st.session_state.codebook[category]:
                        # Match 1: ID matches (e.g. "PUSH-01" in "PUSH-01: ...")
                        code_id = code.get('metadata', {}).get('id', '').lower()
                        if code_id and code_id in subcode_lower:
                            code['frequency'] += 1
                            continue # match found for this code
                        
                        # Match 2: Name matches (e.g. "Acute Side Effects" in string)
                        if code['name'].lower() in subcode_lower:
                            code['frequency'] += 1
                        
        # B. Count Emergent Themes
        for theme_str in item.get('themes', []):
            theme_lower = theme_str.lower()
            if 'emergent_themes' in st.session_state.codebook:
                for code in st.session_state.codebook['emergent_themes']:
                    if code['name'].lower() in theme_lower:
                        code['frequency'] += 1
