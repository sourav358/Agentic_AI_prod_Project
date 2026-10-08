 # Agentic AI Production Project

An Agentic AI assistant built with Python, LangChain and MCP that can understand user instructions, decide which tools are required, and execute real-world tasks instead of only generating text.

## 🚀 What This Project Does

This project demonstrates how an LLM can act as an agent by connecting reasoning with external tools.

Instead of simply answering:

> "How do I create a GitHub repository?"

the agent can understand the request, select the appropriate tool, execute the required actions, and return the result to the user.

## 🏗️ Agent Flow

```text
User Request
     ↓
LLM / Agent
     ↓
Understand the task
     ↓
Select required tool
     ↓
MCP Tool / External Service
     ↓
Execute action
     ↓
Tool Result
     ↓
Agent
     ↓
Final Response
