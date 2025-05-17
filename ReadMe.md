# ScreenTranslator - 屏幕实时翻译工具

## 项目简介 / Project Overview
**ScreenTranslator** 是一个基于 Python 的屏幕翻译工具，集成了截图、OCR 文字识别、自动翻译、实时翻译和翻译功能。  
ScreenTranslator is a Python-based screen translation tool that integrates screenshot capture, OCR text recognition, automatic translation, real-time translation, and translation features.

### 功能特点 / Features
- **屏幕截图 / Screenshot**: 选择屏幕区域并保存截图。
- **OCR 识别 / OCR Recognition**: 使用 Tesseract OCR 识别截图中的文字。
- **翻译 / Translation**: 使用 Google Translate 或有道翻译将识别的文字翻译为目标语言。

## 环境配置 / Environment Setup

1. **安装 Python / Install Python**: 确保已安装 Python 3.8 或更高版本，本项目使用的是 3.11。
2. **安装依赖 / Install Dependencies**: 使用以下命令安装项目所需的依赖库：
   ```bash
   pip install -r requirements.txt
3. **配置 Tesseract**:
   - 下载并安装 [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)。
   - 确保将 Tesseract 的路径添加到系统环境变量中。
   - 如果需要，修改 `translate_screenshot.py` 中的 `pytesseract.pytesseract.tesseract_cmd` 路径。

## 运行项目
1. **运行主窗口**:
   ```bash
   python core/main.py
   ```
   这将启动主窗口，提供屏幕截图、OCR 和翻译功能。

## 注意事项
- 确保所有依赖库和工具（如 Tesseract）已正确安装。
- 如果遇到问题，请检查依赖版本是否与 `requirements.txt` 中的版本一致。

## 项目功能
- **屏幕截图**: 选择屏幕区域并保存截图。
- **OCR 识别**: 使用 Tesseract 识别截图中的文字。
- **翻译**: 使用 Google Translate 将识别的文字翻译为目标语言。

## 打包项目
pyinstaller --onefile --windowed --name ScreenTranslator \
  --add-data "core/tessdata:tessdata" core/main.py