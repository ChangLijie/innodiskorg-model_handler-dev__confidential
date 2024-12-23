FROM python:3.10-slim

# Set the working directory
WORKDIR /workspace
COPY ./app.py /workspace/
COPY ./requirements.txt /workspace/
COPY ./models /workspace/models/
COPY ./routers /workspace/routers/
COPY ./schema /workspace/schema/
COPY ./tools /workspace/tools/
COPY ./utils /workspace/utils/

# Install the dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "app.py"]