import requests
import sys
import subprocess
import time

# Defined "packaged" models for this project
REQUIRED_MODELS = [
    "llama3.1",
    "gemma3:12b"
]

OLLAMA_API = "http://localhost:11434/api"

def check_ollama_running():
    try:
        requests.get(f"{OLLAMA_API}/tags", timeout=2)
        return True
    except:
        return False

def get_installed_models():
    try:
        response = requests.get(f"{OLLAMA_API}/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            return [m['name'] for m in models]
    except Exception as e:
        print(f"Error fetching models: {e}")
    return []

def main():
    print("📦 ScrapeSenseLLM Model Setup")
    print("============================")
    
    # 1. Check Ollama Status
    if not check_ollama_running():
        print("❌ Ollama is NOT running.")
        print("   Please start Ollama (run 'ollama serve' in a separate terminal) and try again.")
        sys.exit(1)
    
    print("✅ Ollama is running.")
    
    # 2. Check Installed Models
    installed = get_installed_models()
    print(f"ℹ️  Found {len(installed)} installed models.")
    
    missing = []
    for model in REQUIRED_MODELS:
        # Check for exact match or match with :latest if implied
        if model not in installed and f"{model}:latest" not in installed:
            missing.append(model)
        else:
            print(f"✅ Model found: {model}")
            
    # 3. Pull Missing Models
    if not missing:
        print("\n🎉 All required models are available!")
        print("   - llama3.1")
        print("   - gemma3:12b")
        print("\nYou can now run the app:")
        print("   streamlit run app.py")
        return

    print(f"\n⚠️  Missing models: {', '.join(missing)}")
    print("   Attempting to pull them now (this may take a while depending on internet speed)...")
    
    for model in missing:
        print(f"\n⬇️  Pulling {model}...")
        try:
            # Use subprocess to stream output
            subprocess.run(["ollama", "pull", model], check=True)
            print(f"✅ Successfully pulled {model}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to pull {model}. Please try manual installation:")
            print(f"   ollama pull {model}")
        except FileNotFoundError:
            print("❌ 'ollama' command not found. Please install the Ollama CLI.")
            sys.exit(1)

    print("\n📦 Model setup complete.")

if __name__ == "__main__":
    main()
