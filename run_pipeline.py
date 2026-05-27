import os
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
import argparse
import subprocess
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(os.path.dirname(BASE_DIR), '.venv', 'Scripts', 'python.exe')

if sys.platform != 'win32':
    VENV_PYTHON = os.path.join(os.path.dirname(BASE_DIR), '.venv', 'bin', 'python')

SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')

def run_step(script_name, description):
    print(f"\n{'='*60}")
    print(f"▶ {description}")
    print(f"{'='*60}")
    
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    start = time.time()
    
    result = subprocess.run(
        [VENV_PYTHON, script_path],
        cwd=BASE_DIR,
        capture_output=False
    )
    
    elapsed = time.time() - start
    
    if result.returncode != 0:
        print(f"\n❌ {description} FAILED (exit code: {result.returncode})")
        return False
    
    print(f"\n✅ {description} completed in {elapsed:.1f}s")
    return True

def main():
    parser = argparse.ArgumentParser(description='TikTok 评论分析流水线 - 从CSV到HTML报告')
    parser.add_argument('--input', '-i', type=str, default=None,
                        help='输入CSV文件路径（默认: data/TikTok.csv）')
    parser.add_argument('--skip-embedding', action='store_true',
                        help='跳过Embedding生成（如果embeddings.npy已存在）')
    parser.add_argument('--skip-analysis', action='store_true',
                        help='跳过LLM分析（如果result.json已存在）')
    args = parser.parse_args()
    
    if args.input:
        input_csv = os.path.abspath(args.input)
        if not os.path.exists(input_csv):
            print(f"❌ 文件不存在: {input_csv}")
            sys.exit(1)
        
        target_path = os.path.join(BASE_DIR, 'data', 'TikTok.csv')
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        import shutil
        shutil.copy2(input_csv, target_path)
        print(f"📂 已复制输入文件到: {target_path}")
    
    total_start = time.time()
    
    print("""
╔══════════════════════════════════════════════════════════╗
║     TikTok 评论分析流水线  v4.0                           ║
║     CSV → 清洗 → Embedding → 分类 → LLM分析 → 情绪 → HTML║
╚══════════════════════════════════════════════════════════╝
""")
    
    steps = []
    
    if not args.skip_embedding:
        steps.append(('step1_embedding.py', 'Step 1/3: 数据清洗 + Embedding生成'))
    
    steps.append(('step3_summary.py', 'Step 2/3: Category分类 + LLM动态分析 + 情绪检测'))
    steps.append(('step4_html.py',   'Step 3/3: 生成HTML报告'))
    
    for script_name, description in steps:
        if not run_step(script_name, description):
            print(f"\n❌ 流水线中断于: {description}")
            sys.exit(1)
    
    total_time = time.time() - total_start
    
    output_html = os.path.join(BASE_DIR, 'outputs', 'report.html')
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║  ✅ 流水线执行完成！                                      ║
║                                                          ║
║  总耗时: {total_time:.1f}s                                        ║
║  报告位置: {output_html}                       ║
║                                                          ║
║  用浏览器打开即可查看                                     ║
╚══════════════════════════════════════════════════════════╝
""")

if __name__ == '__main__':
    main()
