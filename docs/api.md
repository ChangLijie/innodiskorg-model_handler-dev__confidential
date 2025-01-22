# API Documentation

## Endpoints
- [Get model list](#api-models)
- [Delete model](#api-models-delete)
- [Upload model file](#api-modelsupload-post)
- [Create model to model server (Ollama)](#api-modelscreate-post)

## API: `/models/`

### Description
Returns the list of models available from Innodisk for conversion.

### Success Response
A series of JSON objects will be returned in sequence. Examples:

```json
{
    "status": 200,
    "message": {
        "action": "Get model.",
        "task_uuid": "e3fd235d-5852-4a09-868e-c2baf9be07b6",
        "progress_ratio": 0.5,
        "details": {
            "model": "innodisk_llama32_lora"
        }
    }
}
{
    "status": 200,
    "message": {
        "action": "Get model.",
        "task_uuid": "e3fd235d-5852-4a09-868e-c2baf9be07b6",
        "progress_ratio": 1.0,
        "details": {
            "model": "custom"
        }
    }
}
```

## API: `/models/` (DELETE)

### Description
Deletes a specified model from Innodisk.

### Request Parameters
- **Body** (JSON):
  ```json
  {
      "model": "innodisk_llama3_2_full"
  }
### Success Response
A series of JSON objects will be returned to indicate the status of the deletion. Examples:
```json
{
    "status": 200,
    "message": {
        "action": "Start delete model.",
        "task_uuid": "9078e93a-c3ce-4af9-a5a9-1baac4e76e47",
        "progress_ratio": 0.5,
        "details": {
            "model_name": "innodisk_llama32_lora"
        }
    }
}
{
    "status": 200,
    "message": {
        "action": "Success delete model.",
        "task_uuid": "9078e93a-c3ce-4af9-a5a9-1baac4e76e47",
        "progress_ratio": 1.0,
        "details": {
            "model_name": "innodisk_llama32_lora"
        }
    }
}
```
## API: `/models/upload/` (POST)

### Description
Uploads a model file to the server.

### Request Parameters
- **Body** (Form Data):
  - **Model**: The file to be uploaded.

### Success Response
A series of JSON objects will be returned to indicate the status of the upload process. Examples:

```json
{
    "status": 200,
    "message": {
        "action": "Started save model.",
        "task_uuid": "603de8f5-c4e1-416a-ac31-91dc33de50af",
        "progress_ratio": 0,
        "details": {
            "model": "innodisk_llama32_lora.zip"
        }
    }
}
{
    "status": 200,
    "message": {
        "action": "Start extracted model.",
        "task_uuid": "603de8f5-c4e1-416a-ac31-91dc33de50af",
        "progress_ratio": 0.66,
        "details": {
            "model": "innodisk_llama32_lora.zip"
        }
    }
}
{
    "status": 200,
    "message": {
        "action": "Success upload model file.",
        "task_uuid": "603de8f5-c4e1-416a-ac31-91dc33de50af",
        "progress_ratio": 1.0,
        "details": {
            "model": "innodisk_llama32_lora.zip"
        }
    }
}
```
## API: `/models/create/` (POST)

### Description
Creates a model on the Model Server (Ollama).

### Request Parameters
- **Body** (JSON):
  ```json
  {
      "model": "innodisk_llama3_2_lora",
      "model_name_on_ollama": "test"
  }
### Success Response
A series of JSON objects will be returned to indicate the status of the model creation process. Examples:
```json
{
    "status": 200,
    "message": {
        "action": "Started to create model.",
        "task_uuid": "2895c005-fbd3-4402-9752-bc804c509b10",
        "progress_ratio": 0.33,
        "details": {
            "model": "innodisk_llama32_lora"
        }
    }
}
{
    "status": 200,
    "message": {
        "action": "Start structure template",
        "task_uuid": "2895c005-fbd3-4402-9752-bc804c509b10",
        "progress_ratio": 0.66,
        "details": {
            "model": "innodisk_llama32_lora"
        }
    }
}
{
    "status": 200,
    "message": {
        "action": "Success create model",
        "task_uuid": "2895c005-fbd3-4402-9752-bc804c509b10",
        "progress_ratio": 1.0,
        "details": {
            "model": "innodisk_llama32_lora",
            "model_name_on_ollama": "test1"
        }
    }
}
```
## API: `/models/deploy/` (POST)

### Description
Upload and creates a model on the Model Server (Ollama).

### Request Parameters
- **Body** (Form Data):
  - **Model**: The file to be uploaded.
  - **model_name_on_ollama**: The model name on the ollama.
### Success Response
A series of JSON objects will be returned to indicate the status of the model creation process. Examples:
```json
{
    "status": 200,
    "message": {
        "action": "Start save model.",
        "task_uuid": "089350f3-d2cd-4ecd-838a-51cf93d4d9ec",
        "progress": 0.0,
        "details": {
            "model": "innodisk_llama32_lora.zip"
        }
    }
}
{
    "status": 200,
    "message": {
        "action": "Start extract model.",
        "task_uuid": "089350f3-d2cd-4ecd-838a-51cf93d4d9ec",
        "progress": 0.33,
        "details": {
            "model": "innodisk_llama32_lora.zip"
        }
    }
}
{
    "status": 200,
    "message": {
        "action": "Success upload model file.",
        "task_uuid": "089350f3-d2cd-4ecd-838a-51cf93d4d9ec",
        "progress": 0.5,
        "details": {
            "model": "innodisk_llama32_lora.zip"
        }
    }
}
{
    "status": 200,
    "message": {
        "action": "Start create model.",
        "task_uuid": "089350f3-d2cd-4ecd-838a-51cf93d4d9ec",
        "progress": 0.67,
        "details": {
            "model": "innodisk_llama32_lora"
        }
    }
}
{
    "status": 200,
    "message": {
        "action": "Start structure template",
        "task_uuid": "089350f3-d2cd-4ecd-838a-51cf93d4d9ec",
        "progress": 0.83,
        "details": {
            "model": "innodisk_llama32_lora"
        }
    }
}
{
    "status": 200,
    "message": {
        "action": "Success create model",
        "task_uuid": "089350f3-d2cd-4ecd-838a-51cf93d4d9ec",
        "progress": 1.0,
        "details": {
            "model": "innodisk_llama32_lora",
            "model_name_on_ollama": "test"
        }
    }
}
```