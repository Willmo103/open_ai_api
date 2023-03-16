from setuptools import setup

setup(
    name='codex',
    version='0.1.1',
    py_modules=['main'],
    data_files=[(".", ['globals.json', '.env'])],
    install_requires=[
        'openai',
        'click',
        'python-dotenv',
    ],
    entry_points={
        'console_scripts': [
            'codex=main:code_edit',
            'codex_ignore=main:code_edit_ignore',
            'mapfiles=main:dir_to_json',
            'generate=main:generate_directory'
        ],
    },
)
