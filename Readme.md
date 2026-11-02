<<<<<<< HEAD
 # Agentic AI Production Project

An Agentic AI assistant built with Python, LangChain and MCP that can understand user instructions, decide which tools are required, and execute real-world tasks instead of only generating text.

## 🚀 What This Project Does

This project demonstrates how an LLM can act as an agent by connecting reasoning with external tools.

Instead of simply answering:

> "How do I create a GitHub repository?"

the agent can understand the request, select the appropriate tool, execute the required actions, and return the result to the user.

## 🏗️ Agent Flow

```text
User Request
     ↓
LLM / Agent
     ↓
Understand the task
     ↓
Select required tool
     ↓
MCP Tool / External Service
     ↓
Execute action
     ↓
Tool Result
     ↓
Agent
     ↓
Final Response
=======
# Educosys Claude — RAG-Powered Code Assistant

An interactive, terminal-based coding assistant that can inspect a local codebase, answer questions using retrieval-augmented generation (RAG), use filesystem and terminal tools, connect to external Model Context Protocol (MCP) servers, and plan and execute multi-step software tasks with human approval.

The application is built around LangChain/LangGraph agents and a configurable LLM/vector-store layer. It is designed as a local developer assistant and learning project.

## Contents

- [What it does](#what-it-does)
- [Architecture](#architecture)
- [Repository structure](#repository-structure)
- [Technology stack](#technology-stack)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Environment variables](#environment-variables)
- [Run the application](#run-the-application)
- [CLI commands](#cli-commands)
- [How the main workflows work](#how-the-main-workflows-work)
- [Storage and generated data](#storage-and-generated-data)
- [Important implementation notes](#important-implementation-notes)
- [Troubleshooting](#troubleshooting)
- [Security considerations](#security-considerations)

## What it does

### 1. Codebase question answering with RAG

- Parses supported source files and splits code into searchable chunks.
- Builds a persistent vector index using ChromaDB or Qdrant, depending on configuration.
- Retrieves relevant code context for a user question.
- Uses an LLM-powered agent to formulate an answer.
- Includes a semantic cache layer to reuse answers for sufficiently similar questions when enabled.
- Supports manual re-indexing and filesystem watching so code changes can be reflected in the index.

### 2. Agent tools

The primary agent is provided with tools for:

- Searching the indexed codebase.
- Reading and writing files, appending to files, listing directories, and checking whether paths exist.
- Running shell commands, including commands in a selected working directory.
- Calling tools exposed by configured MCP servers.

### 3. Planning and multi-step task execution

The `/plan` workflow turns a software goal into a structured execution plan. The plan contains tasks, dependencies, estimated effort, expected output files, acceptance criteria, risks, and assumptions.

Before execution, the user can approve the plan, modify a task description, or reject it and request a revised plan. Approved plans and task states are stored in SQLite. The task orchestrator executes dependency-ready tasks, records results and failures, and supports recovery of interrupted work.

### 4. Sessions and memory

- Conversation sessions can be created and switched.
- LangGraph's SQLite checkpointer persists agent conversation state.
- A summarization middleware is configured for conversation memory.
- Task execution state is stored separately in a SQLite task database.

### 5. Observability

Application modules use a shared Python logging helper. Application logs are emitted at DEBUG level while the root logging configuration suppresses most third-party library noise at WARNING level.

## Architecture

```text
                         ┌────────────────────────┐
                         │       CLI / REPL       │
                         │      My_claude.main    │
                         └───────────┬────────────┘
                                     │
                  ┌──────────────────┼──────────────────┐
                  │                  │                  │
             /ask workflow      /plan workflow     Session commands
                  │                  │
          Agent orchestrator   Task orchestrator
                  │                  │
             Agent factory      LLM task planner
                  │                  │
       ┌──────────┼─────────┐   Human plan approval
       │          │         │          │
      LLM       RAG       Tools     SQLite task store
       │          │         │          │
       │     Indexer and    ├─ Filesystem tools
       │     retriever      ├─ Terminal tools
       │          │         └─ MCP tools
       │     Chroma / Qdrant
       │
       └── Provider selected through configuration

Cross-cutting components: session/checkpoint memory, semantic cache,
filesystem watcher, skills registry, and application logging.
```

## Repository structure

```text
capstone_project/
├── My_claude/
│   ├── agent/
│   │   ├── factory.py             # Builds the main LangChain agent and registers tools
│   │   ├── orchestrator.py        # Handles user questions and semantic-cache lookup/store
│   │   └── tools.py               # Codebase search tool
│   ├── cache/
│   │   └── semantic_cache.py      # Semantic response cache and repository cache domain
│   ├── context/
│   │   ├── indexers/
│   │   │   ├── code_parser.py     # Parses and chunks supported source files
│   │   │   ├── factory.py         # Selects an indexer from configuration
│   │   │   ├── semantic_chroma.py # ChromaDB indexing
│   │   │   ├── semantic_qdrant.py # Qdrant semantic indexing
│   │   │   ├── hybrid_qdrant.py   # Hybrid Qdrant indexing
│   │   │   └── watcher.py         # Watches source files and refreshes the index
│   │   └── retrievers/
│   │       ├── factory.py         # Selects a retriever from configuration
│   │       ├── semantic_chroma.py # ChromaDB retrieval
│   │       ├── semantic_qdrant.py# Qdrant semantic retrieval
│   │       └── hybrid_qdrant.py   # Hybrid Qdrant retrieval
│   ├── llm/
│   │   └── factory.py             # Creates configured chat model and embedder
│   ├── mcp/
│   │   ├── My_claude_mcp_client.py # Loads MCP tools
│   │   └── My_claude_mcp_config.py # Loads MCP server settings and env references
│   ├── memory/
│   │   ├── session.py             # Current session creation and switching
│   │   └── short_term.py          # SQLite checkpointer and summarization middleware
│   ├── observability/
│   │   └── logger.py              # Shared logging configuration
│   ├── skills/
│   │   ├── registry.py            # Skill discovery and registry
│   │   └── skill_tools.py         # Skill loading and prompt construction
│   ├── tasks/
│   │   ├── planner.py             # Structured LLM execution-plan generation
│   │   ├── approval.py            # Human review, modification, and approval
│   │   ├── orchestrator.py        # Dependency-aware task execution loop
│   │   ├── executor.py            # Executes individual subtasks with agents
│   │   ├── task_store.py          # SQLite project/task persistence and state transitions
│   │   ├── recovery.py            # Recovers interrupted tasks
│   │   └── status.py              # Displays task progress
│   ├── tools/
│   │   ├── filesystem_tools.py    # File operations exposed to the agent
│   │   └── terminal_tools.py      # Shell command tools exposed to the agent
│   ├── config.py                  # Loads config.yaml
│   ├── config.yaml                # LLM, embeddings, RAG, vector store, memory, task settings
│   ├── My_claude_mcp_servers.json # MCP server definitions
│   └── main.py                    # CLI entry point
├── .env                           # Local secrets; do not commit
├── .gitignore
├── pyproject.toml                 # Poetry project and dependencies
├── poetry.lock                    # Locked dependency versions
└── Readme.md
```

Runtime directories such as `.project/`, `.chromadb/`, and `.memory/` may be created or populated while the application runs. They contain local indexes, databases, and session data rather than application source code.

## Technology stack

| Area | Technology |
|---|---|
| Language | Python 3.12 |
| Dependency and packaging | Poetry |
| Agent framework | LangChain |
| Agent state / orchestration | LangGraph |
| LLM providers | OpenAI and Anthropic integrations |
| Embeddings | OpenAI or Hugging Face |
| Vector stores | ChromaDB and Qdrant |
| Structured data validation | Pydantic |
| Configuration | YAML and environment variables |
| MCP integration | `langchain-mcp-adapters` |
| Code parsing | Tree-sitter and tree-sitter-language-pack |
| Filesystem monitoring | Watchdog |
| Task and checkpoint persistence | SQLite |
| CLI presentation | Rich |

## Requirements

- Windows, macOS, or Linux.
- Python `>=3.12,<4.0` (Python 3.12 is the version targeted by the project).
- Poetry 2.x.
- An API key for the LLM provider selected in `My_claude/config.yaml`.
- Node.js/npm (`npx`) if you intend to use the configured GitHub and filesystem MCP servers.
- A GitHub personal access token if you intend to use the GitHub MCP server.

## Installation

Open a terminal in the repository root (`capstone_project/`).

```bash
# Confirm Python and Poetry are available
python --version
poetry --version

# Install project dependencies
poetry install

# Create your local environment file from the example below
# (Create .env manually; do not put API keys in source files.)
```

If Poetry is not using Python 3.12, select the interpreter before installing:

```bash
poetry env use python3.12
poetry install
```

On Windows, you can use the Python launcher if needed:

```powershell
py -3.12 --version
poetry env use (py -3.12 -c "import sys; print(sys.executable)")
poetry install
```

## Configuration

The application reads `My_claude/config.yaml` through `My_claude/config.py`. Update this file to choose the LLM, embedding model, RAG mode, vector-store provider, and local storage paths.

The current configuration includes these settings:

| Section | Purpose | Current configured value |
|---|---|---|
| `llm.provider` | Chat model provider | `openai` |
| `llm.model` | Chat model | `gpt-4o` |
| `llm.judge_model` | Configured judge model | `gpt-4o-mini` |
| `embeddings.provider` | Embedding provider | `openai` |
| `embeddings.model` | Embedding model | `text-embedding-3-small` |
| `rag.mode` | Retrieval mode | `semantic` |
| `vector_store.provider` | Vector database | `chroma` |
| `chromadb.persist_dir` | Chroma persistence directory | `.project/chromadb/` |
| `tasks.db_path` | Task database | `.project/tasks.db` |
| `memory.db_path` | Memory database | `.project/memory/memory.db` |
| `skills.skills_dir` | Skills directory | `.project/skills` |

The indexer/retriever factories select Chroma or Qdrant implementations based on `rag.mode` and `vector_store.provider`. Qdrant-specific settings are also present in the YAML file.

**Configuration note:** the supplied `config.yaml` contains the `vector_store` YAML key twice. YAML parsers commonly retain only the last occurrence, so consolidate these into a single `vector_store` mapping before relying on additional vector-store options. Also verify that the configured semantic-cache backend is available in your environment before enabling it.

## Environment variables

Create a `.env` file in the repository root. For an OpenAI configuration:

```dotenv
OPENAI_API_KEY=your_openai_api_key

# Required only if using the configured GitHub MCP server
GITHUB_TOKEN=your_github_personal_access_token
```

The MCP configuration substitutes `${GITHUB_TOKEN}` from the environment and uses `${CWD}` as the filesystem MCP server's working directory. Do not commit `.env` or paste secrets into issue reports.

If you switch providers, add the credentials required by that provider and confirm the corresponding LangChain integration is installed.

## Run the application

From the repository root:

```bash
poetry run My_claude
```

The application initializes the configured LLM and embedder, indexes the current working directory, starts the filesystem watcher, initializes the agent and session, and then opens an interactive terminal prompt.

You can also invoke the Python entry point:

```bash
poetry run python -m My_claude.main
```

Run the command from the project/repository directory you want the assistant to inspect. The indexer and filesystem watcher use the current working directory as the codebase root.

## CLI commands

| Command | Description |
|---|---|
| `/ask <question>` | Ask a question about the indexed codebase. |
| `/reindex` | Re-index the current working directory and invalidate its semantic cache entry. |
| `/show_index` | Display the indexed chunks using the configured index inspector. |
| `/new_session` | Start a new conversation session. |
| `/switch <session_id>` | Switch to an existing session. |
| `/session` | Display the active session ID. |
| `/plan <goal>` | Generate a multi-step execution plan, request approval, and execute approved tasks. |
| `/task_status` | Display task progress for the active project. |
| `/exit` or `/quit` | Exit the application. |

Example:

```text
> /ask Where is the configuration loaded and which model is selected?
> /plan Add unit tests for the configuration loader and document how to run them.
> /task_status
> /exit
```

## How the main workflows work

### Ask workflow

1. The user enters `/ask <question>`.
2. The agent orchestrator checks the semantic cache when a cache instance/domain is available.
3. On a cache miss, the LangChain agent is invoked with the current thread/session ID.
4. The agent can search the codebase and use its registered filesystem, terminal, and MCP tools.
5. The response is returned and, when configured, stored in the semantic cache.

### Indexing workflow

1. The indexer factory reads `rag.mode` and `vector_store.provider`.
2. The selected parser/indexer processes supported source files and creates embeddings.
3. Embeddings and metadata are persisted in the selected vector store.
4. The watcher observes file creation, modification, deletion, and moves.
5. File events are debounced before the index is updated. Cache invalidation is triggered after updates.

### Plan-and-execute workflow

1. `/plan <goal>` asks the LLM planner for a structured `ExecutionPlan`.
2. The plan is displayed in a Rich table.
3. The user approves it, edits a task description, or rejects it and supplies feedback for a new plan.
4. The approved plan and its tasks are persisted in SQLite.
5. The task orchestrator selects tasks whose dependencies are complete and claims them before execution.
6. Subtask agents execute the work; results and errors are written to the task store.
7. Recovery logic handles tasks left in progress after an interrupted run.
8. The project directory is re-indexed so follow-up `/ask` questions can find generated files.

## Storage and generated data

The current YAML configuration points to these local paths:

- `.project/tasks.db` — project plans, task metadata, execution status, results, and errors.
- `.project/memory/memory.db` — configured memory database.
- `.project/chromadb/` — ChromaDB persistent vector data.
- The LangGraph checkpointer database path is selected by `get_checkpointer_db_path()` in `My_claude/memory/short_term.py`.
- `.project/skills/` — configured skills directory.

The archive also contains `.chromadb/`, `.memory/`, and `.project/` runtime data. These are generated local state and are not required to understand the source architecture. Keep runtime databases and vector-index files out of source control unless there is a deliberate reason to share them.

## Important implementation notes

- The package is named `My_claude` (capitalization matters on case-sensitive filesystems).
- The configured MCP servers are launched over standard I/O using `npx`; Node.js/npm must be installed for those integrations.
- The configured GitHub MCP server requires `GITHUB_TOKEN`.
- The task orchestrator currently defaults to serial execution (`max_concurrent=1`) for deterministic execution and cost control.
- Plan generation and subtask execution require working model-provider credentials and network access.
- The shell tool uses `subprocess.run(..., shell=True)` and a small blocked-command list. That is not a complete security sandbox; only run this assistant in directories and environments where executing model-requested commands is acceptable.
- The filesystem tools can write to paths supplied to them. Restrict the working directory and permissions appropriately.

## Troubleshooting

### Poetry command is not found

Install Poetry and ensure its executable directory is on your PATH. Restart the terminal after changing PATH, then verify:

```bash
poetry --version
```

### Wrong Python interpreter

Check the interpreter Poetry selected:

```bash
poetry env info
poetry run python --version
```

Select Python 3.12 if necessary:

```bash
poetry env use python3.12
poetry install
```

### Missing API key or provider authentication errors

- Confirm `.env` exists in the repository root.
- Confirm the variable name matches the provider integration.
- Restart the application after editing environment variables.
- Do not include the actual key in logs or screenshots.

### MCP server fails to start

- Confirm Node.js and `npx` are installed and available on PATH.
- Check the MCP server package name and arguments in `My_claude/My_claude_mcp_servers.json`.
- For GitHub, confirm `GITHUB_TOKEN` is set and valid.

### Vector database or embedding errors

- Check `rag.mode`, `vector_store.provider`, and embedding settings in `My_claude/config.yaml`.
- Confirm the selected vector-store service/dependencies are available.
- For Chroma, confirm the configured persistence directory is writable.
- Resolve the duplicate `vector_store` YAML key noted above.

### Index does not reflect recent changes

Use `/reindex`. The filesystem watcher also refreshes supported files after a short debounce interval.

## Security considerations

- Never commit `.env`, API keys, GitHub tokens, or other credentials.
- The assistant can write files and execute shell commands. Review plans before approval and use a disposable/test repository when experimenting.
- The terminal command blocklist is limited and must not be treated as a security boundary.
- Avoid indexing secret files, credential stores, private keys, or large generated/runtime directories.
- Do not expose `.git`, vector-store databases, memory databases, or local runtime state unless required.

## Project status

This README documents the implementation and configuration found in the supplied project archive. It is not a claim that every optional integration has been exercised end-to-end. Before presenting the project as production-ready, validate a clean installation, each configured provider/vector-store combination, MCP connectivity, task recovery, and the security boundaries around filesystem and terminal tools.
>>>>>>> 140c7d8 (Implementation done)
