FROM python:3.10-slim

# Set the working directory
WORKDIR /workspace
COPY ./requirements.txt /workspace/
COPY ./src /workspace/

# Install the dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "app.py"]