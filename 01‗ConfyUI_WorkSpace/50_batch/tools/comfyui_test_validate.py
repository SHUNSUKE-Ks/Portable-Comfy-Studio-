#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ComfyUI CPUテスト検証スクリプト（画像生成なし・GPU/CPU負荷ゼロ志向）

目的:
  グラボなしのテスト機（venv）で ComfyUI を起動相当まで読み込み、
  「環境（パッケージ/カスタムノード）」と「ワークフロー」を検証して
  結果を JSON ログ1ファイルに記録する。本番(GPU機)では生成に集中するための事前チェック。

検証内容:
  1) パッケージ/カスタムノード import検証
     - nodes.init_extra_nodes() を実行し、全ノードの読み込み成否を収集
       （ComfyUI の --quick-test-for-ci 相当。サンプリングは一切しない）
  2) ワークフロー検証（画像生成なし）
     - API形式JSON   : execution.validate_prompt() でグラフ/入力/モデル参照を検証（負荷ゼロ）
     - UI形式JSON    : ノード型の存在 + 参照モデルファイルの実在を構文チェック

出力:
  <log-dir>\<YYYYMMDDHHmmss>_test.json  （1実行=1ファイル）

使い方（通常はBAT経由）:
  python comfyui_test_validate.py --comfy-dir D:\\ai\\ComfyUI \
      --workflow-dir D:\\ai\\ComfyUI\\user\\default\\workflows \
      --log-dir D:\\ai\\01‗ConfyUI_WorkSpace\\Report\\test_logs
"""

import argparse
import asyncio
import datetime
import glob
import json
import logging
import os
import sys
import traceback

# コンソール出力をUTF-8に固定（パスに含まれる特殊文字 '‗' 等で cp932 が落ちるのを防ぐ）
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# UI形式で「実行ノードではない」型（NODE_CLASS_MAPPINGS に無くても正常）
UI_NON_EXEC_TYPES = {
    "Note", "MarkdownNote", "Reroute", "PrimitiveNode", "Reroute (rgthree)",
    "Bookmark (rgthree)", "Fast Groups Bypasser (rgthree)",
}

# モデルファイルとみなす拡張子
MODEL_EXTS = (".safetensors", ".ckpt", ".pt", ".pth", ".bin", ".gguf", ".sft", ".onnx")

# 参照モデルを探すフォルダ種別
MODEL_FOLDER_TYPES = [
    "checkpoints", "loras", "vae", "controlnet", "clip", "clip_vision",
    "unet", "diffusion_models", "upscale_models", "embeddings",
    "style_models", "gligen", "hypernetworks", "photomaker", "text_encoders",
]


def parse_args():
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument("--comfy-dir", default=r"D:\ai\ComfyUI",
                   help="ComfyUI ルートディレクトリ")
    p.add_argument("--workflow", action="append", default=[],
                   help="検証するワークフローJSON（複数指定可）")
    p.add_argument("--workflow-dir", default=None,
                   help="このフォルダ内の *.json を全て検証")
    p.add_argument("--log-dir", default=None,
                   help="JSONログ出力先（省略時は comfy-dir\\test_output\\logs）")
    p.add_argument("--mode", default="CPU_TEST", help="ログに記録する実行モード名")
    p.add_argument("--skip-boot", action="store_true",
                   help="ノード初期化(import検証)を省略し、ワークフローの軽量構文確認のみ行う")
    # ComfyUI 側の引数と衝突しないよう parse_known_args
    return p.parse_known_args()[0]


class LogCollector(logging.Handler):
    """ComfyUI のログから IMPORT FAILED 等を拾うためのハンドラ。"""
    def __init__(self):
        super().__init__()
        self.messages = []

    def emit(self, record):
        try:
            self.messages.append(record.getMessage())
        except Exception:
            pass


def setup_comfy_import(comfy_dir, collector):
    """ComfyUI を CPU モードで import できるよう sys.argv / path を整える。"""
    # ComfyUI の cli_args は import 時に sys.argv を読むため、ここで仕込む
    sys.argv = [
        os.path.join(comfy_dir, "main.py"),
        "--cpu",
        "--disable-auto-launch",
        "--disable-api-nodes",   # オフライン安全（外部API/ネットワーク回避）
    ]
    sys.path.insert(0, comfy_dir)
    os.chdir(comfy_dir)
    # cli_args が sys.argv を読むのは args_parsing=True の時だけ。
    # nodes.py 任せにせず、import前に明示的に有効化して --cpu を確実に反映させる。
    import comfy.options
    comfy.options.enable_args_parsing()
    # IMPORT FAILED は INFO/WARNING で出るため INFO を拾う
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    collector.setLevel(logging.INFO)
    root.addHandler(collector)


def boot_nodes():
    """全ノードを初期化（import検証）。NODE_CLASS_MAPPINGS を返す。"""
    import nodes  # noqa: E402  (sys.argv 仕込み後に import する必要がある)
    asyncio.run(nodes.init_extra_nodes(init_custom_nodes=True, init_api_nodes=False))
    return nodes


def collect_import_failures(collector):
    """ログメッセージから IMPORT FAILED 一覧と、失敗理由(Cannot import ... : reason)を抽出。"""
    fails = []
    reasons = []
    for msg in collector.messages:
        if "IMPORT FAILED" in msg:
            fails.append(msg.strip())
        # nodes.py: load_custom_node の except で出る実エラー理由
        if msg.startswith("Cannot import"):
            reasons.append(msg.strip())
    return fails, reasons


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def detect_format(data):
    """UI形式 / API形式 / 不明 を判定。"""
    if isinstance(data, dict):
        if isinstance(data.get("nodes"), list) and "links" in data:
            return "ui"
        # API形式: {node_id: {"class_type":..., "inputs":...}} もしくは {"prompt": {...}}
        prompt = data.get("prompt", data)
        if isinstance(prompt, dict) and prompt:
            if all(isinstance(v, dict) and "class_type" in v for v in prompt.values()):
                return "api"
    return "unknown"


def scan_model_refs(obj, found):
    """widgets_values 等を再帰走査し、モデルファイルらしき文字列を集める。"""
    if isinstance(obj, str):
        low = obj.lower()
        if low.endswith(MODEL_EXTS):
            found.add(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            scan_model_refs(v, found)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            scan_model_refs(v, found)


def known_model_basenames(folder_paths):
    known = set()
    for ft in MODEL_FOLDER_TYPES:
        try:
            for name in folder_paths.get_filename_list(ft):
                known.add(os.path.basename(name).lower())
        except Exception:
            pass
    return known


def validate_ui_workflow(data, node_mappings, folder_paths):
    """UI形式の構文チェック（ノード型の存在 + モデル実在）。サンプリングなし。"""
    result = {"format": "ui", "status": "success",
              "missing_node_types": [], "missing_models": [], "node_count": 0}
    nodes_list = data.get("nodes", [])
    result["node_count"] = len(nodes_list)

    missing_types = set()
    for n in nodes_list:
        t = n.get("type")
        if not t or t in UI_NON_EXEC_TYPES:
            continue
        if node_mappings is not None and t not in node_mappings:
            missing_types.add(t)
    result["missing_node_types"] = sorted(missing_types)

    if folder_paths is not None:
        refs = set()
        scan_model_refs(nodes_list, refs)
        known = known_model_basenames(folder_paths)
        missing_models = [r for r in sorted(refs)
                          if os.path.basename(r).lower() not in known]
        result["missing_models"] = missing_models

    if result["missing_node_types"] or result["missing_models"]:
        result["status"] = "error"
    return result


def validate_api_workflow(data, execution):
    """API形式を validate_prompt で検証（グラフ/入力/モデル参照、サンプリングなし）。"""
    prompt = data.get("prompt", data)
    valid, error, good_outputs, node_errors = asyncio.run(
        execution.validate_prompt("cpu-test", prompt, None)
    )
    result = {
        "format": "api",
        "status": "success" if valid else "error",
        "good_outputs": list(good_outputs) if good_outputs else [],
        "node_count": len(prompt),
    }
    if not valid:
        result["error"] = error
        result["node_errors"] = node_errors
    return result


def main():
    cli = parse_args()
    comfy_dir = os.path.abspath(cli.comfy_dir)
    log_dir = cli.log_dir or os.path.join(comfy_dir, "test_output", "logs")
    os.makedirs(log_dir, exist_ok=True)

    started = datetime.datetime.now()
    log = {
        "timestamp": started.isoformat(timespec="seconds"),
        "status": "success",
        "mode": cli.mode,
        "comfy_dir": comfy_dir,
        "python": sys.executable,
        "package_check": None,
        "workflows": [],
    }

    collector = LogCollector()
    node_mappings = None
    folder_paths = None
    execution = None

    # ---- 1) パッケージ / カスタムノード import検証 ----
    if not cli.skip_boot:
        setup_comfy_import(comfy_dir, collector)
        pkg = {"status": "success", "total_nodes": 0, "import_failed": []}
        try:
            nodes = boot_nodes()
            import folder_paths as _fp           # noqa
            import execution as _ex               # noqa
            folder_paths = _fp
            execution = _ex
            node_mappings = nodes.NODE_CLASS_MAPPINGS
            pkg["total_nodes"] = len(node_mappings)
            fails, reasons = collect_import_failures(collector)
            pkg["import_failed"] = fails
            pkg["import_failed_reasons"] = reasons
            if fails:
                pkg["status"] = "warning"   # 一部ノード失敗。コアが動けば検証は継続
        except Exception as ex:
            pkg["status"] = "error"
            pkg["error_message"] = "{}: {}".format(type(ex).__name__, ex)
            pkg["traceback"] = traceback.format_exc()
            log["status"] = "error"
        log["package_check"] = pkg
    else:
        # skip-boot: import検証なし。UI形式の最小構文確認のみ可能
        setup_comfy_import(comfy_dir, collector)
        try:
            import folder_paths as _fp  # noqa
            folder_paths = _fp
        except Exception:
            folder_paths = None
        log["package_check"] = {"status": "skipped"}

    # ---- 2) 検証対象ワークフローの収集 ----
    targets = list(cli.workflow)
    if cli.workflow_dir and os.path.isdir(cli.workflow_dir):
        targets += sorted(glob.glob(os.path.join(cli.workflow_dir, "*.json")))
    targets = list(dict.fromkeys(os.path.abspath(t) for t in targets))  # 重複除去

    # ---- 3) 各ワークフロー検証 ----
    for path in targets:
        entry = {"file": path, "status": "success"}
        try:
            data = load_json(path)
            fmt = detect_format(data)
            if fmt == "api" and execution is not None:
                entry.update(validate_api_workflow(data, execution))
            elif fmt == "ui":
                entry.update(validate_ui_workflow(data, node_mappings, folder_paths))
            elif fmt == "api" and execution is None:
                entry["status"] = "skipped"
                entry["reason"] = "API形式だが --skip-boot のため validate_prompt 不可"
                entry["format"] = "api"
            else:
                entry["status"] = "error"
                entry["format"] = fmt
                entry["error_message"] = "形式を判定できません（UI/APIどちらでもない）"
        except Exception as ex:
            entry["status"] = "error"
            entry["error_message"] = "{}: {}".format(type(ex).__name__, ex)
            entry["traceback"] = traceback.format_exc()
        if entry["status"] == "error":
            log["status"] = "error"
        log["workflows"].append(entry)

    # ---- 4) JSONログ出力（1実行=1ファイル）----
    log["finished"] = datetime.datetime.now().isoformat(timespec="seconds")
    fname = started.strftime("%Y%m%d%H%M%S") + "_test.json"
    out_path = os.path.join(log_dir, fname)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

    # 標準出力に要約（BAT/コンソールで見える形）
    print("=" * 60)
    print("[ComfyUI CPU TEST] 検証結果サマリ")
    print("  status        :", log["status"])
    pc = log["package_check"] or {}
    print("  package_check :", pc.get("status"),
          "(nodes={}, import_failed={})".format(pc.get("total_nodes"),
                                                 len(pc.get("import_failed", []))))
    print("  workflows     :", len(log["workflows"]), "件")
    for w in log["workflows"]:
        print("    - [{}] {} {}".format(
            w["status"], os.path.basename(w["file"]),
            "({})".format(w.get("format", "")) if w.get("format") else ""))
    print("  log file      :", out_path)
    print("=" * 60)

    # status=error なら終了コード1
    sys.exit(0 if log["status"] != "error" else 1)


if __name__ == "__main__":
    main()
