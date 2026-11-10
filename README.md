# ScrapeSenseLLM
A tool designed for qualitative analysis of Reddit data, focusing on the "Nootropics" market using the Push-Pull-Mooring (PPM) framework. This application integrates data scraping, Local LLM-assisted thematic coding, and an interactive dashboard for academic research. 91/100 grade.

The thesis applies the Push-Pull-Mooring (PPM) migration framework to consumers switching from caffeine and stimulants to nootropics. Reddit posts and comments from six communities (2020 to 2025) were coded by a local LLM against a PPM codebook, and each community was placed on a perceptual map.

<img width="1800" height="1300" alt="image" src="https://github.com/user-attachments/assets/dc794760-a39a-4a15-9f2d-c357c0bacaac" />

Certified corpus: 50,044 units (609 submissions, 49,435 comments). The
map uses the 609 submissions.

  Community           N   Balance   Mooring (%) Archetype
  --------------- ----- --------- ------------- --------------------------------------
  r/NooTopics        87    +0.758          29.9 Facilitator-Embedded Wellness Seeker
  r/Supplements     105    +0.450          26.7 Facilitator-Embedded Wellness Seeker
  r/StackAdvice     100    +0.469          23.0 Self-Directed Natural Optimiser
  r/Nootropics      105    +0.381          21.9 Self-Directed Natural Optimiser
  r/Biohackers      105    +0.415          17.1 Self-Directed Natural Optimiser
  r/Decaf           107    +0.091          29.9 Caffeine/Stimulant Escapee

Balance is the push-pull balance, (PULL-PUSH)/(PULL+PUSH). Mooring
is mooring prevalence, the share of submissions with any mooring code.

All six communities read net-pull. r/Decaf is the exception in degree:
push (40) nearly matches pull (48). Mooring then splits the rest,
highest in r/NooTopics and r/Supplements, lowest in r/Biohackers.

Inter-rater agreement was slight (Cohen's kappa 0.115 Llama–researcher, 0.151 Gemma–researcher, 0.047 Llama–Gemma), so the archetypes are an interpretive, community-level reading of the map rather than a measurement.

Method

1.  Collection. BigQuery extraction through the Reddit for Researchers Analytics Hub under a Research Data Addendum. time scope: 1 January 2020 to 31 December 2025. Two retrieval routes, keyword-targeted and high-engagement, pooled. Quality gate: score ≥ 50 and body ≥ 250 characters, r/StackAdvice calibrated to 25 and 50. 660 submissions admitted with their full comment threads; 609 certified after cleaning. Parameters in Appendix B.

2.  Coding. Llama 3.1 via Ollama, local, structured JSON output. 24-code deductive codebook *compiled from existing academic literature, Appendix A. Every allocation stored with source text, evidence quote and confidence rating.

3.  Reliability. Researcher blind-coded 125 submissions, stratified across the six communities. Second rater Gemma 3 12B, reliability stage only. Cohen’s kappa at dimension level: 0.115, 0.151, 0.047. Table 4.3 and Appendix D

4.  Map. Per-community counts frozen to file after data cleaning and was used to render the perception map



The repository holds no Reddit data. A synthetic dataset runs the
pipeline end to end:

    pip install -e .                          # Python 3.11+
    python scripts/verify_install.py
    python scripts/generate_mock_ppm_data.py
    streamlit run app.py

Ollama setup: . Data-agreement compliance: .

Citation

    @software{dolgov2026caffeine,
      author      = {Dolgov, Vladislav},
      title       = {Caffeine to Brain Boosts: A Qualitative Research Instrument for Nootropic Discourse Analysis},
      institution = {Modul University Vienna},
      year        = {2026},
      url         = {https://github.com/Hotpopize/NootropicRedditScrapePPM}
    }

Repository: https://github.com/Hotpopize/NootropicRedditScrapePPM
