# Academic Research Tool: Natural Cognitive Supplement Market Segmentation

A specialized research tool designed for qualitative analysis of Reddit data, focusing on the "Nootropics" market using the Push-Pull-Mooring (PPM) framework. This application integrates data scraping, Local LLM-assisted thematic coding, and an interactive dashboard for academic research.

## 🚀 Features

- **Reddit Data Collection**: Targeted scraping of subreddits (e.g., r/Nootropics) using `praw`.
- **LLM-Assisted Coding**: Automated qualitative coding using local LLMs (via Ollama) to identify Push, Pull, Mooring factors, and Emergent Themes.
- **Interactive Dashboard**: Visualizes data through topic modeling, factor frequency analysis, and temporal trends using Streamlit.
- **Codebook Management**: Tools to manage and refine qualitative codebooks.
- **Data Export**: Export functionality for audit trails (CSV/JSON) and Zotero integration for literature review.
- **Privacy & Replicability**: Designed to run locally with open-source models for data privacy and academic reproducibility.

## 🛠️ Installation

### Prerequisites

- Python 3.11 or higher
- [Ollama](https://ollama.com/) installed and running (for LLM features)

### Setup

1. **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd ScrapeSenseLLM
    ```

2. **Create and activate a virtual environment:**

    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate
    ```

3. **Install dependencies:**

    ```bash
    pip install .
    # OR if using requirements directly
    pip install -r requirements.txt # (If available, otherwise use pip install .)
    ```

    *Note: Dependencies are managed via `pyproject.toml`.*

4. **Model Setup (Packaging):**
    Ensure the required models (`llama3.1`, `gemma3:12b`) are installed:

    ```bash
    python setup_models.py
    ```

5. **Environment Configuration:**
    Create a `.env` file in the root directory (copy `.env.example` if it exists) and add your Reddit API credentials:

    ```env
    REDDIT_CLIENT_ID=your_client_id
    REDDIT_CLIENT_SECRET=your_client_secret
    REDDIT_USER_AGENT=your_user_agent
    ```

## 🖥️ Usage

1. **Start Ollama** (if using LLM features):
    Ensure your Ollama instance is running (default `http://localhost:11434`).

2. **Run the Application:**

    ```bash
    streamlit run app.py
    ```

3. **Navigate the App:**
    - **Dashboard**: Overview of collected data and analysis.
    - **Reddit Data Collection**: Fetch new discussions from Reddit.
    - **LLM-Assisted Coding**: Process raw data into coded themes.
    - **Codebook Management**: View and edit the coding schema.
    - **Data Export & Audit**: Download datasets and audit logs.

## 📂 Project Structure

```
ScrapeSenseLLM/
├── app.py                 # Main Streamlit application entry point
├── database.py            # Database initialization and connection
├── pyproject.toml         # Project dependencies and configuration
├── CITATION.cff           # Citation metadata
├── modules/               # Core functionality modules
│   ├── reddit_scraper.py  # Reddit data fetching logic
│   ├── llm_coder.py       # Interface with Ollama for coding
│   ├── dashboard.py       # Visualization components
│   ├── codebook.py        # Codebook management logic
│   └── ...
├── utils/                 # Utility functions (database helpers, etc.)
└── data/                  # Local storage for data (if applicable)
```

## 📄 License

See [LICENSE](LICENSE) file for details.
