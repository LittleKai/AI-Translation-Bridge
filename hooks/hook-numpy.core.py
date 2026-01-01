from PyInstaller.utils.hooks import collect_dynamic_libs, collect_data_files

# Collect only compiled binaries, not source files
binaries = collect_dynamic_libs('numpy.core')
datas = collect_data_files('numpy.core', include_py_files=False)

# Don't collect .py source files to prevent import errors
hiddenimports = [
    'numpy.core._multiarray_umath',
    'numpy.core._multiarray_tests',
]