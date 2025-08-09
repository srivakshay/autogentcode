# app.py
import argparse
import os
import re
from pathlib import Path
from typing import List

from autogen import (
    AssistantAgent,
    UserProxyAgent,
)
from autogen import GroupChat, GroupChatManager

from config import LLM_CONFIG, MAX_TURNS


# --- helpers -----------------------------------------------------------------

def extract_file_blocks(text: str) -> List[tuple]:
    """
    Parse blocks like:

    [FILE: path/to/File.java]
    <code>

    Returns list of (path, content).
    """
    pattern = r"\[FILE:\s*([^\]]+)\]\s*(?:\r?\n)+```.*?\r?\n(.*?)```|(\[FILE:.*?])"
    # more robust two-pass parse:
    files = []
    file_header = r"\[FILE:\s*([^\]]+)\]"
    segments = re.split(file_header, text)
    # segments looks like: [pre, path1, rest1, path2, rest2, ...]
    if len(segments) <= 1:
        # try without code fences
        loose = re.findall(r"\[FILE:\s*([^\]]+)\]\s*(.+?)(?=(?:\n\[FILE:)|\Z)", text, flags=re.S)
        for path, content in loose:
            files.append((path.strip(), content.strip()))
        return files

    pre = segments[0]
    pairs = list(zip(segments[1::2], segments[2::2]))
    for path, body in pairs:
        # If the model wrapped in triple backticks, strip them
        fenced = re.findall(r"```[a-zA-Z0-9]*\n(.*?)```", body, flags=re.S)
        content = fenced[0].strip() if fenced else body.strip()
        files.append((path.strip(), content))
    return files


def write_files(base_dir: Path, files: List[tuple]):
    for rel, code in files:
        out_path = base_dir / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(code, encoding="utf-8")


def write_diagrams(base_dir: Path, mermaid_text: str):
    # Extract all mermaid code blocks
    blocks = re.findall(r"```mermaid\s+(.*?)```", mermaid_text, flags=re.S | re.I)
    (base_dir / "diagrams").mkdir(parents=True, exist_ok=True)
    for idx, block in enumerate(blocks, start=1):
        (base_dir / "diagrams" / f"diagram_{idx}.mmd").write_text(block.strip(), encoding="utf-8")


# --- Agents ------------------------------------------------------------------

def build_agents(project_name: str):
    supervisor = AssistantAgent(
        name="SupervisorAgent",
        system_message=(
            "You are the Supervisor. Coordinate two experts:\n"
            "- ConverterAgent (code)\n"
            "- DiagramAgent (mermaid)\n\n"
            "Plan:\n"
            "1) Ask ConverterAgent to produce Java Spring Boot project files\n"
            "2) Ask DiagramAgent to produce 2 Mermaid diagrams matching code\n"
            "3) Ensure consistency of names and layers. When both are done, say FINAL."
        ),
        llm_config=LLM_CONFIG,
    )

    converter = AssistantAgent(
        name="ConverterAgent",
        system_message=Path("prompts/converter_system.txt").read_text(encoding="utf-8"),
        llm_config=LLM_CONFIG,
    )

    diagrammer = AssistantAgent(
        name="DiagramAgent",
        system_message=Path("prompts/diagram_system.txt").read_text(encoding="utf-8"),
        llm_config=LLM_CONFIG,
    )

    user = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",  # we feed the SP via script
        code_execution_config=False,
        default_auto_reply="OK",
    )

    return supervisor, converter, diagrammer, user


def run(project_name: str, stored_proc_path: Path, database: str):
    out_dir = Path("out") / project_name
    out_dir.mkdir(parents=True, exist_ok=True)

    sp_sql = stored_proc_path.read_text(encoding="utf-8")

    supervisor, converter, diagrammer, user = build_agents(project_name)

    # Group chat
    chat = GroupChat(
        agents=[user, supervisor, converter, diagrammer],
        messages=[],
        max_round=MAX_TURNS,
        speaker_selection_method="auto",
    )
    manager = GroupChatManager(groupchat=chat, llm_config=LLM_CONFIG)

    # Seed message with the input + requirements
    seed = f"""
PROJECT_NAME: {project_name}
DATABASE: {database}

INPUT_STORED_PROCEDURE_SQL:
CREATE OR REPLACE PROCEDURE process_orders(p_min_total NUMERIC)
LANGUAGE plpgsql
AS $$
BEGIN
  -- Example: mark orders above threshold as PRIORITY
  UPDATE orders
     SET priority = TRUE
   WHERE total_amount >= p_min_total
     AND status = 'NEW';
END;
$$;

REQUIREMENTS:
- Spring Boot 3.x
- Java 21
- Postgres (override if SQL clearly targets another DB)
- Clean architecture: controller → service → repository; include entities, DTOs, mappers
- Proper build (Gradle or Maven)
- Config (application.yml with profiles)
- Unit tests for service layer
- Return code in [FILE: path] blocks.
- DiagramAgent must output exactly two mermaid code blocks: (1) high-level, (2) low-level.
- Keep naming consistent between code and diagrams.
"""
    user.initiate_chat(manager, message=seed)

    # Collect everything the agents said
    full_transcript = "\n\n".join(m["content"] for m in chat.messages if isinstance(m.get("content"), str))

    # Split by agent for easier extraction
    conv_texts = {
        "ConverterAgent": "",
        "DiagramAgent": ""
    }
    for m in chat.messages:
        if m.get("name") in conv_texts and isinstance(m.get("content"), str):
            conv_texts[m["name"]] += "\n\n" + m["content"]

    # Write code files
    code_files = extract_file_blocks(conv_texts["ConverterAgent"])
    write_files(out_dir, code_files)

    # Write diagrams
    write_diagrams(out_dir, conv_texts["DiagramAgent"])

    # Also drop raw outputs for debugging
    (out_dir / "raw_converter.txt").write_text(conv_texts["ConverterAgent"], encoding="utf-8")
    (out_dir / "raw_diagrammer.txt").write_text(conv_texts["DiagramAgent"], encoding="utf-8")
    (out_dir / "transcript.txt").write_text(full_transcript, encoding="utf-8")

    print(f"\n✅ Done. See: {out_dir}\n"
          f"- Java project files under that folder\n"
          f"- Mermaid diagrams in {out_dir/'diagrams'}\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--sp", required=True, type=str, help="Path to stored procedure SQL file")
    p.add_argument("--project-name", required=True, type=str, help="Output project name (folder)")
    p.add_argument("--db", default="postgres", choices=["postgres", "mysql", "mssql", "oracle"], help="Target DB")
    args = p.parse_args()

    run(
        project_name=args.project_name,
        stored_proc_path=Path(args.sp),
        database=args.db,
    )
