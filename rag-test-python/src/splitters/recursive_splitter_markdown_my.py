from langchain_core.documents import Document
from langchain_text_splitters import MarkdownTextSplitter

readme_text = """# Project Name

> A brief description of your project

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Features

- ✨ Feature 1
- 🚀 Feature 2
- 💡 Feature 3

## Installation

```bash
npm install project-name
```

## Usage

### Basic Usage

```javascript
import { Project } from 'project-name';

const project = new Project();
project.init();
```

### Advanced Usage

```javascript
const project = new Project({
  config: {
    apiKey: 'your-api-key',
    timeout: 5000,
  }
});

await project.run();
```

## API Reference

### `Project`

Main class for the project.

#### Methods

- `init()`: Initialize the project
- `run()`: Run the project
- `stop()`: Stop the project

## Contributing

Contributions are welcome! Please read our [contributing guide](CONTRIBUTING.md).

## License

MIT License"""

readme_doc = Document(page_content=readme_text)

markdown_splitter = MarkdownTextSplitter(
    chunk_size=200,
    chunk_overlap=40,
)

split_documents = markdown_splitter.split_documents([readme_doc])

for index, doc in enumerate(split_documents):
  print(f"第{index}个文档:")
  print(doc)
  print("character length:", len(doc.page_content))
