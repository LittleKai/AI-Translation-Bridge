import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

class PyInstallerBuilderFixed:
    """Build AIBridge with PyInstaller - Fixed for numpy/pandas"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.app_name = "AI Translation Bridge"
        self.app_filename = "AI_Translation_Bridge"
        self.version = "1.0.0"

    def check_requirements(self):
        """Check and install PyInstaller"""
        print("Checking requirements...")
        try:
            import PyInstaller
            print(f"✓ PyInstaller version: {PyInstaller.__version__}")
        except ImportError:
            print("Installing PyInstaller...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])

        return True

    def clean_old_builds(self):
        """Clean previous builds"""
        print("\nCleaning old builds...")
        for folder in ['build', 'dist']:
            folder_path = self.project_root / folder
            if folder_path.exists():
                shutil.rmtree(folder_path)
                print(f"  Removed: {folder}")

    def create_minimal_spec(self):
        """Create optimized spec file that works with numpy/pandas"""

        icon_path = self.project_root / "assets" / "icon.ico"
        icon_line = f"icon='{str(icon_path).replace(chr(92), chr(92)*2)}'," if icon_path.exists() else ""

        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=[
        'pkg_resources.extern',
        'pkg_resources.py2_warn',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'pytest', 'IPython', 'notebook'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{self.app_filename}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {icon_line}
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='{self.app_filename}',
)
'''
        spec_file = self.project_root / f"{self.app_filename}.spec"
        spec_file.write_text(spec_content, encoding='utf-8')
        return spec_file

    def build(self):
        """Build with PyInstaller using minimal spec"""
        print("\n" + "="*60)
        print(f"Building {self.app_name} v{self.version}")
        print("Using: PyInstaller with auto-detection")
        print("="*60 + "\n")

        if not self.check_requirements():
            return False

        self.clean_old_builds()
        spec_file = self.create_minimal_spec()

        # Build command - let PyInstaller auto-detect everything
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            str(spec_file)
        ]

        print("Running PyInstaller...")
        print("This may take 3-5 minutes...\n")

        result = subprocess.run(cmd)

        # Clean up spec file
        if spec_file.exists():
            spec_file.unlink()

        if result.returncode == 0:
            print("\n" + "="*60)
            print("✓ Build completed!")
            print("="*60)

            # Move to releases
            dist_dir = self.project_root / "dist" / self.app_filename
            if dist_dir.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                releases_dir = self.project_root / "releases"
                releases_dir.mkdir(exist_ok=True)

                final_dir = releases_dir / f"{self.app_filename}_{self.version}_{timestamp}"

                if final_dir.exists():
                    shutil.rmtree(final_dir)

                shutil.copytree(dist_dir, final_dir)

                # Rename exe
                old_exe = final_dir / f"{self.app_filename}.exe"
                new_exe = final_dir / f"{self.app_name}.exe"
                if old_exe.exists() and old_exe != new_exe:
                    old_exe.rename(new_exe)

                # Ensure assets are copied
                assets_dst = final_dir / "assets"
                assets_src = self.project_root / "assets"
                if assets_src.exists():
                    if assets_dst.exists():
                        shutil.rmtree(assets_dst)
                    shutil.copytree(assets_src, assets_dst)

                print(f"\n✓ Release created: {final_dir}")
                print(f"  Executable: {new_exe}")

                if new_exe.exists():
                    size_mb = new_exe.stat().st_size / (1024 * 1024)
                    print(f"  Size: {size_mb:.1f} MB")

                # Clean up
                build_dir = self.project_root / "build"
                dist_dir_root = self.project_root / "dist"
                for folder in [build_dir, dist_dir_root]:
                    if folder.exists():
                        shutil.rmtree(folder)

                return True
            else:
                print("✗ Output directory not found")
                return False
        else:
            print("\n✗ Build failed")
            return False

if __name__ == "__main__":
    builder = PyInstallerBuilderFixed()
    success = builder.build()

    print("\n" + "="*60)
    if success:
        print("✓✓✓ BUILD SUCCESS ✓✓✓")
    else:
        print("✗✗✗ BUILD FAILED ✗✗✗")
    print("="*60)

    input("\nPress Enter to exit...")