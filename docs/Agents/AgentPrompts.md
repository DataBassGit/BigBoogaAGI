# Agent Prompts Guide

---

## Introduction

Prompt templates are at the heart of the **AgentForge** framework. They define how agents interact with users and Large Language Models (LLMs). Written in **YAML** format, prompt templates allow you to craft dynamic, context-aware conversations and behaviors for your agents.

---

## Table of Contents

1. [Organizing Agent Prompt Files](#organizing-agent-prompt-files)
2. [Understanding Prompt Files](#understanding-prompt-files)
3. [Crafting Prompts with System and User Sections](#crafting-prompts-with-system-and-user-sections)
4. [Dynamic Variables in Prompts](#dynamic-variables-in-prompts)
5. [Handling Special Cases and Code Snippets](#handling-special-cases-and-code-snippets)
6. [Combining Persona Data](#combining-persona-data)
7. [Important Considerations](#important-considerations)
8. [Best Practices for Prompt Design](#best-practices-for-prompt-design)
9. [Example: Bringing It All Together](#example-bringing-it-all-together)
10. [Conclusion](#conclusion)
11. [Additional Resources](#additional-resources)

---

## Organizing Agent Prompt Files

Each agent requires a corresponding **YAML** prompt file located within the `.agentforge/prompts/` directory of your project. This file contains the prompt templates that guide the agent's interactions.

### Naming Convention

- **Match the `agent_name`**: The prompt template **YAML** file **must** have the same name as the agent's `agent_name`. The `agent_name` is determined by the `name` parameter provided during agent initialization or defaults to the agent's class name if no name is given.

  **Example**:

  ```python
  # echo_agent.py
  from agentforge.agent import Agent

  # Option 1: Using the default class name as agent_name
  class EchoAgent(Agent):
      pass  # agent_name defaults to 'EchoAgent' if no name is provided

  # Option 2: Specifying a custom agent_name during initialization
  agent = Agent(agent_name="CustomEchoAgent")
  ```

  - For `EchoAgent`, the corresponding prompt file should be named `EchoAgent.yaml`.
  - For `agent = Agent(agent_name="CustomEchoAgent")`, the prompt file should be named `CustomEchoAgent.yaml`.

### Directory Structure

You can organize your agents and prompt files into subdirectories for better categorization, especially when dealing with multiple agents.

**Example Structure**:

```
.agentforge/
└── prompts/
    ├── EchoAgent.yaml
    ├── CustomEchoAgent.yaml
    ├── topic_qanda/
    │   ├── QuestionGenerator.yaml
    │   └── AnswerAgent.yaml
    └── other/
        └── HelperAgent.yaml
```

- The system automatically searches all subdirectories within `.agentforge/prompts/` to find agent prompt template files.
- **Tip**: Organize agents by functionality or project modules for easier management.

---

## Understanding Prompt Files

Prompt files define the dialogue structures that agents use when interacting with users and LLMs. They are composed of `System` and `User` prompts, each containing one or more **sub-prompts**.

### Basic Structure

The `System` and `User` prompts can be defined in two ways:

1. **As Strings**: Providing the entire prompt template directly as a string.
2. **As a Set of Sub-Prompts**: Organizing the prompt into sub-sections for modularity and conditional rendering.

#### Option 1: Prompts as Strings

In the simplest form, you can define the `System` and `User` prompts directly as strings without any sub-prompts.

**Example Prompt File (`SimpleEcho.yaml`):**

```yaml
Prompts:
  System: You are an assistant that echoes the user's input.
  User: {user_input}
```

- **System Prompt**: A single string providing context or instructions to the assistant.
- **User Prompt**: A single string that may include variables to be replaced at runtime.

#### Option 2: Prompts with Sub-Prompts

Alternatively, you can structure your prompts using sub-prompts for better organization and flexibility.

**Example Prompt File (`EchoAgent.yaml`):**

```yaml
Prompts:
  System:
    Name: You are {name}.
    Description: You are an assistant that echoes the user's input.
  User:
    Instructions: Echo what the user says.
    Echo: |
      user input:
      {user_input}
```

### Notes:

- **Prompts**: The root key containing the `System` and `User` prompts.
- **System Prompt**: Provides the AI assistant with system instructions.
- **User Prompt**: Represents the user's input.
- **Sub-Prompts**: Named sections under `System` and `User` that can contain static text or dynamic variables.
- **Variables**: Placeholders within `{}` that will be dynamically replaced at runtime.

---

## Crafting Prompts with System and User Sections

### Prompt Structure

- **System Prompt**: Contains sub-prompts that define the assistant's behavior, background, or instructions.
- **User Prompt**: Contains sub-prompts representing user inputs or specific tasks.

**Example Prompt File (`QuestionGenerator.yaml`):**

```yaml
Prompts:
  System:
    Role: You are an assistant that generates questions based on a topic.
    Guidelines: Please ensure the questions are open-ended and thought-provoking.
  User:
    Topic: |
      The topic is: {topic}.
    Instruction: Please generate an insightful question about the topic.
```

### How It Works

- **Sub-Prompts Rendering**:
  - Each sub-prompt under `System` and `User` is processed individually.
  - If all variables within a sub-prompt are provided, it is rendered.
  - Sub-prompts are concatenated to form the final `System` and `User` prompts sent to the LLM.

### Final Prompt Structure

- **Flexibility with LLM APIs**:
  - The agent generates two separate prompts:
    - **System Prompt**: The concatenated and rendered `System` sub-prompts.
    - **User Prompt**: The concatenated and rendered `User` sub-prompts.
  - **API Handling**:
    - Depending on the LLM API you are using, the prompts may be sent differently:
      - **Separate Prompts**: Some APIs (e.g., OpenAI) accept system and user prompts as separate inputs.
      - **Single Prompt**: Other APIs require a single prompt that combines both the system and user messages.
  - **Creating Custom APIs**:
    - The agent provides both the system and user prompts separately in a dictionary variable.
    - It's up to your API implementation to handle these prompts appropriately, either by sending them as separate messages or concatenating them into a single prompt before sending to the LLM.

---

## Dynamic Variables in Prompts

Dynamic variables allow prompts to be flexible and context-aware. Any text enclosed in `{}` that matches a valid Python variable name is considered a variable.

### How Variables Work

- **Detection**: Variables are identified by the `PromptHandling` class using a regular expression that matches valid Python identifiers.
- **Replacement**: At runtime, these variables are replaced with the corresponding values provided to the agent.
- **Conditional Rendering**: Sub-prompts containing variables are only rendered if all required variables are provided.

**Example**:

```yaml
Prompts:
  System: You are a helpful assistant.
  User: {greeting}
```

- If you run the agent with `agent.run(greeting="Hello, AgentForge!")`, the `{greeting}` variable will be replaced accordingly.

### Important Notes

- **Valid Variable Names**: Use variable names that are valid Python identifiers (letters, numbers, underscores, not starting with a number).
- **Missing Variables**: If a required variable is missing, the entire sub-prompt is skipped.
- **Plain Text**: If no placeholders are present in a sub-prompt, it will be rendered as plain text.
- **Invalid Variable Placeholders**: Placeholders that are not valid variable names are left unchanged and will be considered as normal text.

---

## Handling Special Cases and Code Snippets

### Invalid Variable Placeholders

Placeholders within `{}` that are not valid variable names remain unchanged. This is useful for including templates or placeholders in your prompts.

**Example**:

```yaml
Prompts:
  System: You are a helpful assistant.
  User: |
    Please respond in the following format:

    Thoughts: {your thoughts here}
    Response: {your response here}
```

- `{your thoughts here}` and `{your response here}` are not valid variable names and will remain in the prompt.

---

### Including Code Snippets

When including code, **JSON**, etc., in your prompts, you might have curly braces `{}` that are part of the code and not intended for variable replacement. To prevent these from being interpreted as variables, you can escape them using `/{` and `/}`.

#### How to Escape Curly Braces

- **Syntax**: Wrap the curly braces you want to escape with `/{` and `/}`.
  - `/{.../}` will be converted to `{...}` after rendering.
- **Purpose**: This ensures that any content within the escaped braces is **not** treated as a variable and remains unchanged during variable substitution.

**Example**:

```yaml
Prompts:
  System: |
    Here is a JSON template:

    {
      "name": "/{name/}",
      "age": "/{age/}"
    }
  User: Please fill in the template with the appropriate values.
```

- **Rendered System Prompt**:

  ```
  Here is a JSON template:

  {
    "name": "{name}",
    "age": "{age}"
  }
  ```

- In this example, `/{name/}` and `/{age/}` ensure that `{name}` and `{age}` inside the code snippet are **not** treated as variables.

---

## Combining Persona Data

Agents can utilize data from persona files stored in `.agentforge/personas/`. This allows you to define agent-specific information separately from your code and reuse personas across different agents.

**Note**: Prompts **must** include both `System` and `User` sections for the agent to function properly.

**Example Persona File (`Botty.yaml`)**:

```yaml
Name: Botty McBotFace
Description: a generic bot
Location: Dinner Table
Purpose: Pass the butter
```

**Example Prompt File (`BottyAgent.yaml`)**:

```yaml
Prompts:
  System:
    Introduction: |
      You are {Name}, {Description}.
    Details: |
      Your location: {Location}.
      Your purpose: {Purpose}.
  User: Hello! Please introduce yourself.
```

**Usage**:

```python
from agentforge.agent import Agent

# Instantiate the agent with a custom name matching the persona and prompt file
agent = Agent(agent_name="BottyAgent")
response = agent.run()
print(response)
```

**Rendered Prompts**:

- **System Prompt**:

  ```
  You are Botty McBotFace, a generic bot.
  Your location: Dinner Table.
  Your purpose: Pass the butter.
  ```

- **User Prompt**:

  ```
  Hello! Please introduce yourself.
  ```

---

## Important Considerations

### Agent Name and Prompt Matching

- **`agent_name` Determines Prompt File**: The agent will look for a prompt file matching its `agent_name`. This means that if you provide a custom name during initialization, you must have a corresponding prompt file with the same name.

**Example**:

```python
from agentforge.agent import Agent

# Agent will use 'CustomAgent.yaml' as the prompt file
agent = Agent(agent_name="CustomAgent")
```

- Ensure that `CustomAgent.yaml` exists in the `.agentforge/prompts/` directory.

### Variable Precedence

- **Persona vs. Runtime Variables**: Variables provided at runtime override those found in the persona file.
- **Avoid Conflicts**: To prevent unintended overrides, ensure that variable names in persona files do not conflict with those passed at runtime unless desired.

**Example**:

If both the persona file and runtime arguments provide a value for `topic`, the runtime `topic` value will be used.

### Required Prompts

- **Both `System` and `User` Prompts are Required**: For the agent to function correctly, your prompt file must contain both `System` and `User` sections. Even if one section is minimal, it needs to be present to meet the framework's requirements.

---

## Best Practices for Prompt Design

- **Include Both `System` and `User` Prompts**: Always ensure your prompt files contain both the `System` and `User` sections.
- **Use Valid Variable Names**: Ensure variables are valid Python identifiers.
- **Unique Variable Names**: Avoid naming conflicts between persona data and runtime arguments.
- **Be Mindful of Variable Scope**: Understand where variables come from and how they interact.
- **Test Your Prompts**: Regularly test to ensure variables are correctly replaced and prompts render as expected.
- **Keep Prompts Clear and Concise**: Write prompts that are easy to read and understand.
- **Match Prompt Files with `agent_name`**: Ensure that the prompt file names match the `agent_name` of your agents.

---

## Example: Bringing It All Together

**Prompt File (`KnowledgeAgent.yaml`)**:

```yaml
Prompts:
  System:
    Role: |
      You are {Name}, an expert in {Expertise}.
    Goal: Your goal is to assist users by providing detailed explanations.
  User:
    Question: Please explain the concept of {concept}.
```

**Persona File (`KnowledgeAgent.yaml`)**:

```yaml
Name: Dr. Know
Expertise: Quantum Physics
```

**Usage**:

```python
from agentforge.agent import Agent

# Instantiate the agent with the name matching the prompt and persona files
agent = Agent(agent_name="KnowledgeAgent")
response = agent.run(concept="Quantum Entanglement")
print(response)
```

**Rendered Prompts**:

- **System Prompt**:

  ```
  You are Dr. Know, an expert in Quantum Physics.
  Your goal is to assist users by providing detailed explanations.
  ```

- **User Prompt**:

  ```
  Please explain the concept of Quantum Entanglement.
  ```

---

## Conclusion

By structuring your prompts using `System` and `User` sections with sub-prompts, you gain precise control over how your agents interact with users and LLMs. Leveraging dynamic variables, persona data, and custom `agent_name` allows for rich, context-aware conversations.

---

## Additional Resources

- **Prompt Handling Deep Dive**: For a detailed exploration of how prompts are processed, check out the [Prompt Handling Documentation](../Utils/PromptHandling.md).
- **Custom Agents Guide**: Learn more about creating and customizing agents, including using custom `agent_name`, in the [Custom Agents Guide](CustomAgents.md).
- **Personas**: Understand how to define and use personas in the [Personas Guide](../Personas/Personas.md).

---

**Need Help?**

If you have questions or need assistance, feel free to reach out:

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)

---