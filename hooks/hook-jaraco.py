
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = collect_submodules('jaraco')
datas = collect_data_files('jaraco', include_py_files=True)
