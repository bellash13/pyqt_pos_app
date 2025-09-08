import os
import shutil
import zipfile

EXCLUDE = {
    '.git', '.venv', '__pycache__', 'migrate_database.py', 'test_features.py', 'install_features.bat',
    'pos_backup_20250808_120337.db', 'make_dist.py', '.gitignore', '.gitattributes', '.vscode',
}

INCLUDE_EXT = {'.py', '.db', '.md', '.txt'}
INCLUDE_DIRS = {'views'}

DIST_NAME = 'pyqt_pos_app_dist.zip'


def should_include(file):
    if file in EXCLUDE:
        return False
    if os.path.isdir(file):
        return file in INCLUDE_DIRS
    ext = os.path.splitext(file)[1]
    return ext in INCLUDE_EXT or file in INCLUDE_DIRS


def make_dist():
    base = os.path.dirname(os.path.abspath(__file__))
    dist_path = os.path.join(base, DIST_NAME)
    with zipfile.ZipFile(dist_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(base):
            # Exclure les dossiers
            dirs[:] = [d for d in dirs if d not in EXCLUDE]
            for file in files:
                rel_dir = os.path.relpath(root, base)
                rel_file = os.path.join(rel_dir, file) if rel_dir != '.' else file
                if should_include(file) and not any(x in rel_file for x in EXCLUDE):
                    z.write(os.path.join(root, file), rel_file)
    print(f"Archive créée : {DIST_NAME}")

if __name__ == '__main__':
    make_dist()
