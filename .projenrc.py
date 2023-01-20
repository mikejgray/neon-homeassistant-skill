from projen.python import PythonProject

project = PythonProject(
    author_email="mike@graywind.org",
    author_name="Mike Gray",
    module_name="neon_homeassistant_skill",
    name="neon-homeassistant-skill",
    version="0.1.0",
    poetry=True,
    dev_deps=[
        "pytest",
        "pylint",
        "flake8",
        "pydocstyle",
        "pycodestyle",
        "black",
        "mypy",
        "bandit",
        "projen",
        "lichecker"
    ],
)

project.synth()
