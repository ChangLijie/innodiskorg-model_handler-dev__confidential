# Model Handler

Model Handler is a project designed to provide an interface for uploading custom model files **(Note: Custom models must be in GGUF format.)** and deploying them to the Ollama Model Server.

## Purpose

The primary goal of Model Handler is to create an efficient workflow for managing models by:

* Providing an API to upload custom model files.**(Note: Custom models must be in GGUF format.)**

* Deploying uploaded models to Ollama.

## Features

* Upload Models: Upload custom model files to the server.**(Note: Custom model must be in GGUF format.)**

* Deploy to Ollama: Deploy the uploaded models to the Ollama Model Server for use.

* Manage Models: Perform operations such as listing available models, deleting models, and managing model metadata.

## API Endpoints
See more api information from [API Documents](./docs/api.md)

## Getting Started
### Prerequisites
* You must first create a models folder. Inside the models folder, there should be two subdirectories: inno and ollama.
    ```
    models/
    ├── inno/
    └── ollama/
    ```
* A running instance of Ollama Model Server [(How to Run Ollama)](https://github.com/ollama/ollama). When starting the Ollama server, ensure the models folder is mounted properly:

    - ./models/ollama:/root/.ollama

    - ./models/inno:/home   

### Installation
Run Docker:
   ```bash
   docker run -it --rm -p 5000:5000 \
      -v ${model folder path}:/workspace/models \
      -e MODEL_SERVER_IP=${Ollama IP} \
      -e MODEL_SERVER_PORT=${Ollama Port} \
      --name test_model_handler \
      innodiskorg/model_handler:latest
   ```
   **Notes:**
   - **model folder path**: The directory path where your models will be stored. *(The models folder you created earlier, which contains the inno and ollama subdirectories.)*
   - **Ollama IP**: The IP address of the Ollama Model Server.
   - **Ollama Port**: The port number of the Ollama Model Server.


   