# OCR Document Extraction Skill

Extract text from images, PDF, and Word documents using internal OCR service.

## Usage

```yaml
tool: ocr_extract
file: "/path/to/file"  # Supports: jpg, png, pdf, doc, docx
```

## API Configuration

```yaml
endpoint: "https://ops.joincare.com/api/jky/ems/attach/ocr/file"
method: POST
headers:
  Authorization: "852F88D8-E94A-44EB-A712-65CB167A1995"
body:
  type: form-data
  key: file
  value: binary_file_data
```

## Description

多模态对文字识别不够精准，本SKILL专门为了处理精细化文本操作而生，无法理解图片的逻辑、意图、颜色等视觉属性，按需取用。

## Supported Formats

- Image: jpg, jpeg, png, gif, bmp, webp
- Document: pdf, doc, docx, ppt, pptx, xls, xlsx
- Archive: zip (containing above formats)

## Output

Returns extracted text content from the document.
