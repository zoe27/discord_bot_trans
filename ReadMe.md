## 环境配置
1. **安装 Python**: 确保已安装 Python 3.8 或更高版本。
2. **安装依赖**: 使用以下命令安装项目所需的依赖库：
   ```bash
   pip install -r requirements.txt
   ```
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