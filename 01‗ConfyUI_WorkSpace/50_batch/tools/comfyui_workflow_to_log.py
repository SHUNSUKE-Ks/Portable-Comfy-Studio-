#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ComfyUI ワークフロー → JSONログ抽出（画像生成なし・ComfyUI起動なし・負荷ゼロ）

目的:
  ワークフロー(UI形式JSON)を「実行せず」純パースし、生成パラメータ
  (model/lora/prompt/seed/steps/cfg/sampler/scheduler/denoise/resolution 等)を
  抽出して JSONログ1ファイルに記録する。準備フェーズ(グラボなし)で
  「何を生成する設定か」を画像の代わりにテキストで確認するためのもの。

特徴:
  - ComfyUI を import しない。Pythonの標準ライブラリのみ。
  - UI形式(nodes/links)を対象。links を辿って positive/negative や解像度を判定。

使い方（通常はBAT経由）:
  python comfyui_workflow_to_log.py --workflow-dir "<dir>" --log-dir "<dir>"
  python comfyui_workflow_to_log.py --workflow "<file.json>" --log-dir "<dir>"
"""

import argparse
import datetime
import glob
import json
import os
import sys

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 各ノードの widgets_values の並び（UI形式。seed系は control_after_generate が後続する点に注意）
WIDGET_MAP = {
    "CheckpointLoaderSimple": ["ckpt_name"],
    "UNETLoader": ["unet_name", "weight_dtype"],
    "LoraLoader": ["lora_name", "strength_model", "strength_clip"],
    "LoraLoaderModelOnly": ["lora_name", "strength_model"],
    "CLIPTextEncode": ["text"],
    "KSampler": ["seed", "control_after_generate", "steps", "cfg",
                 "sampler_name", "scheduler", "denoise"],
    "KSamplerAdvanced": ["add_noise", "noise_seed", "control_after_generate", "steps",
                         "cfg", "sampler_name", "scheduler", "start_at_step",
                         "end_at_step", "return_with_leftover_noise"],
    "EmptyLatentImage": ["width", "height", "batch_size"],
    "EmptySD3LatentImage": ["width", "height", "batch_size"],
    "ImageScale": ["upscale_method", "width", "height", "crop"],
    "LoadImage": ["image", "upload"],
    "SaveImage": ["filename_prefix"],
}

KSAMPLER_TYPES = {"KSampler", "KSamplerAdvanced"}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--workflow", action="append", default=[], help="対象JSON（複数可）")
    p.add_argument("--workflow-dir", default=None, help="このフォルダ内の*.jsonを全て対象")
    p.add_argument("--log-dir", required=True, help="JSONログ出力先")
    p.add_argument("--mode", default="CPU_TEST_PARAMS")
    return p.parse_args()


def widgets_dict(node):
    """node の widgets_values を名前付き dict にする（既知ノードのみ）。"""
    names = WIDGET_MAP.get(node.get("type"))
    vals = node.get("widgets_values") or []
    if not names:
        return {}
    out = {}
    for i, name in enumerate(names):
        if i < len(vals):
            out[name] = vals[i]
    return out


def input_link(node, input_name):
    for inp in node.get("inputs", []) or []:
        if inp.get("name") == input_name:
            return inp.get("link")
    return None


def build_link_src(data):
    """link_id -> (from_node_id, from_slot)"""
    src = {}
    for ln in data.get("links", []) or []:
        if isinstance(ln, list) and len(ln) >= 5:
            src[ln[0]] = (ln[1], ln[2])
    return src


def trace_text(link_id, nodes_by_id, link_src):
    """link を辿って CLIPTextEncode の text を取得（reroute等は1段だけ追従）。"""
    visited = set()
    cur = link_src.get(link_id)
    while cur and cur[0] not in visited:
        visited.add(cur[0])
        n = nodes_by_id.get(cur[0])
        if not n:
            break
        if n.get("type") == "CLIPTextEncode":
            return widgets_dict(n).get("text"), n.get("id")
        # 1入力だけのノード(Reroute等)なら辿る
        in_links = [i.get("link") for i in (n.get("inputs") or []) if i.get("link") is not None]
        if len(in_links) == 1:
            cur = link_src.get(in_links[0])
        else:
            return None, n.get("id")  # 判定不能（複合ノード等）
    return None, None


def resolve_resolution(ksampler, nodes_by_id, link_src):
    """KSampler の latent_image を辿って解像度と txt2img/img2img を判定。"""
    lat = input_link(ksampler, "latent_image") or input_link(ksampler, "samples")
    cur = link_src.get(lat)
    visited = set()
    while cur and cur[0] not in visited:
        visited.add(cur[0])
        n = nodes_by_id.get(cur[0])
        if not n:
            break
        t = n.get("type")
        wd = widgets_dict(n)
        if t in ("EmptyLatentImage", "EmptySD3LatentImage"):
            return f"{wd.get('width')}x{wd.get('height')}", "txt2img"
        if t == "ImageScale":
            return f"{wd.get('width')}x{wd.get('height')}", "img2img"
        if t == "VAEEncode":
            nxt = input_link(n, "pixels")
            cur = link_src.get(nxt)
            continue
        # それ以外は最初の入力を辿る
        in_links = [i.get("link") for i in (n.get("inputs") or []) if i.get("link") is not None]
        cur = link_src.get(in_links[0]) if in_links else None
    return None, None


def extract(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    entry = {"workflow_file": os.path.basename(path), "path": path, "status": "ok"}

    nodes = data.get("nodes")
    if not isinstance(nodes, list) or "links" not in data:
        entry["status"] = "error"
        entry["error_message"] = "UI形式(nodes/links)のワークフローではありません"
        return entry

    nodes_by_id = {n.get("id"): n for n in nodes}
    link_src = build_link_src(data)

    # checkpoint / lora
    checkpoint = None
    loras = []
    for n in nodes:
        t = n.get("type")
        if t == "CheckpointLoaderSimple":
            checkpoint = widgets_dict(n).get("ckpt_name")
        elif t in ("LoraLoader", "LoraLoaderModelOnly"):
            wd = widgets_dict(n)
            loras.append({"name": wd.get("lora_name"),
                          "strength_model": wd.get("strength_model"),
                          "strength_clip": wd.get("strength_clip")})

    entry["model"] = checkpoint
    entry["loras"] = loras

    # KSampler（複数あれば配列）
    samplers = []
    for n in nodes:
        if n.get("type") not in KSAMPLER_TYPES:
            continue
        wd = widgets_dict(n)
        pos_text, pos_id = trace_text(input_link(n, "positive"), nodes_by_id, link_src)
        neg_text, neg_id = trace_text(input_link(n, "negative"), nodes_by_id, link_src)
        resolution, gen_type = resolve_resolution(n, nodes_by_id, link_src)
        samplers.append({
            "ksampler_id": n.get("id"),
            "seed": wd.get("seed", wd.get("noise_seed")),
            "steps": wd.get("steps"),
            "cfg": wd.get("cfg"),
            "sampler": wd.get("sampler_name"),
            "scheduler": wd.get("scheduler"),
            "denoise": wd.get("denoise"),
            "resolution": resolution,
            "gen_type": gen_type,
            "positive_prompt": pos_text,
            "negative_prompt": neg_text,
        })

    if not samplers:
        entry["status"] = "warning"
        entry["note"] = "KSampler が見つかりませんでした（生成系でない可能性）"
    entry["samplers"] = samplers

    # 出力保存先（SaveImage の filename_prefix）
    save_paths = [widgets_dict(n).get("filename_prefix")
                  for n in nodes if n.get("type") == "SaveImage"]
    entry["save_path"] = [s for s in save_paths if s]

    return entry


def main():
    cli = parse_args()
    os.makedirs(cli.log_dir, exist_ok=True)

    targets = list(cli.workflow)
    if cli.workflow_dir and os.path.isdir(cli.workflow_dir):
        targets += sorted(glob.glob(os.path.join(cli.workflow_dir, "*.json")))
    targets = list(dict.fromkeys(os.path.abspath(t) for t in targets))

    started = datetime.datetime.now()
    log = {
        "timestamp": started.isoformat(timespec="seconds"),
        "mode": cli.mode,
        "note": "画像生成なし・ComfyUI起動なしで抽出したパラメータログ",
        "count": len(targets),
        "workflows": [],
    }
    overall = "ok"
    for path in targets:
        try:
            e = extract(path)
        except Exception as ex:
            e = {"workflow_file": os.path.basename(path), "path": path,
                 "status": "error", "error_message": f"{type(ex).__name__}: {ex}"}
        if e.get("status") == "error":
            overall = "error"
        log["workflows"].append(e)
    log["status"] = overall

    fname = started.strftime("%Y%m%d%H%M%S") + "_params.json"
    out_path = os.path.join(cli.log_dir, fname)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

    # コンソール要約
    print("=" * 60)
    print("[Workflow → JSON Log] 抽出結果")
    print("  status   :", log["status"])
    print("  count    :", log["count"])
    for w in log["workflows"]:
        s = w.get("samplers", [{}])
        s0 = s[0] if s else {}
        print("  - [{}] {}".format(w.get("status"), w.get("workflow_file")))
        print("      model={} res={} steps={} cfg={} sampler={}".format(
            w.get("model"), s0.get("resolution"), s0.get("steps"),
            s0.get("cfg"), s0.get("sampler")))
    print("  log file :", out_path)
    print("=" * 60)
    sys.exit(0 if log["status"] != "error" else 1)


if __name__ == "__main__":
    main()
