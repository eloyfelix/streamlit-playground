from FPSim2 import FPSim2Engine

fpe = FPSim2Engine("fpsim2_file.h5")

def similarity_search(smiles, threshold=0.7):
    results = fpe.similarity(smiles, threshold, n_workers=2)
    return results
