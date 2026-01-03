import os
import sys
import shutil
import subprocess
from pathlib import Path
import json
from datetime import datetime

class AIBridgeBuilder:
    """Build AIBridge application to executable (Multi-file Support)"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"

        self.app_name = "AI Translation Bridge"
        self.app_filename = "AI_Translation_Bridge"
        self.version = "1.0.0"

        # CẤU HÌNH BUILD
        self.build_options = {
            'console': False,     # Tắt màn hình đen console
            'onefile': False,     # False = Multi-file (Nhanh & Ổn định)
            'icon': None,
            'upx': True,
            'clean': True
        }

    def check_requirements(self):
        """Check if all required tools are installed"""
        print("Checking requirements...")
        try:
            import PyInstaller
            print(f"✓ PyInstaller version: {PyInstaller.__version__}")
        except ImportError:
            print("✗ PyInstaller not found. Installing...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])

        icon_path = self.project_root / "assets" / "icon.ico"
        if icon_path.exists():
            self.build_options['icon'] = str(icon_path).replace('\\', '\\\\')
            print(f"✓ Icon found: {icon_path}")
        else:
            print("! Icon not found, will use default")
        return True

    def create_spec_file(self):
        """Create PyInstaller spec file for Multi-file mode"""

        icon_line = f"icon='{self.build_options['icon']}'," if self.build_options['icon'] else ""

        version_line = ""
        if (self.project_root / "version_info.txt").exists():
            version_line = "version='version_info.txt',"

        # Configuration for Multi-file mode (OneDir)
        collect_block = f'''
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx={self.build_options['upx']},
    upx_exclude=[],
    name='{self.app_filename}',
)
'''
        # Check if hooks folder exists
        hooks_path_line = ""
        hooks_dir = self.project_root / "hooks"
        if hooks_dir.exists():
            hooks_path_line = f"hookspath=['{str(hooks_dir).replace(chr(92), chr(92)*2)}'],"

        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all submodules for problematic packages
hiddenimports_extra = []
for package in ['jaraco', 'jaraco.text', 'jaraco.functools', 'jaraco.context', 
                'jaraco.classes', 'jaraco.collections', 'keyboard', 'pyperclip',
                'importlib_metadata', 'zipp', 'more_itertools']:
    try:
        hiddenimports_extra.extend(collect_submodules(package))
    except:
        pass

a = Analysis(
    ['main.py'],
    pathex=['{str(self.project_root).replace(chr(92), chr(92)*2)}'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox',
        'pandas', 'pandas._libs', 'pandas._libs.tslibs.timedeltas',
        'pandas._libs.tslibs.np_datetime', 'pandas._libs.tslibs.nattype',
        'pandas._libs.skiplist', 'pandas._libs.hashtable', 'pandas._libs.lib',
        'openpyxl', 'openpyxl.cell', 'openpyxl.cell._writer',
        'numpy', 'numpy.core._multiarray_umath', 'numpy.random',
        'PIL', 'PIL._imaging', 'cv2', 
        'pyautogui', 'pyperclip', 'keyboard',
        'jaraco', 'jaraco.text', 'jaraco.functools', 'jaraco.context',
        'jaraco.classes', 'jaraco.collections',
        'importlib_metadata', 'zipp', 'more_itertools',
        'cryptography', 'cryptography.fernet',
        'requests', 'docx', 'ebooklib', 'bs4', 'lxml', 'html5lib',
        'pkg_resources', 'pkg_resources.py2_warn'
    ] + hiddenimports_extra,
    {hooks_path_line}
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'pytest', 'ipython', 'jupyter', 'IPython', 'notebook'],
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
    upx={self.build_options['upx']},
    console={self.build_options['console']},
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {icon_line}
    {version_line}
)

{collect_block}
'''
        spec_file = self.project_root / f"{self.app_filename}.spec"
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        return spec_file

    def create_version_info(self):
        """Create Windows version information file"""
        version_info = f'''VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x4,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'AIBridge'),
        StringStruct(u'FileDescription', u'AI Translation Bridge Application'),
        StringStruct(u'FileVersion', u'{self.version}'),
        StringStruct(u'InternalName', u'{self.app_filename}'),
        StringStruct(u'OriginalFilename', u'{self.app_name}.exe'),
        StringStruct(u'ProductName', u'AI Translation Bridge'),
        StringStruct(u'ProductVersion', u'{self.version}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
        version_file = self.project_root / "version_info.txt"
        with open(version_file, 'w', encoding='utf-8') as f:
            f.write(version_info)
        return version_file

    def clean_temp_files(self):
        """Clean temporary build files"""
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)

        spec_file = self.project_root / f"{self.app_filename}.spec"
        version_file = self.project_root / "version_info.txt"

        if spec_file.exists(): spec_file.unlink()
        if version_file.exists(): version_file.unlink()

    def build(self):
        """Build the executable"""
        print("\n" + "="*50)
        print(f"Building {self.app_name} v{self.version}")
        print("Type: Multi-file (Folder) - Optimized for Speed")
        print("="*50 + "\n")

        # 1. Dọn dẹp
        self.clean_temp_files()
        if self.dist_dir.exists(): shutil.rmtree(self.dist_dir)

        # 2. Chuẩn bị
        if not self.check_requirements(): return False
        self.create_version_info()
        spec_file = self.create_spec_file()

        # 3. Chạy PyInstaller
        print("\nRunning PyInstaller...")
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", str(spec_file)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ Build completed successfully!")

            # 4. Xử lý Output
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_release_dir = self.project_root / "releases" / f"{self.app_filename}_{self.version}_{timestamp}"
            final_release_dir.mkdir(parents=True, exist_ok=True)

            # Folder gốc do PyInstaller tạo ra
            build_output_dir = self.dist_dir / self.app_filename

            if build_output_dir.exists():
                # Copy toàn bộ nội dung sang folder release
                shutil.copytree(build_output_dir, final_release_dir, dirs_exist_ok=True)

                # Đổi tên file exe cho đẹp
                src_exe = final_release_dir / f"{self.app_filename}.exe"
                dst_exe = final_release_dir / f"{self.app_name}.exe"
                if src_exe.exists() and src_exe != dst_exe:
                    src_exe.rename(dst_exe)

                # --- QUAN TRỌNG: COPY ASSETS ---
                # Đảm bảo folder assets nằm cạnh file exe và là bản mới nhất
                assets_src = self.project_root / "assets"
                assets_dst = final_release_dir / "assets"

                if assets_src.exists():
                    print(f"Syncing assets folder...")
                    # dirs_exist_ok=True sẽ ghi đè file cũ nếu cần
                    shutil.copytree(assets_src, assets_dst, dirs_exist_ok=True)
                    print(f" ✓ Assets verified at: {assets_dst}")

                print(f"\n✓ Release Created: {final_release_dir}")
                print(f"  Main file: {dst_exe}")
                print(f"  Assets dir: {assets_dst}")

            self.clean_temp_files()
            if self.dist_dir.exists(): shutil.rmtree(self.dist_dir)
            return True
        else:
            print("✗ Build failed!")
            print(result.stderr)
            return False

if __name__ == "__main__":
    builder = AIBridgeBuilder()
    builder.build()
