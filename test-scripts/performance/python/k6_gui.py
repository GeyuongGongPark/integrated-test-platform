import subprocess
import os
import tkinter as tk
from tkinter import ttk
import threading
import platform
# from dotenv import load_dotenv

from k6_options import (
    ENV_TYPE_OPTIONS,
    DOCUMENT_TYPE_OPTIONS,
    DRAFT_TYPE_OPTIONS,
    CONTRACT_UPLOAD_OPTIONS,
    EDITOR_USE_OPTIONS,
    CONTRACT_TYPE_OPTIONS,
    SECURITY_TYPE_OPTIONS,
    REVIEW_TYPE_OPTIONS,
    ADVICE_TYPE_OPTIONS
)

root = tk.Tk()
root.title("LFBZ 문서 생성기")

# 1. 메인 프레임(좌우 2단)
main_frame = tk.Frame(root)
main_frame.pack(padx=20, pady=20, fill="both", expand=True)

# 2. 왼쪽: 설정용 프레임
left_frame = tk.Frame(main_frame)
left_frame.pack(side="left", fill="y", padx=(0, 10))

# 3. 오른쪽: 콘솔창 프레임
right_frame = tk.Frame(main_frame)
right_frame.pack(side="left", fill="both", expand=True)

# 환경 선택 Combobox
env_label = tk.Label(left_frame, text="환경 선택 :").pack(anchor="w", pady=5)
# env_options = ["prod", "alpha"]
env_var = tk.StringVar(value=list(ENV_TYPE_OPTIONS.keys())[0])
env_combo = ttk.Combobox(left_frame, textvariable=env_var, values=list(ENV_TYPE_OPTIONS.keys()), state="readonly")
env_combo.pack(anchor="w", pady=5)

# DOCUMENT_TYPE Combobox
tk.Label(left_frame, text="문서 구분 :").pack(anchor="w", pady=5)
document_type_var = tk.StringVar(value=list(DOCUMENT_TYPE_OPTIONS.keys())[0])
document_type_combo = ttk.Combobox(left_frame, textvariable=document_type_var, values=list(DOCUMENT_TYPE_OPTIONS.keys()), state="readonly")
document_type_combo.pack(anchor="w", pady=5)

# 하위 옵션 Combobox 및 Label (초기에는 생성만, 배치는 동적으로)
draft_type_label = tk.Label(left_frame, text="계약 구분 :")
draft_type_var = tk.StringVar(value=list(DRAFT_TYPE_OPTIONS.keys())[0])
draft_type_combo = ttk.Combobox(left_frame, textvariable=draft_type_var, values=list(DRAFT_TYPE_OPTIONS.keys()), state="readonly")

contract_upload_label = tk.Label(left_frame, text="계약서 업로드 여부 :")
contract_upload_var = tk.StringVar(value=list(CONTRACT_UPLOAD_OPTIONS.keys())[0])
contract_upload_combo = ttk.Combobox(left_frame, textvariable=contract_upload_var, values=list(CONTRACT_UPLOAD_OPTIONS.keys()), state="readonly")

editor_use_label = tk.Label(left_frame, text="편집기 사용 여부 :")
editor_use_var = tk.StringVar(value=list(EDITOR_USE_OPTIONS.keys())[0])
editor_use_combo = ttk.Combobox(left_frame, textvariable=editor_use_var, values=list(EDITOR_USE_OPTIONS.keys()), state="readonly")

contract_type_label = tk.Label(left_frame, text="계약서 유형 :")
contract_type_var = tk.StringVar(value=list(CONTRACT_TYPE_OPTIONS.keys())[0])
contract_type_combo = ttk.Combobox(left_frame, textvariable=contract_type_var, values=list(CONTRACT_TYPE_OPTIONS.keys()), state="readonly")

security_type_label = tk.Label(left_frame, text="보안여부 :")
security_type_var = tk.StringVar(value=list(SECURITY_TYPE_OPTIONS.keys())[0])
security_type_combo = ttk.Combobox(left_frame, textvariable=security_type_var, values=list(SECURITY_TYPE_OPTIONS.keys()), state="readonly")

review_type_label = tk.Label(left_frame, text="검토 여부 :")
review_type_var = tk.StringVar(value=list(REVIEW_TYPE_OPTIONS.keys())[0])
review_type_combo = ttk.Combobox(left_frame, textvariable=review_type_var, values=list(REVIEW_TYPE_OPTIONS.keys()), state="readonly")

advice_type_label = tk.Label(left_frame, text="자문 분류")
advice_type_var = tk.StringVar(value=list(ADVICE_TYPE_OPTIONS.keys())[0])
advice_type_combo = ttk.Combobox(left_frame, textvariable=advice_type_var, values=list(ADVICE_TYPE_OPTIONS.keys()), state="readonly")

# 오른쪽: 콘솔창
output_text = tk.Text(right_frame, height=30, width=60)
output_text.pack(fill="both", expand=True)

def on_document_type_change(event=None):
    doc_type = DOCUMENT_TYPE_OPTIONS[document_type_var.get()]
    drf_type = DRAFT_TYPE_OPTIONS[draft_type_var.get()]
    cont_type = CONTRACT_UPLOAD_OPTIONS[contract_upload_var.get()]
    # 모두 숨김
    draft_type_label.pack_forget()
    draft_type_combo.pack_forget()
    contract_upload_label.pack_forget()
    contract_upload_combo.pack_forget()
    editor_use_label.pack_forget()
    editor_use_combo.pack_forget()
    contract_type_label.pack_forget()
    contract_type_combo.pack_forget()
    security_type_label.pack_forget()
    security_type_combo.pack_forget()
    review_type_label.pack_forget()
    review_type_combo.pack_forget()
    advice_type_label.pack_forget()
    advice_type_combo.pack_forget()
    # 계약 검토(clm)일 때만 하위 옵션 노출
    if doc_type == "clm":
        draft_type_label.pack(anchor="w", pady=5)
        draft_type_combo.pack(anchor="w", pady=5)
        editor_use_label.pack(anchor="w", pady=5)
        editor_use_combo.pack(anchor="w", pady=5)
        contract_type_label.pack(anchor="w", pady=5)
        contract_type_combo.pack(anchor="w", pady=5)
        security_type_label.pack(anchor="w", pady=5)
        security_type_combo.pack(anchor="w", pady=5)
        review_type_label.pack(anchor="w", pady=5)
        review_type_combo.pack(anchor="w", pady=5)
        # DRAFT_TYPE이 '해지'일 때만 contract_upload 노출
        if drf_type == "stop":
            contract_upload_label.pack(anchor="w", pady=5)
            contract_upload_combo.pack(anchor="w", pady=5)
            if cont_type == "not_use":
                editor_use_label.pack_forget()
                editor_use_combo.pack_forget()
                contract_type_label.pack_forget()
                contract_type_combo.pack_forget()
    elif doc_type == "advice":
        advice_type_label.pack(anchor="w", pady=5)
        advice_type_combo.pack(anchor="w", pady=5)
        contract_type_label.pack(anchor="w", pady=5)
        contract_type_combo.pack(anchor="w", pady=5)
        editor_use_label.pack(anchor="w", pady=5)
        editor_use_combo.pack(anchor="w", pady=5)
        security_type_label.pack(anchor="w", pady=5)
        security_type_combo.pack(anchor="w", pady=5)
    else:
        security_type_label.pack(anchor="w", pady=5)
        security_type_combo.pack(anchor="w", pady=5)

document_type_combo.bind("<<ComboboxSelected>>", on_document_type_change)
draft_type_combo.bind("<<ComboboxSelected>>", on_document_type_change)
contract_upload_combo.bind("<<ComboboxSelected>>", on_document_type_change)
on_document_type_change()

def load_env_file(env_file, env_dict):
    if not os.path.exists(env_file):
        return
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                env_dict[key.strip()] = value.strip()

def run_k6():
    document_type_label = document_type_var.get()
    draft_type_label_val = draft_type_var.get()
    contract_upload_label_val = contract_upload_var.get()
    editor_use_label_val = editor_use_var.get()
    contract_type_label_val = contract_type_var.get()
    security_type_label_val = security_type_var.get()
    review_type_label_val = review_type_var.get()
    advice_type_label_val = advice_type_var.get()
    document_type = DOCUMENT_TYPE_OPTIONS[document_type_label]
    draft_type = DRAFT_TYPE_OPTIONS[draft_type_label_val]
    contract_upload = CONTRACT_UPLOAD_OPTIONS[contract_upload_label_val]
    editor_use = EDITOR_USE_OPTIONS[editor_use_label_val]
    contract_type = CONTRACT_TYPE_OPTIONS[contract_type_label_val]
    security_type = SECURITY_TYPE_OPTIONS[security_type_label_val]
    review_type = REVIEW_TYPE_OPTIONS[review_type_label_val]
    advice_type = ADVICE_TYPE_OPTIONS[advice_type_label_val]
    selected_env_display = env_var.get()
    selected_env = ENV_TYPE_OPTIONS[selected_env_display]
    env_file = f".env.{selected_env}"
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    if document_type == "clm":
        js_path = os.path.abspath(os.path.join(BASE_DIR, "../clm/clm_draft.js"))
    elif document_type == "advice":
        js_path = os.path.abspath(os.path.join(BASE_DIR, "../advice/advice_draft.js"))
    elif document_type == "litigation":
        js_path = os.path.abspath(os.path.join(BASE_DIR, "../litigation/litigation_draft.js"))
    else:
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "지원하지 않는 문서 타입입니다.")
        return
    cmd = ["k6", "run"]
    if document_type == "clm":
        cmd += [
            "--env", f"DRAFT_TYPE={draft_type}",
            "--env", f"CONTRACT_TYPE={contract_type}",
            "--env", f"EDITOR_USE={editor_use}",
            "--env", f"SECURITY_TYPE={security_type}",
            "--env", f"REVIEW_TYPE={review_type}",
        ]
        if draft_type == "stop":
            cmd += ["--env", f"CONTRACT_UPLOAD={contract_upload}"]
    elif document_type == "advice":
        cmd += [
            "--env", f"ADVICE_TYPE={advice_type}",
            "--env", f"CONTRACT_TYPE={contract_type}",
            "--env", f"EDITOR_USE={editor_use}",
            "--env", f"SECURITY_TYPE={security_type}",
        ]
    elif document_type == "litigation":
        cmd += [
            "--env", f"SECURITY_TYPE={security_type}",
        ]
    cmd.append(js_path)
    cmd_str = " ".join(cmd)

    if platform.system() == "Windows":
        env = os.environ.copy()
        env_file_path = os.path.abspath(os.path.join(BASE_DIR, f"../.env.{selected_env}"))
        load_env_file(env_file_path, env)
        full_cmd = cmd_str
    else:
        env_file = f".env.{selected_env}"
        full_cmd = f"source {env_file} && {cmd_str}"
        env = None

    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, f"[실행명령어]\n{full_cmd}\n\n[실행결과]\n")
    output_text.see(tk.END)

    def stream_k6():
        if platform.system() == "Windows":
            process = subprocess.Popen(
                full_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                shell=True,
                env=env,
                encoding="utf-8"
            )
        else:
            process = subprocess.Popen(
                full_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                shell=True,
                executable="/bin/bash"
            )
        if process.stdout:
            for line in iter(process.stdout.readline, ''):
                output_text.insert(tk.END, line)
                output_text.see(tk.END)
            process.stdout.close()
        process.wait()

    threading.Thread(target=stream_k6, daemon=True).start()
tk.Button(left_frame, text="문서생성", command=run_k6).pack(side="bottom", fill="x", pady=10)
root.mainloop()