from setuptools import setup

setup(
    name='codex',
    version='0.1',
    py_modules=['main'],
    install_requires=[
        'openai',
        'click',
    ],
    entry_points={
        'console_scripts': [
            'codex=main:code_edit',
        ],
    },
)
