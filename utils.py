from io import BytesIO
import numpy as np
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
import onnxruntime
import streamlit as st

# load the model
ort_session = onnxruntime.InferenceSession("chembl_multitask.onnx")


def calc_morgan_fp(smiles):
    mol = Chem.MolFromSmiles(smiles)
    fp = rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, 2, nBits=1024)
    a = np.zeros((0,), dtype=np.float32)
    Chem.DataStructs.ConvertToNumpyArray(fp, a)
    return a


def run_predictions(smiles):
    # calculate the FPs
    descs = calc_morgan_fp(smiles)

    # run the prediction
    ort_inputs = {ort_session.get_inputs()[0].name: descs}
    preds = ort_session.run(None, ort_inputs)
    # example of how the output of the model can be formatted
    preds = np.concatenate(preds).ravel()
    return preds


def generate_file_content(df):
    # Convert DataFrame to CSV
    csv = df.to_csv(index=False)

    # Create BytesIO object to hold the CSV data
    bytes_io = BytesIO()
    bytes_io.write(csv.encode())
    bytes_io.seek(0)  # Move the cursor to the start of the stream

    return bytes_io
