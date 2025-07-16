# Viral AI Video Generation Platform - Architecture Overview

This document provides a high-level overview of the architecture of the Viral AI Video Generation Platform.

## 1. Core Principles

The platform is designed around a **modular, agent-based architecture**. The core principle is to break down the complex process of video generation into a series of smaller, manageable tasks, each handled by a specialized "agent". This approach promotes:

*   **Scalability**: New features or video generation techniques can be added by creating new agents without disrupting the existing workflow.
*   **Maintainability**: Each agent has a specific responsibility, making the code easier to understand, debug, and maintain.
*   **Flexibility**: The orchestration of agents can be easily modified to create different types of videos or experiment with new workflows.

The project follows the principles of **Clean Architecture**, separating the core business logic from the infrastructure and UI layers. This is evident in the `src/core` and `src/infrastructure` directory structures.

## 2. High-Level Architecture

The platform can be broadly divided into four main layers:

1.  **Orchestration Layer**: This layer is responsible for managing the overall video generation process. It coordinates the various agents, passing data between them and ensuring that the final video is assembled correctly. The `working_orchestrator` is the central component of this layer.
2.  **Agent Layer**: This layer contains the specialized agents that perform the individual tasks of video generation, such as scriptwriting, image selection, video composition, and voice generation.
3.  **Generation Layer**: This layer contains the clients and services that interact with external AI models and services, such as Google's Vertex AI (for VEO and Imagen) and text-to-speech services.
4.  **Core Layer**: This layer defines the core business logic and entities of the application, such as the `Video`, `Session`, and `Agent` entities, as well as the interfaces for repositories and services.

## 3. Directory Structure Overview

The project's directory structure reflects the architecture described above:

*   `src/`: This is the main source code directory.
    *   `agents/`: Contains the specialized agents responsible for different tasks in the video generation pipeline.
    *   `generators/`: Contains the clients for interacting with external AI models (e.g., `VertexAIVeo2Client`).
    *   `core/`: Defines the core business logic, entities, and interfaces.
    *   `infrastructure/`: Implements the interfaces defined in the core layer, providing concrete implementations for repositories and services.
    *   `workflows/`: Contains the high-level workflows that orchestrate the agents to generate a video.
    *   `utils/`: Contains utility functions and classes used throughout the application.
*   `tests/`: Contains the unit, integration, and end-to-end tests for the application.
*   `config/`: Contains configuration files for various aspects of the application.
*   `docs/`: Contains project documentation.
*   `scripts/`: Contains utility scripts for various tasks.
*   `outputs/`: The default directory for generated videos and other artifacts.

## 4. Data Flow

A typical video generation workflow involves the following steps:

1.  A user initiates a video generation request through the `main.py` script, providing a prompt and other parameters.
2.  The `working_orchestrator` creates a new session and begins the multi-agent discussion process to brainstorm and refine the video concept.
3.  The `DirectorAgent` creates a script based on the discussion.
4.  The `VideoGenerator` agent uses the script to generate the video, coordinating with other agents like the `SoundmanAgent` and `VisualStyleAgent`.
5.  The `VideoGenerator` uses clients in the `generators/` directory to interact with external AI services to generate video clips, images, and audio.
6.  The `EditorAgent` assembles the final video, adding overlays, subtitles, and other effects.
7.  The final video is saved to the `outputs/` directory. 