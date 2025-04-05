
# Streamlit Video Processing Application with Ollama and Open-Source Models

This repository contains a Streamlit application designed to process video files by extracting frames, analyzing them using the `gemma3:12b` model via [Ollama](https://ollama.com/), and generating comprehensive summaries. The application leverages Apache Kafka for efficient data handling and communication between components.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Use Cases](#use-cases)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Setting Up Apache Kafka](#setting-up-apache-kafka)
  - [Running the Application](#running-the-application)
- [Configuration](#configuration)
- [Acknowledgments](#acknowledgments)

## Overview

The application provides a user-friendly interface for uploading video files, processing them to extract frames at specified intervals, and analyzing these frames using the `gemma3:12b` model—a powerful open-source large language model (LLM). By integrating [Ollama](https://ollama.com/), the application can run LLMs locally, ensuring data privacy and reducing latency.

## Features

- **Video Upload:** Users can upload video files through the Streamlit interface.
- **Frame Extraction:** The application extracts frames from the video at specified intervals.
- **Batch Processing:** Frames are processed in batches to optimize performance.
- **AI Analysis:** Utilizes the `gemma3:12b` model via Ollama to analyze frames and generate summaries.
- **Kafka Integration:** Employs Apache Kafka for efficient data streaming and processing.

## Use Cases

The application can be utilized in various scenarios, including but not limited to:

- **Content Analysis:** Summarizing video content for quick insights.
- **Security Monitoring:** Analyzing surveillance footage to detect notable events.
- **Educational Purposes:** Extracting and summarizing key moments from lecture recordings.
- **Media Archiving:** Generating metadata for video archives to enhance searchability.

## Installation

### Prerequisites

Ensure that the following dependencies are installed:

- [Python 3.x](https://www.python.org/downloads/)
- [Streamlit](https://streamlit.io/)
- [Ollama](https://ollama.com/)
- [Apache Kafka](https://kafka.apache.org/)

### Setting Up Apache Kafka

1. **Install Kafka:**

   On macOS, you can install Kafka using Homebrew:

   ```bash
   brew install kafka
   ```

2. **Start Zookeeper:**

   Kafka requires Zookeeper to manage its cluster state. Start Zookeeper with the following command:

   ```bash
   /usr/local/bin/zookeeper-server-start /usr/local/etc/zookeeper/zoo.cfg
   ```

3. **Start Apache Kafka:**

   Once Zookeeper is running, start the Kafka server:

   ```bash
   /usr/local/bin/kafka-server-start /usr/local/etc/kafka/server.properties
   ```

### Running the Application

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/streamlit-video-processor.git
   cd streamlit-video-processor
   ```

2. **Install Python Dependencies:**

   Use `pip` to install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the Application:**

   Update the `config.yaml` file with your desired settings. Refer to the [Configuration](#configuration) section for details.

4. **Run the Streamlit Application:**

   Start the application with:

   ```bash
   streamlit run app.py
   ```

   Access the application in your web browser at `http://localhost:8501`.

## Configuration

The application uses a `config.yaml` file for configuration settings. Below is an example of the configuration parameters:

```yaml
KAFKA_TOPIC: "video-frames"
BOOTSTRAP_SERVERS: "localhost:9092"
FRAME_INTERVAL: 30
BATCH_SIZE: 10
RESIZED_WIDTH: 640
RESIZED_HEIGHT: 480
MODEL: "gemma3:12b"
PROMPT: "Describe the following sequence of images extracted from a video and provide a comprehensive summary of the video's content, including observed objects, people, actions, and any notable events."
```

## Acknowledgments

This application integrates [Ollama](https://ollama.com/), an open-source tool that simplifies running large language models locally. By leveraging models like `gemma3:12b`, the application demonstrates the potential of open-source AI in processing and analyzing video content efficiently.

For more information on Ollama and available models, visit the [Ollama Library](https://ollama.com/library).
