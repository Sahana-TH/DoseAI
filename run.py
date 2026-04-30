# run.py — Entry point to start the Flask server
# Run this with: python run.py

from app import create_app

app = create_app()

if __name__ == "__main__":
    print("🚀 DoseAI Backend starting...")
    print("📡 Server running at: http://localhost:5000")
    print("🔍 Test it: http://localhost:5000/medicine/ibuprofen")
    print("Press CTRL+C to stop.\n")
    
    app.run(
        debug=True,   # Auto-reloads when you save code changes
        port=5000,
        host="0.0.0.0"
    )