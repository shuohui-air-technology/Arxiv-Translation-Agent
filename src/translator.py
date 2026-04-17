import re
import requests
import time
import sys
import os

API_KEY = "YOUR_API_KEY_HERE" 
API_URL = "URL" 
MODEL_NAME = "DeepSeek-V3-250324" 

def run_translator(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"错误：找不到输入文件 {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    # --- 公式保护 ---
    math_blocks = []
    def replace_math(match):
        math_blocks.append(match.group(0))
        return f"___MATH_BLOCK_{len(math_blocks)-1}___"

    text_safe = re.sub(r'(?<!\\)\$\$[\s\S]*?(?<!\\)\$\$', replace_math, text)
    text_safe = re.sub(r'(?<!\\)\$(?!\d|\s)(?:(?!\n\n)[^$]){1,800}?(?<!\\|\s)\$', replace_math, text_safe)

    # --- 物理切分 ---
    paragraphs = text_safe.split("\n")
    chunks = []
    current_chunk = ""
    for p in paragraphs:
        if len(current_chunk) + len(p) < 1500:
            current_chunk += p + "\n"
        else:
            if current_chunk.strip():
                chunks.append(current_chunk)
            current_chunk = p + "\n"
    if current_chunk.strip():
        chunks.append(current_chunk)
        
    print(f"解析成功，待翻译文档已切分为 {len(chunks)} 块。")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    system_prompt = """
    你是一个专业的学术文献翻译专家。请将以下英文文献段落准确、流畅地翻译成中文。
    要求：
    1. 准确翻译学术正文内容，保持学术论文的严谨语气。
    2. 专有名词（如算法名、模型名）、代码块（```内的内容）以及末尾的参考文献列表请保持英文原文，不需要强行翻译。
    3. 绝对不能修改、翻译或删除任何形如 ___MATH_BLOCK_X___ 的占位符标记。
    4. 所有的中文汉字与保留的英文字母、数字、占位符之间，请自动补充一个半角空格。
    5. 请直接输出翻译后的正文，绝不要包含任何额外的解释、开场白或对话。
    """

    def translate_single_chunk(content, retry_count=3):
        for attempt in range(retry_count):
            current_temp = 0.3 + (attempt * 0.2)
            if current_temp > 0.9: current_temp = 0.9
            
            payload = {
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content}
                ],
                "temperature": current_temp 
            }
            
            try:
                response = requests.post(API_URL, headers=headers, json=payload, proxies={"http": None, "https": None}, timeout=120)
                if response.status_code == 200:
                    res_text = response.json()["choices"][0]["message"]["content"]
                    
                    content_no_code = re.sub(r'```[\s\S]*?```', '', content)
                    res_no_code = re.sub(r'```[\s\S]*?```', '', res_text)
                    
                    orig_en_len = len(re.findall(r'[a-zA-Z]', content_no_code))
                    res_zh_len = len(re.findall(r'[\u4e00-\u9fa5]', res_no_code))
                    
                    if orig_en_len > 100 and res_zh_len < (orig_en_len * 0.2):
                        time.sleep(2)
                        continue
                            
                    return res_text
            except Exception:
                time.sleep(2)
        return None

    def recursive_translate(content, depth=0, max_depth=3):
        res = translate_single_chunk(content)
        if res is not None:
            return res
            
        if depth < max_depth:
            mid = len(content) // 2
            split_point = content.rfind('\n', 0, mid)
            if split_point == -1: split_point = mid
            
            part1 = content[:split_point]
            part2 = content[split_point:]
            
            res1 = recursive_translate(part1, depth + 1, max_depth)
            res2 = recursive_translate(part2, depth + 1, max_depth)
            
            if res1 and res2:
                return res1 + "\n\n" + res2
                
        return content

    results = [None] * len(chunks)
    for i, chunk in enumerate(chunks):
        print(f"正在处理第 {i+1}/{len(chunks)} 块...", end="\r")
        results[i] = recursive_translate(chunk)

    final_translated_text = "\n\n".join([r for r in results if r])

    for i, block in enumerate(math_blocks):
        final_translated_text = final_translated_text.replace(f"___MATH_BLOCK_{i}___", block)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_translated_text)

    print(f"\n流水线执行完毕！结果已保存至: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("启动命令错误。请使用: python translator.py <输入md文件路径> <输出md文件路径>")
    else:
        run_translator(sys.argv[1], sys.argv[2])