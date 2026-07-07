import time
import uuid
import subprocess
import requests
import sys

def main():
    print("==================================================")
    print("MSME Risk Intelligence API - Integration Test")
    print("==================================================")

    # 1. Start FastAPI server using uvicorn in a background process
    print("\n[1/5] Starting FastAPI server...")
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "apps.main:app", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give the server a few seconds to start up
    time.sleep(3)
    
    # Check if the process died early
    if server_process.poll() is not None:
        print("ERROR: FastAPI server failed to start. Logs:")
        out, err = server_process.communicate()
        print(out)
        print(err)
        sys.exit(1)
        
    print("FastAPI server started successfully on port 8000.")

    # Base URL for API requests
    base_url = "http://127.0.0.1:8000"
    
    # Set headers with dev-bypass role authorization
    headers = {
        "Authorization": "Bearer risk_engineer_token"
    }

    try:
        # 2. Test root endpoint
        print("\n[2/5] Testing Root Endpoint...")
        r = requests.get(f"{base_url}/")
        print(f"Status: {r.status_code}, Response: {r.json()}")
        assert r.status_code == 200

        # 3. Test Macro Risk Evaluation Endpoint
        print("\n[3/5] Testing Macro Risk Evaluation...")
        loan_app_id = str(uuid.uuid4())
        macro_payload = {
            "loan_application_id": loan_app_id,
            "loan_amount": 5000000.0,
            "loan_type": "SME",
            "industry": "Manufacturing",
            "location": "Delhi",
            "employment_sector": "Private"
        }
        r = requests.post(f"{base_url}/api/macro-risk/", json=macro_payload, headers=headers)
        print(f"Status: {r.status_code}")
        macro_result = r.json()
        print("Response payload:")
        for k, v in macro_result.items():
            print(f"  {k}: {v}")
        assert r.status_code == 200
        assert "macro_risk_score" in macro_result
        assert macro_result["loan_application_id"] == loan_app_id

        # 4. Test Document Risk Evaluation Endpoint (Async)
        print("\n[4/5] Testing Document Risk Upload (Async)...")
        # Create some dummy files in memory
        files = [
            ("documents", ("pan_card.jpg", b"fake image bytes representing PAN card", "image/jpeg")),
            ("documents", ("salary_slip.pdf", b"fake PDF bytes representing salary slip net salary 85000", "application/pdf")),
        ]
        
        # We pass loan_application_id as a query parameter
        r = requests.post(
            f"{base_url}/api/document-risk/?loan_application_id={loan_app_id}",
            files=files,
            headers=headers
        )
        print(f"Status: {r.status_code}")
        doc_response = r.json()
        print(f"Response: {doc_response}")
        assert r.status_code == 200
        assert "task_id" in doc_response
        
        task_id = doc_response["task_id"]

        # 5. Poll Document Risk Result Endpoint
        print("\n[5/5] Polling Document Risk Result...")
        completed = False
        attempts = 0
        max_attempts = 10
        
        while not completed and attempts < max_attempts:
            attempts += 1
            print(f"Polling attempt {attempts}/{max_attempts}...")
            r = requests.get(f"{base_url}/api/document-risk/{task_id}", headers=headers)
            
            if r.status_code == 200:
                result = r.json()
                print("\nSuccess! Document risk analysis complete.")
                print("Result details:")
                for k, v in result.items():
                    print(f"  {k}: {v}")
                completed = True
                break
            elif r.status_code == 202:
                print("Still processing, waiting 2 seconds...")
                time.sleep(2)
            else:
                print(f"Unexpected status: {r.status_code}, detail: {r.text}")
                break
                
        assert completed, "Document risk processing task failed or timed out."
        print("\n==================================================")
        print("ALL TESTS PASSED SUCCESSFULLY!")
        print("==================================================")

    except Exception as e:
        print(f"\nTest failed with exception: {e}")
        # Retrieve server logs
        print("Server process poll status:", server_process.poll())
        sys.exit(1)
        
    finally:
        print("\nStopping FastAPI server...")
        server_process.terminate()
        server_process.wait()
        print("Server stopped.")

if __name__ == "__main__":
    main()
