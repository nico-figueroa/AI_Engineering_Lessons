# AI Engineering Lessons
A collection of explorations, experiments, and learning projects focused on artificial intelligence, machine learning, and modern AI tooling. This repository reflects my progression in understanding, building, refactoring, and deploying AI‑powered applications — sometimes independently, sometimes assisted by AI systems like Copilot.

## 📘 About This Repository
The lessons and learnings demonstrate my ability to work with AI frameworks, RAG pipelines, vector stores, and cloud‑hosted AI applications. Some projects follow structured learning paths (Codecademy, Microsoft Learn, tutorials, guided labs).

All licenses and source materials are respected and referenced when appropriate. Contents may be reused under an open license.
![License: MIT](https://img.shields.io/badge/License-MIT-yellow)

## 📂 Main Projects

### Microsoft Learn — Azure RAG Deployment Archive

[Project summary, architecture, deployment inventory, and recorded changes](./my-intelligent-app/README.md)
from my exercise deploying the Microsoft Azure Search + OpenAI sample to Azure
Container Apps. This is a curated historical portfolio archive, not a runnable
copy of the upstream application.

As of October 15, 2026, I report that the
[deployed application endpoint](https://capps-backend-2zusqcpu4spb6.jollyhill-b19bfefa.eastus.azurecontainerapps.io/)
remains available, but the model service has been retired to reduce costs.
UI availability does not establish that AI answers still work. The archive
distinguishes my recorded changes and reported deployment from upstream sample
material and preserves a Git recovery reference.

MCP‑Enabled Web Dashboard
Learning artifact exploring dashboarding concepts with AI assistance.

## 📚 Learning Sources

* Microsoft Learn
* AI‑generated content (primarily Copilot)
* Online documentation and tutorials
* Codecademy — AI Engineer Lessons
* Codecademy — Pytorch Lessons
* Codecademy — Machine Learning Lessons
* Personal experimentation

## 🛠️ Technologies Practiced

* ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
* ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
* ![Azure](https://img.shields.io/badge/Azure-0078D4?logo=microsoftazure&logoColor=white)
* ![RAG](https://img.shields.io/badge/RAG-Pipeline-blue)
* ![AI](https://img.shields.io/badge/AI-Learning-green)

## Python setup on Windows

Keep the Python install manager's `%LOCALAPPDATA%\Python\bin` and
`%LOCALAPPDATA%\Microsoft\WindowsApps` directories on your user PATH.
Graph rendering also requires the Graphviz application (not just its Python
package); its `bin` directory must be on PATH. Restart VS Code after PATH changes.
Avoid copying the machine PATH into the user PATH or using `setx PATH`, which
can truncate long values.

For new projects, use a project-local virtual environment rather than adding
packages to the shared Python installation:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install torch torchviz torchview ipykernel
.\.venv\Scripts\python.exe -m pip check
```

Select that environment as both the VS Code Python interpreter and notebook
kernel. Use `python -m pip install <package>` with the selected interpreter
instead of a bare `pip` command; inside a notebook, `%pip install <package>`
targets its kernel environment. Restart the kernel after package changes.

The architecture diagram in [custom_torchinfo.py](./Codecademy/custom_torchinfo.py)
uses Arial to avoid torchview's missing Linux Libertine font warning on Windows.

## Git and Local Dependencies

Local Postman AI instruction templates matching
`.github/instructions/postman-*.instructions.md` are ignored and stay on your
computer. Other files under `.github/` remain eligible for version control.

For active projects, installed dependencies such as `node_modules/` stay local
and are excluded by `.gitignore`. Commit dependency manifests and lockfiles
instead, and restore dependencies with the project's package manager.
The [Azure project](./my-intelligent-app/README.md) is now a historical archive;
its installed dependencies and runnable sample copy have been removed.
Its README explains how to recover the original tracked source if needed.

An ignore rule does not stop tracking files already committed. If dependencies
are accidentally tracked again, use `git rm -r --cached -- <dependency-folder>`
and commit the removal. `--cached` keeps the installed files on your computer.

Before committing, review `git status` and stage only the intended files. After
committing, use `git push origin main` to publish the changes to GitHub.

## 📨 Contact
Name: Nicolas Figueroa
Email: nico.figueroa.hidalgo@outlook.com
