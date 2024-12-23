# API Documentation

## Endpoints
- [Get model list](#api-models)
- [Delete model](#api-models-delete)
- [Upload model file](#api-modelsupload-post)
- [Create model to model server (Ollama)](#api-modelscreate-post)

## API: `/models`

### Description
Returns the list of models available from Innodisk for conversion.

### Success Response
A series of JSON objects will be returned in sequence. Examples:

```json
{
    "status": "success",
    "message": {
        "model": "innodisk_llama3"
    }
}
{
    "status": "success",
    "message": {
        "model": "innodisk_llama3_1"
    }
}
{
    "status": "success",
    "message": {
        "model": "innodisk_llama3_lora"
    }
}
{
    "status": "success",
    "message": {
        "model": "innodisk_llama3_1_lora"
    }
}
{
    "status": "success",
    "message": {
        "model": "innodisk_llama3_2_full"
    }
}
{
    "status": "success",
    "message": {
        "end": true
    }
}
```

## API: `/models` (DELETE)

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
    "status": "success",
    "message": "Start Delete Model innodisk_llama3_2_full"
}
{
    "status": "success",
    "message": "Delete Model innodisk_llama3_2_full success."
}
{
    "status": "success",
    "message": {
        "end": true
    }
}
```
## API: `/models/upload` (POST)

### Description
Uploads a model file to the server.

### Request Parameters
- **Body** (Form Data):
  - **Model**: The file to be uploaded.

### Success Response
A series of JSON objects will be returned to indicate the status of the upload process. Examples:

```json
{
    "status": "success",
    "message": "Save 'innodisk_llama3_2_lora.zip' success."
}
{
    "status": "success",
    "message": "Model extracted successfully."
}
{
    "status": "success",
    "message": {
        "end": true
    }
}
```
## API: `/models/create` (POST)

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
    "status": "success",
    "message": "Get model process status from ollama.",
    "details": "{\"status\":\"using existing layer sha256:a574146212de8143c7c2edb75d35981488ae859a064cf75441de9011b711c244\"}"
}
{
    "status": "success",
    "message": "Get model process status from ollama.",
    "details": "{\"status\":\"using existing layer sha256:30d7f588ec81ba8717196a8ed05407ee402d76891e855a9c1a4b2a1b094b4ae8\"}"
}
{
    "status": "success",
    "message": "Get model process status from ollama.",
    "details": "{\"status\":\"writing manifest\"}"
}
{
    "status": "success",
    "message": "Get model process status from ollama.",
    "details": "{\"status\":\"success\"}"
}
{
    "status": "success",
    "message": {
        "end": true
    }
}
```