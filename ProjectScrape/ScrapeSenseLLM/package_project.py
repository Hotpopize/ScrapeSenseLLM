import os
import zipfile
import datetime

def package_project():
    # Define what to include and exclude
    base_dir = os.getcwd()
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    zip_filename = f"ScrapeSenseLLM_AdvisorBuild_{timestamp}.zip"
    
    # Exclude these directories/files to minimize bloat
    EXCLUDES = {
        '.git', '.venv', '__pycache__', '.pytest_cache', '.vscode', '.idea',
        'nootropics-research-replication', 'attached_assets', 'tests',
        '.local', 'node_modules', '*.zip', '*.pyc', '.DS_Store'
    }

    # Ensure we don't include the output zip in itself or old zips
    print(f"📦 Packaging project into {zip_filename}...")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_dir):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDES and not d.startswith('.')]
            
            for file in files:
                # Skip excluded files and the zip itself
                if file == zip_filename or any(file.endswith(ext) for ext in ['.zip', '.pyc', '.pyo']):
                    continue
                if file.startswith('.'): # Skip hidden files like .env
                    continue
                    
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, base_dir)
                
                print(f"  Adding: {arcname}")
                zipf.write(file_path, arcname)
    
    print(f"\n✅ Build complete: {zip_filename}")
    print(f"   Size: {os.path.getsize(zip_filename) / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    package_project()
