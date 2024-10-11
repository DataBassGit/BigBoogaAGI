# Installation Guide

This guide will walk you through the steps required to install **AgentForge** on your system.

---

## Installation Steps

### 1. Ensure Python is Installed

- **Python Version**: AgentForge requires **Python 3.11**.
- **Check Python Version**:

  ```shell
  python3 --version
  ```
  
  If Python is not installed or the version is anything other than **3.11**, download **version 3.11** from the official [Python website](https://www.python.org/downloads/).

### 2. Set Up a Virtual Environment (Optional But Recommended)

Using a virtual environment helps avoid conflicts with system-wide packages.

- **Create a Virtual Environment**:

  ```shell
  python3.11 -m venv venv
  ```

- **Activate the Virtual Environment**:

  - On **Unix/macOS**:

    ```shell
    source venv/bin/activate
    ```

  - On **Windows**:

    ```shell
    venv\Scripts\activate
    ```

### 3. Install AgentForge

With the virtual environment activated, install **AgentForge** using pip:

```shell
pip install agentforge
```

### 4. Set Up Environment Variables

Depending on the language model service you plan to use with **AgentForge**, you may need to set up environment variables with your API keys. If you're using local models like **LM Studio** or **Ollama**, you do **not** need to set up environment variables for API keys.

#### For OpenAI:

```bash
export OPENAI_API_KEY='your-openai-api-key'
```

#### For Anthropic:

```bash
export ANTHROPIC_API_KEY='your-anthropic-api-key'
```

#### For Google Gemini:

```bash
export GOOGLE_API_KEY='your-google-api-key'
```

### 5. Initialize Your Project

Navigate to your project directory and initialize your **AgentForge** project:

```shell
python -m agentforge.init_agentforge
```

This command creates a new `.agentforge` folder in your project with sub-folders containing **YAML** files:

```
your_project/
  .agentforge/
    actions/
    personas/
    prompts/
    settings/
    tools/
```

---

## Using AgentForge

Now that your project is set up, you can proceed to the [Using AgentForge Guide](UsingAgentForge.md) to learn how to run agents and build your solutions. This guide provides examples and instructions on how to create and interact with agents using **AgentForge**.

---

## Next Steps

- Review the [Prerequisites Guide](PrerequisitesGuide.md) if you haven't set up API keys or other necessary configurations.

- If you're having trouble with **AgentForge**, please head over to the [Troubleshooting Guide](TroubleshootingGuide.md) for solutions to common issues.
