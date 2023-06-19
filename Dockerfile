# Use the official Python image as the base image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download the onnx model file
RUN curl -LJ https://github.com/chembl/chembl_multitask_model/raw/main/trained_models/chembl_33_model/chembl_33_multitask_q8.onnx -o /app/chembl_multitask.onnx

RUN curl -LJ https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_33/chembl_33.h5 -o /app/fpsim2_file.h5

# Copy the Streamlit app files into the container
COPY pages/ pages/
COPY Home_page.py .
COPY utils.py .
COPY similarity_utils.py .
COPY heatmap.py .
COPY docs.csv .


# Expose the port that Streamlit runs on (default is 8501)
EXPOSE 8501

# Set the command to run the Streamlit app
CMD ["streamlit", "run", "Home_page.py"]
