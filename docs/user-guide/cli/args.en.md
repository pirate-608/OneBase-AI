# Arguments Reference

Complete documentation for all OneBase CLI options, value ranges, and usage combinations.

---

## Global Options

Global options go **before** the command name and apply to all commands.

### `--version` / `-V`

Display the OneBase version and exit immediately. The version is read from `pyproject.toml` metadata.

```bash
onebase -V
# OneBase CLI, version 0.1.2
```

| Property | Value                                                |
| :------- | :--------------------------------------------------- |
| Type     | `bool` (flag)                                        |
| Default  | `False`                                              |
| Priority | Eager — executes immediately, ignores remaining args |

---

### `--lang` / `-l`

Set the CLI output language. Affects all logs, prompts, and error messages.

```bash
onebase --lang zh build     # Chinese output
onebase -l en serve -d      # English output
```

| Property | Value                          |
| :------- | :----------------------------- |
| Type     | `str`                          |
| Default  | `en`                           |
| Values   | `en` (English), `zh` (Chinese) |

**Environment variable alternative:**

```bash
export ONEBASE_LANG=zh   # Linux/macOS
set ONEBASE_LANG=zh      # Windows CMD
$env:ONEBASE_LANG="zh"   # PowerShell
```

Once set, no need to pass `--lang` each time. CLI argument takes priority over environment variable.

---

### `--verbose` / `-v`

Enable debug mode with DEBUG-level logging. Includes container startup commands, database connection probes, internal state, etc.

```bash
onebase -v build
# PG ready (attempt 1)
# Starting container group: db
# Executing: docker compose -f .onebase/docker-compose.yml up -d db
```

| Property  | Value   |
| :-------- | :------ |
| Type      | `bool`  |
| Default   | `False` |
| Log Level | `DEBUG` |

---

### `--quiet` / `-q`

Quiet mode — only ERROR-level output. Suitable for CI/CD pipelines or scripted invocations.

```bash
onebase -q build && echo "success"
```

| Property  | Value   |
| :-------- | :------ |
| Type      | `bool`  |
| Default   | `False` |
| Log Level | `ERROR` |

!!! note "`--verbose` and `--quiet` are mutually exclusive"
    When both are passed, `--quiet` takes priority (ERROR level overrides DEBUG).

---

### `--help` / `-h`

Display help information. Works for the main command or any subcommand.

```bash
onebase -h          # Global help
onebase build -h    # build command help
onebase serve -h    # serve command help
```

---

## init Options

### `--force` / `-f`

Overwrite existing configuration files. By default, if `onebase.yml` already exists, init refuses to execute and exits.

```bash
onebase init --force
```

| Property | Value   |
| :------- | :------ |
| Type     | `bool`  |
| Default  | `False` |

**Overwrite scope:**

| File               | `--force` Behavior                   |
| :----------------- | :----------------------------------- |
| `onebase.yml`      | Regenerate default config            |
| `.env`             | Regenerate (**new random password**) |
| `requirements.txt` | Regenerate template                  |
| `base/overview.md` | Regenerate                           |

!!! warning "Password will be reset"
    `--force` generates a new `POSTGRES_PASSWORD`. If a database is already running, first run `onebase stop -v` to clear old volumes — otherwise the new password won't connect to the old database.

---

## get-deps Options

`get-deps` has no dedicated options. It reads `onebase.yml` and outputs the dependency list to stdout.

```bash
# Standard usage: redirect to file
onebase get-deps > requirements.txt
pip install -r requirements.txt
```

**Output format:** One package per line (with version constraints), pip requirements format.

**Dependency mapping:** Maps `engine.reasoning.provider` and `engine.embedding.provider` to corresponding SDK packages. Examples:

| provider    | Generated Dependency                           |
| :---------- | :--------------------------------------------- |
| `ollama`    | `langchain-ollama>=0.2.0`                      |
| `openai`    | `langchain-openai>=0.2.0`                      |
| `dashscope` | `langchain-community>=0.3.0`, `dashscope>=1.0` |

---

## build Options

### `--with-ollama`

Start an Ollama Docker container alongside `build` for in-container embedding.

```bash
onebase build --with-ollama
```

| Property     | Value            |
| :----------- | :--------------- |
| Type         | `bool`           |
| Default      | `False`          |
| Container    | `onebase_ollama` |
| Exposed Port | `11434`          |

**Effect:** During `docker compose up`, starts the `ollama` service in addition to `db`, and sets `OLLAMA_BASE_URL` to `http://ollama:11434` (Docker internal network).

---

### `--with-xinference`

Start a Xinference container (ModelScope ecosystem).

```bash
onebase build --with-xinference
```

| Property     | Value                   |
| :----------- | :---------------------- |
| Type         | `bool`                  |
| Default      | `False`                 |
| Container    | `onebase_xinference`    |
| Exposed Port | `9997`                  |
| Web UI       | `http://localhost:9997` |

**Effect:** Overrides `OPENAI_API_BASE` to `http://xinference:9997/v1` (OpenAI-compatible protocol).

---

### `--with-vllm`

Start a vLLM container (high-throughput inference).

```bash
onebase build --with-vllm --use-gpu
```

| Property     | Value                            |
| :----------- | :------------------------------- |
| Type         | `bool`                           |
| Default      | `False`                          |
| Container    | `onebase_vllm`                   |
| Exposed Port | `8001` (maps to internal `8000`) |

**Effect:** Reads `engine.reasoning.model` from `onebase.yml` and passes it to vLLM's `--model` parameter, overriding `OPENAI_API_BASE` to `http://vllm:8000/v1`.

---

### `--use-gpu` / `-g`

Enable NVIDIA GPU passthrough for containerized inference engines.

```bash
onebase build --with-ollama -g
```

| Property     | Value                              |
| :----------- | :--------------------------------- |
| Type         | `bool`                             |
| Default      | `False`                            |
| Prerequisite | NVIDIA Container Toolkit installed |

**Generated Compose config:**

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

!!! note "Only affects inference containers"
    `-g` only affects containers started by `--with-ollama`, `--with-xinference`, or `--with-vllm`. It does not affect database or backend containers. Without any inference engine specified, `-g` has no effect.

---

### Inference Engine Mutual Exclusion

`--with-ollama`, `--with-xinference`, and `--with-vllm` — **at most one** can be specified:

```bash
# ✅ Valid
onebase build
onebase build --with-ollama
onebase build --with-vllm -g

# ❌ Invalid — multiple engines specified
onebase build --with-ollama --with-xinference
# → ❌ Container conflict: only one local inference engine can be specified at a time.
```

---

## serve Options

`serve` includes all of `build`'s inference engine options, plus `--port` and `--detach`.

### `--port` / `-p`

Specify the host port for the service.

```bash
onebase serve -d -p 3000
```

| Property | Value                          |
| :------- | :----------------------------- |
| Type     | `int`                          |
| Default  | `8000`                         |
| Mapping  | Host `port` → Container `8000` |

---

### `--detach` / `-d`

Run containers in background (Docker detached mode).

```bash
onebase serve -d    # Background, returns immediately
onebase serve       # Foreground, Ctrl+C to stop
```

| Property | Value   |
| :------- | :------ |
| Type     | `bool`  |
| Default  | `False` |

**Behavior differences:**

| Mode                 | Logs             | Terminal            | Stop Method    |
| :------------------- | :--------------- | :------------------ | :------------- |
| Foreground (default) | Real-time output | Blocking            | `Ctrl+C`       |
| Background (`-d`)    | Not displayed    | Returns immediately | `onebase stop` |

---

### `--with-ollama` / `--with-xinference` / `--with-vllm` / `--use-gpu`

Same as `build` command — see above. Mutual exclusion rules apply equally.

---

## stop Options

### `--volumes` / `-v`

Remove Docker data volumes when stopping containers.

```bash
onebase stop       # Keep data
onebase stop -v    # Remove volumes
```

| Property | Value   |
| :------- | :------ |
| Type     | `bool`  |
| Default  | `False` |

**Deleted volumes:**

| Volume            | Content                | Impact                            |
| :---------------- | :--------------------- | :-------------------------------- |
| `pgdata`          | PostgreSQL database    | All vectors lost, need to `build` |
| `ollama_data`     | Ollama model cache     | Need to `ollama pull` again       |
| `xinference_data` | Xinference model cache | Need to re-download models        |
| `vllm_data`       | vLLM HuggingFace cache | Need to re-download weights       |

---

## Quick Reference

| Command | Option              | Short | Type | Default |
| :------ | :------------------ | :---- | :--- | :------ |
| Global  | `--version`         | `-V`  | flag | —       |
| Global  | `--lang`            | `-l`  | str  | `en`    |
| Global  | `--verbose`         | `-v`  | flag | `False` |
| Global  | `--quiet`           | `-q`  | flag | `False` |
| `init`  | `--force`           | `-f`  | flag | `False` |
| `build` | `--with-ollama`     | —     | flag | `False` |
| `build` | `--with-xinference` | —     | flag | `False` |
| `build` | `--with-vllm`       | —     | flag | `False` |
| `build` | `--use-gpu`         | `-g`  | flag | `False` |
| `serve` | `--port`            | `-p`  | int  | `8000`  |
| `serve` | `--detach`          | `-d`  | flag | `False` |
| `serve` | `--with-ollama`     | —     | flag | `False` |
| `serve` | `--with-xinference` | —     | flag | `False` |
| `serve` | `--with-vllm`       | —     | flag | `False` |
| `serve` | `--use-gpu`         | `-g`  | flag | `False` |
| `stop`  | `--volumes`         | `-v`  | flag | `False` |

---

## Usage Examples

### Zero-Config Local Experience

```bash
onebase init
onebase get-deps > requirements.txt && pip install -r requirements.txt
# Ensure Ollama is running on host with models pulled
onebase build
onebase serve -d
```

### Fully Containerized + GPU

```bash
onebase init
onebase build --with-ollama -g
onebase serve --with-ollama -g -d -p 80
```

### CI/CD Pipeline

```bash
onebase -q build && onebase -q serve -d
```

### Chinese Output + Debug

```bash
onebase --lang zh -v build --with-ollama
```

### Reset Project

```bash
onebase stop -v        # Clear containers and data
onebase init --force   # Regenerate config
onebase build          # Rebuild
```

---

## Related Documentation

- [Basic Commands](basic.md) — Command overview and execution flow
- [Local Deployment](../deploy/cloud_deploy.en.md) — Complete deployment guide
- [Engine Configuration](../config/engine.md) — Provider and model selection
