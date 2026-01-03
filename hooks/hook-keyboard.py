
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all jaraco submodules needed by keyboard
hiddenimports = collect_submodules('jaraco')
hiddenimports += collect_submodules('keyboard')
datas = collect_data_files('jaraco', include_py_files=True)
