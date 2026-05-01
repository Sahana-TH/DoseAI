import sys
import os

from app.scanner import extract_medicine_candidates

sample_texts = [
    "DOLO 650\nBatch No: 12345\nExp: 12/2025\nParacetamol Tablets IP",
    "Crocin Advance\nFast Relief\n500 mg",
    "Rx\nAmoxicillin and Potassium Clavulanate Tablets IP\nAugmentin 625 Duo\nGlaxoSmithKline",
    "Paracetamol, Phenylephrine Hydrochloride & Cetirizine Hydrochloride Tablets\nSinarest",
    "Allegra 120 mg\nSanofi",
    "Mfg. Lic. No.: MNB/16/970\nAzithromycin Tablets IP 500 mg\nAzithral 500\nAlembic",
    "Combiflam\nIbuprofen & Paracetamol Tablets",
    "Pantoprazole Gastro-resistant Tablets IP 40 mg\nPan 40\nAlkem",
]

print("Testing extract_medicine_candidates:")
print("-" * 50)
for text in sample_texts:
    candidates = extract_medicine_candidates(text)
    print(f"RAW TEXT:\n{text}")
    print(f"CANDIDATES: {candidates}")
    print("-" * 50)
