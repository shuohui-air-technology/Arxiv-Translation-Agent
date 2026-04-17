# 🚀 Academic Paper Translation Agent

基于大语言模型（LLM）的工业级高鲁棒性学术论文自动化翻译流水线。

## ✨ 核心特性

- **物理级断点防吞噬机制**：自主编写高强度 RegEx 隔离罩，彻底解决大模型翻译中由于 LaTeX 占位符跨段落匹配导致的公式无法正常显示问题，完美保护公式与排版。
- **Token 优化与精准局部增量翻译**：首创基于深度的递归二分切分翻译策略（Divide and Conquer）。当遇到超长附录触发大模型“偷懒”时，引擎拒绝无意义的全局重试，而是切碎文本执行局部增量翻译，实现全文**零漏译**。
- **动态升温算法 (Dynamic Temperature)**：内置智能比例质检器，实时监控中英文字符产出比。拦截异常后自动调高 Temperature 重试，打破模型复读死循环。
- **脱机物理剥离**：支持无缝对接基于 Hugging Face 的轻量级本地视觉解析模型（如 Marker），实现极高的数据隐私与合规性。

## 📦 快速开始

### 1. 环境准备
项目已在 macOS (Apple Silicon) 环境下完成极端边界测试。
```bash
pip install -r requirements.txt
```

### 2. 配置密钥
在 `translator.py` 顶部填入你的 API Key：
```python
API_KEY = "YOUR_API_KEY_HERE"
```

### 3. 一键运行
采用标准的 CLI 传参调用：
```bash
python translator.py <输入的Markdown文件路径> <输出的Markdown文件路径>
```
