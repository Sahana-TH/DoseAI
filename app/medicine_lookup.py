# medicine_lookup.py
# This module is responsible for fetching medicine information
# from the OpenFDA API and returning it in a clean format.

import requests  # For making HTTP requests to external APIs

# The base URL for the OpenFDA drug label endpoint
OPENFDA_BASE_URL = "https://api.fda.gov/drug/label.json"

def fetch_medicine_info(medicine_name: str) -> dict:
    """
    Fetches medicine information from the OpenFDA API.
    
    Args:
        medicine_name (str): The name of the medicine (e.g., "paracetamol")
    
    Returns:
        dict: A structured dictionary with medicine details,
              or an error message if not found.
    """
    
    # Build the search query — we search by brand name OR generic name
    params = {
        "search": f'openfda.brand_name:"{medicine_name}" OR openfda.generic_name:"{medicine_name}"',
        "limit": 1  # We only need the first (best) result
    }
    
    try:
        # Make the GET request to OpenFDA
        response = requests.get(OPENFDA_BASE_URL, params=params, timeout=10)
        
        # Check if request was successful (status code 200 = OK)
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        
        # Check if any results were found
        if not data.get("results"):
            return {"error": f"No information found for '{medicine_name}'"}
        
        # Extract the first result
        result = data["results"][0]
        
        # Build a clean, structured response
        # We use .get() with a default so it doesn't crash if a field is missing
        medicine_info = {
            "name": medicine_name.title(),
            
            # Usage / What it's for
            "usage": result.get("indications_and_usage", ["Information not available"])[0],
            
            # How much to take and when
            "dosage": result.get("dosage_and_administration", ["Information not available"])[0],
            
            # Side effects
            "side_effects": result.get("adverse_reactions", ["Information not available"])[0],
            
            # What happens if too much is taken
            "overdose": result.get("overdosage", ["Information not available"])[0],
            
            # Warnings
            "warnings": result.get("warnings", ["Information not available"])[0],
        }
        
        return medicine_info
    
    except requests.exceptions.ConnectionError:
        return {"error": "No internet connection. Please check your network."}
    
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. OpenFDA may be slow. Try again."}
    
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            return {"error": f"Medicine '{medicine_name}' not found in OpenFDA database."}
        return {"error": f"API error occurred: {str(e)}"}
    
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def pretty_print_medicine(info: dict):
    """
    Prints medicine info to console in a readable format.
    Useful for testing.
    """
    if "error" in info:
        print(f"\n❌ Error: {info['error']}")
        return
    
    print("\n" + "="*60)
    print(f"💊 MEDICINE: {info['name']}")
    print("="*60)
    print(f"\n📋 USAGE:\n{info['usage'][:300]}...")  # First 300 chars
    print(f"\n💉 DOSAGE:\n{info['dosage'][:300]}...")
    print(f"\n⚠️  SIDE EFFECTS:\n{info['side_effects'][:300]}...")
    print(f"\n🚨 OVERDOSE RISK:\n{info['overdose'][:300]}...")
    print("\n" + "="*60)


# ── TEST BLOCK ──────────────────────────────────────────────
# This only runs when you execute this file directly:
# python app/medicine_lookup.py
if __name__ == "__main__":
    print("Testing DoseAI medicine lookup...")
    
    # Test with a common medicine
    result = fetch_medicine_info("metformin")
    pretty_print_medicine(result)