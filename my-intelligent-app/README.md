# Azure RAG application - deployment learning archive

This is a compact historical portfolio archive of Nicolas Figueroa's exercise
deploying the Microsoft Azure Search + OpenAI sample application to Azure.
It is **not a runnable application checkout** and does not claim authorship of
the Microsoft sample or its bundled screenshots, datasets, or evaluation results.

## Project at a glance

- **Goal:** practice deploying a document-grounded AI chat application to Azure.
- **Application pattern:** retrieval-augmented generation (RAG), combining a
  document search index with a language model to produce answers with citations.
- **Sample technology:** Python/Quart backend, React/TypeScript frontend,
  Azure Developer CLI (`azd`), and Bicep infrastructure templates.
- **Hosting:** Azure Container Apps, as recorded in the retained manifests and
  the owner's resource inventory.
- **Original project:** [Azure Samples: azure-search-openai-demo](https://github.com/Azure-Samples/azure-search-openai-demo).
- **Learning context:** Microsoft Learn and hands-on Azure deployment practice.

## Deployment status and evidence

**Owner-reported status, October 15, 2026:** the application endpoint remains
operational. The model service was retired to reduce billing costs. A reachable
web interface should therefore **not** be interpreted as confirmation that
end-to-end AI answer generation still works.

Historical deployment endpoint:
<https://capps-backend-2zusqcpu4spb6.jollyhill-b19bfefa.eastus.azurecontainerapps.io/>

This archive cleanup did not contact the application, run inference, inspect
the Azure account, or change cloud resources. Resource existence and live
availability below are the owner's report, not independently verified results.

### Retained Azure resources reported by the owner

| Resource | Service | Region |
| --- | --- | --- |
| `capps-backend-2zusqcpu4spb6` | Container App | East US |
| `rapdemo-aca-env` | Container Apps Environment | East US |
| `rapdemoacr2zusqcpu4spb6` | Container registry | East US |
| `cog-di-2zusqcpu4spb6` | Document Intelligence | East US |
| `st2zusqcpu4spb6` | Storage account | East US |
| `gptkb-2zusqcpu4spb6-identity` | Managed Identity | East US |
| `rapdemo-aca-identity` | Managed Identity | East US |
| `appi-2zusqcpu4spb6` | Application Insights | East US |
| `log-2zusqcpu4spb6` | Log Analytics workspace | East US |
| `dash-2zusqcpu4spb6` | Shared dashboard | East US |
| `Application Insights Smart Detection` | Action group | Global |

Azure AI Search and Azure OpenAI are part of the sample's RAG design, but are
not listed as retained resources in the owner's current inventory. Do not infer
their present availability from the architecture diagrams.

Retiring the model service does not establish that the remaining deployment is
free: retained hosting, registry, storage, document processing, and telemetry
resources can still incur charges. Review Azure Cost Management separately.
Deleting this local archive does not delete Azure resources.

## What the exercise entailed

The sample's architecture illustrates two connected flows:

1. **Document ingestion:** upload documents to Blob Storage, extract content
   with Document Intelligence, split it into chunks in Python, generate
   embeddings with Azure OpenAI, and index those chunks in Azure AI Search.
2. **Question answering:** send a question from the web UI to the backend,
   retrieve relevant document content, and supply that content with a prompt
   to the language model so the response can cite its sources.

These describe the **sample design**, not a claim that every optional feature
was enabled or independently implemented during this exercise.

### Reference diagrams (upstream material, not personal deployment evidence)

![Upstream sample RAG architecture](azure-search-openai-demo/docs/images/appcomponents.png)

![Upstream sample document ingestion flow](azure-search-openai-demo/docs/images/diagram_prepdocs.png)

The other supplied screenshots, example evaluation runs, and sample datasets
were bundled reference material. They were removed rather than presented as
personal screenshots, performance measurements, or original work.

## Repository-verifiable work

The repository records the project import and subsequent local changes:

| Commit | Recorded work |
| --- | --- |
| `79375315a0bc99aac96244925cb4e4e32d185010` | Initial project import |
| `8c9f19c` | Removed `user-select: none` from the settings CSS, recorded as a compatibility fix |
| `3b42e54` | Moved MarkdownViewer styling onto a wrapping element rather than passing `className` to ReactMarkdown |
| `3b42e54`, `9651919`, `505dc9a` | Frontend dependency manifest and lockfile updates |

The concise [personal changes patch](personal-changes.patch) preserves the
net source edits and dependency manifest changes relative to the initial
import. The much larger lockfile diff remains in Git history instead of being
duplicated here. These changes are recorded facts, not a new claim of passing
builds, tests, or deployment validation.

The retained deployment configuration consists of:

- [Outer azd initialization manifest](azure.yaml): the original wrapper
  pointing to the nested project.
- [Sample deployment manifest](azure-search-openai-demo/azure.yaml): backend
  Container Apps hosting, frontend build hooks, optional ingestion Functions,
  and provisioning/deployment hooks.

Both manifests are historical artifacts. Their application, infrastructure,
and script paths intentionally refer to files removed from this archive;
**do not run `azd up` from this folder**.

## Archive selection

Before cleanup the project occupied **466,330,217 bytes (444.7 MiB)** across
**69,227 local files**, with **700 files tracked in Git**.

| Kept | Reason |
| --- | --- |
| This project summary and owner-reported resource inventory | Gives an employer context, scope, limitations, and attributable work |
| Two original deployment manifests | Records deployment intent without retaining the full template |
| Concise personal changes patch | Shows repository-recorded modifications |
| Two upstream reference diagrams | Explains the RAG and ingestion design, explicitly attributed |
| [Azure Samples MIT license](azure-search-openai-demo/LICENSE) | Preserves the upstream copyright and license |

Removed locally and from the current Git index:

- Installed `node_modules` (328.8 MiB) and generated backend static assets
  (35.5 MiB), including stale duplicate build bundles.
- Bundled evaluation tooling, ground truth, and example results (64.7 MiB);
  these were not verified as personal experiments.
- The runnable sample source, Bicep modules, sample documents, tests,
  fixtures, remaining screenshots, copied guides, and upstream contribution,
  automation, and editor scaffolding.
- The generated next-steps guide and duplicate development-container setup.

The full application can be recovered from this repository's history. This
cleanup intentionally does **not** rewrite history: older blobs, including
previously committed dependencies, still occupy Git storage. The repository's
Git object store was about 127.9 MiB before cleanup, shared across all projects;
that is separate from the local project files measured above.

## Recovering the historical source

The full pre-archive repository state is commit:

```text
b2ffe4bdbbe183996354510d00d88de9eda183f6
```

From the repository root, create a separate checkout without undoing the archive:

```powershell
git worktree add --detach ..\AI_Engineering_Lessons-before-azure-archive b2ffe4bdbbe183996354510d00d88de9eda183f6
```

This checks out the whole historical repository, so allow disk space for other
projects too. Installed dependencies excluded from Git are not recovered.
For the application alone, export its tracked files to a separate ZIP:

```powershell
git archive --format=zip --output=..\azure-project-before-archive.zip b2ffe4bdbbe183996354510d00d88de9eda183f6 my-intelligent-app
```

Historical dependencies may be outdated; recovery is not a guarantee of a
working deployment. Consult the recovered documentation or the maintained
upstream project before running it, and do not commit credentials or local
Azure environment files.

No exact upstream source commit was established for the original import.
The commit above identifies this repository's preserved snapshot; it is not
an Azure Samples release identifier. Keep that history available when sharing
this archive if historical reproducibility matters.

## Attribution

Application template and reference diagrams: Azure Samples contributors.
The retained upstream material is covered by its
[MIT license](azure-search-openai-demo/LICENSE), copyright 2023 Azure Samples.
Personal contribution here is the deployment learning exercise and the
repository-recorded changes described above, not authorship of the full RAG
application.
