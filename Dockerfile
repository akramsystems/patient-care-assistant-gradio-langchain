FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
EXPOSE 7860
EXPOSE 5000
ENV GRADIO_SERVER_NAME="0.0.0.0"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .
