# Project Status & TODOs

## 📌 Current Status

- **Core Functionality**: ✅ Reddit scraping, LLM coding, and Dashboard visualization are implemented.
- **Documentation**: ✅ Initial `README.md` and `CITATION.cff` compliant with academic standards.
- **Dependencies**: ✅ Managed via `pyproject.toml`.

## 📋 To-Do List

### 📝 Documentation & Methodology

- [x] Create `README.md` with setup instructions.
- [ ] Document specific LLM prompt strategies in `docs/`.
- [ ] Create a user guide for non-technical researchers.

### 🧪 Testing & Reliability

- [ ] Add unit tests for `modules/` (especially `llm_coder.py` and `reddit_scraper.py`).
- [ ] Implement validation for Reddit API rate limits handling.
- [ ] Verify database schema consistency during migration/updates.

### ✨ Feature Enhancements

- [ ] **Data Sources**: Add support for other sources beyond Reddit (e.g., specialized forums).
- [ ] **LLM Integration**: Allow selection of different Ollama models via UI.
- [ ] **Dashboard**: Add exportable high-resolution charts for publication.

### 🔧 Maintenance

- [ ] Audit dependencies for security vulnerabilities.
- [ ] Refactor `app.py` if simple routing becomes too complex.
