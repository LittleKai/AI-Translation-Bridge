from PyInstaller.utils.hooks import collect_dynamic_libs, collect_data_files

# Collect pandas compiled libraries
binaries = collect_dynamic_libs('pandas')
datas = collect_data_files('pandas', include_py_files=False)

hiddenimports = [
    'pandas._libs.tslibs.np_datetime',
    'pandas._libs.tslibs.nattype',
    'pandas._libs.tslibs.timedeltas',
    'pandas._libs.skiplist',
    'pandas._libs.hashtable',
    'pandas._libs.lib',
]