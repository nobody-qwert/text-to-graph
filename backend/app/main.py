"""FastAPI application that exposes the graph generation pipeline as an HTTP API."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


# ---------------------------------------------------------------------------
#  Configure the import path so the API can reuse the existing graph pipeline
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
GRAPH_SRC = REPO_ROOT / "graph_extractor" / "src"

if str(GRAPH_SRC) not in os.sys.path:
    os.sys.path.insert(0, str(GRAPH_SRC))


import abort_manager  # noqa: E402  (import after sys.path mutation)
import config as cfg  # noqa: E402
import graph_generator as gg  # noqa: E402
import llm_api  # noqa: E402


API_DESCRIPTION = """REST API for the Knowledge Graph generator."""


def _load_json_field(raw_value: str | None, field_name: str) -> Dict:
    """Safely parse a JSON field from a multipart request."""

    if raw_value in (None, ""):
        return {}

    try:
        return json.loads(raw_value)
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=400, detail=f"Invalid JSON in '{field_name}': {exc}") from exc


def _build_runtime_config(config_payload: Dict, options_payload: Dict) -> Dict:
    """Merge the incoming config payload with the application's defaults."""

    runtime_config = cfg.default_config.copy()
    runtime_config.update(config_payload)

    runtime_config.setdefault("config_file", "config.json")

    # Build the extended configuration (adds internal defaults)
    runtime_config = cfg.build_extended_config(runtime_config)

    # Allow runtime overrides for UI specific flags
    if "merge_document_graphs" in options_payload:
        runtime_config["merge_document_graphs"] = bool(options_payload["merge_document_graphs"])

    if "optimization_on" in options_payload:
        runtime_config["optimization_on"] = bool(options_payload["optimization_on"])

    if options_payload.get("resolution_state") == "high":
        cfg.set_resolution(runtime_config, "high")
    elif options_payload.get("resolution_state") == "normal":
        cfg.set_resolution(runtime_config, "normal")

    # Directories inside the container that are mounted as volumes via docker-compose
    output_dir = Path(os.getenv("OUTPUT_DIR", runtime_config["output_folder"]))
    internal_dir = Path(os.getenv("INTERNAL_DATA_DIR", runtime_config["internal_data_dir"]))

    output_dir.mkdir(parents=True, exist_ok=True)
    internal_dir.mkdir(parents=True, exist_ok=True)

    runtime_config["output_folder"] = str(output_dir)
    runtime_config["internal_data_dir"] = str(internal_dir)

    cfg.detect_external_pdf_extractor_tool(runtime_config)

    api_key = runtime_config.get("api_key") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="Missing OpenAI API key. Provide it in the request or as OPENAI_API_KEY.")

    runtime_config["api_key"] = api_key

    return runtime_config


app = FastAPI(title="Text to Graph Backend", description=API_DESCRIPTION, version="0.1.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", REPO_ROOT / "output_graphs"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")


@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "ok"}


def _progress_logger(logs: List[Dict[str, str]]):
    def wrapper(message: str, type_name: str = "progress") -> None:
        # Avoid leaking API keys or other sensitive values
        if type_name == "log" and "api_key" in message.lower():
            return
        logs.append({"type": type_name, "message": message})

    return wrapper


@app.post("/generate")
async def generate_graphs(
    files: List[UploadFile] = File(description="One or more PDF documents."),
    config: str | None = Form(default=None, description="JSON encoded configuration overrides."),
    options: str | None = Form(default=None, description="JSON encoded UI flags."),
):
    if not files:
        raise HTTPException(status_code=400, detail="At least one PDF file must be provided.")

    config_payload = _load_json_field(config, "config")
    options_payload = _load_json_field(options, "options")

    runtime_config = _build_runtime_config(config_payload, options_payload)

    abort_manager.ABORT_FLAG = False
    llm_api.set_llm_config(runtime_config)

    progress_entries: List[Dict[str, str]] = []
    callback = _progress_logger(progress_entries)

    upload_dir = Path(tempfile.mkdtemp(prefix="uploads_", dir=runtime_config["internal_data_dir"]))

    stored_files: List[Path] = []
    try:
        for upload in files:
            if upload.content_type not in {"application/pdf", "application/octet-stream", None}:
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {upload.content_type}")

            safe_name = Path(upload.filename or "document.pdf").name
            destination = upload_dir / safe_name

            with destination.open("wb") as buffer:
                while chunk := await upload.read(1024 * 1024):
                    buffer.write(chunk)

            stored_files.append(destination)

        existing_outputs = {p.name for p in Path(runtime_config["output_folder"]).glob("*.html")}

        await gg.generate_graph_async([str(path) for path in stored_files], runtime_config, callback)

        new_outputs = [
            str(Path("/outputs") / path.name)
            for path in Path(runtime_config["output_folder"]).glob("*.html")
            if path.name not in existing_outputs
        ]

        return {
            "status": "completed",
            "outputs": new_outputs,
            "logs": progress_entries,
        }
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - executed in runtime, not during tests
        callback(f"{exc}", "error")
        raise HTTPException(status_code=500, detail="Graph generation failed.") from exc
    finally:
        shutil.rmtree(upload_dir, ignore_errors=True)
        abort_manager.ABORT_FLAG = False

