# Markdown 文档翻译器

基于 LLM 的 Markdown 文档翻译工具，支持按一级标题自动切分文档并逐段翻译。

## 功能特点

- **智能切片**: 按一级标题 (`# `) 自动切分文档
- **API 兼容**: 支持 OpenAI Compatible API，可接入多种 LLM 服务
- **并发控制**: 支持配置并发请求数，提高处理效率
- **错误处理**: 单切片失败不影响整体流程，自动保留原文
- **详细日志**: 实时显示处理状态和耗时

## 快速开始

### 1. 安装依赖【推荐使用uv】

```bash
uv venv
.venv/Scripts/activate
uv pip install -r requirements.txt
```

### 2. 配置 API

复制环境变量示例文件并设置 API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API Key：

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
```

### 3. 配置参数（可选）

编辑 `config.yaml` 自定义 API 参数：

```yaml
api:
  base_url: "https://api.openai.com/v1"
  model: "gpt-3.5-turbo"
  temperature: 0.7
  max_tokens: 2048
concurrency: 1
slicing_level: 1   # 1 = split by # headers only; 2 = split by # and ## headers
```

### 4. 运行翻译

```bash
python main.py input.md
```

翻译后的文件保存为 `input_translated.md`

## 命令行参数

```
usage: md-translator [-h] [-c CONFIG] [-e ENV] [-v] input_file

Translate Markdown documents using LLM APIs

positional arguments:
  input_file            Path to the input Markdown file

optional arguments:
  -h, --help            Show this help message
  -c, --config CONFIG   Path to config.yaml (default: config.yaml)
  -e, --env ENV         Path to .env file (default: .env)
  -v, --verbose         Enable verbose output
```

## 项目结构

```
md_translator/
├── main.py                 # 命令行入口
├── cli/                    # 命令行接口
├── config/                 # 配置管理
├── core/                   # 核心业务逻辑
│   ├── slicer.py           # Markdown 切片
│   ├── translator.py       # 翻译流程控制
│   └── assembler.py        # 结果组装
├── api/                    # API 交互
│   ├── client.py           # API 客户端
│   └── prompt_builder.py   # Prompt 构建器
├── utils/                  # 工具函数
└── tests/                  # 测试用例
```

## GUI 使用

安装 PyQt5 依赖后，运行:

```bash
python gui_main.py
```

即可启动图形界面。

## 开发

运行测试：

```bash
pytest
```

## 许可证

MIT License