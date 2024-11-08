#!/bin/bash
set -e

# Create AppDir structure
mkdir -p AppDir/usr/{bin,lib,python,share}

# Install Python and dependencies
python3.13 -m venv AppDir/usr/python
source AppDir/usr/python/bin/activate
pip install --no-cache-dir -e /src[help,browser]

# Copy system libraries
copy_dependencies() {
    ldd "$1" | grep "=> /" | awk '{print $3}' | xargs -I '{}' cp -v '{}' AppDir/usr/lib/
}

# Copy Python binary and its dependencies
cp $(which python3.13) AppDir/usr/bin/
copy_dependencies $(which python3.13)

# Create entry point script
cat > AppDir/AppRun << 'EOF'
#!/bin/bash
HERE=$(dirname "$(readlink -f "${0}")")
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
export PYTHONHOME="${HERE}/usr/python"
export PYTHONPATH="${HERE}/usr/python/lib/python3.13/site-packages"
exec "${HERE}/usr/bin/python3.13" -m brade "$@"
EOF
chmod +x AppDir/AppRun

# Create desktop file
cat > AppDir/brade.desktop << EOF
[Desktop Entry]
Name=Brade
Exec=brade
Icon=brade
Type=Application
Categories=Development;
EOF

# Download icon (placeholder - replace with actual icon)
curl -L https://raw.githubusercontent.com/deansher/brade/main/assets/icon.png -o AppDir/brade.png
ln -sf brade.png AppDir/.DirIcon

# Generate AppImage
ARCH=$(uname -m) appimagetool AppDir/
