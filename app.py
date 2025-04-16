# app.py
from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# Define service enum
class ServiceProvider:
    VAPI = "vapi"
    RETELL = "retell"

# Service client class
class AgentServiceClient:
    def __init__(self):
        # Replace with your real API keys before running
        self.vapi_api_key = 'your-api-key'
        self.retell_api_key = 'your-api-key'
    
    def create_agent(self, service, data):
        if service == ServiceProvider.VAPI:
            return self._create_vapi_agent(data)
        elif service == ServiceProvider.RETELL:
            return self._create_retell_agent(data)
        else:
            raise ValueError(f"Unsupported service: {service}")
    
    def _create_vapi_agent(self, data):
        vapi_data = self._transform_to_vapi_format(data)
        
        print(f"Calling Vapi API with URL: https://api.vapi.ai/v1/assistants")
        print(f"Headers: {{'Authorization': 'Bearer your-api-key'}}")
        print(f"Request body: {json.dumps(vapi_data, indent=2)}")
        
        response = requests.post(
            "https://api.vapi.ai/v1/assistants",
            json=vapi_data,
            headers={"Authorization": f"Bearer {self.vapi_api_key}"}
        )
        
        print(f"Response status code: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code in [200, 201]:
            try:
                return {"service": "vapi", "agent_id": response.json().get("assistant_id"), "details": response.json()}
            except json.JSONDecodeError:
                return {"error": True, "service": "vapi", "status_code": response.status_code, 
                        "message": "Could not parse JSON response", "raw_response": response.text}
        else:
            return {"error": True, "service": "vapi", "status_code": response.status_code, "message": response.text}
    
    def _create_retell_agent(self, data):
        retell_data = self._transform_to_retell_format(data)
        
        print(f"Calling Retell API with URL: https://api.retellai.com/v1/agents")
        print(f"Headers: {{'Authorization': 'Bearer your-api-key'}}")
        print(f"Request body: {json.dumps(retell_data, indent=2)}")
        
        response = requests.post(
            "https://api.retellai.com/v1/agents",
            json=retell_data,
            headers={"Authorization": f"Bearer {self.retell_api_key}"}
        )
        
        print(f"Response status code: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code in [200, 201]:
            try:
                return {"service": "retell", "agent_id": response.json().get("id"), "details": response.json()}
            except json.JSONDecodeError:
                return {"error": True, "service": "retell", "status_code": response.status_code, 
                        "message": "Could not parse JSON response", "raw_response": response.text}
        else:
            return {"error": True, "service": "retell", "status_code": response.status_code, "message": response.text}
    
    def _transform_to_vapi_format(self, data):
        return {
            "name": data.get("name"),
            "model": {
                "provider": data.get("model", {}).get("provider", "openai"),
                "name": data.get("model", {}).get("model_name", "gpt-4"),
                "temperature": data.get("model", {}).get("temperature", 0.7),
                "max_tokens": data.get("model", {}).get("max_tokens")
            },
            "voice_id": data.get("voice", {}).get("voice_id"),
            "first_message": data.get("first_message"),
            "description": data.get("description"),
            "instructions": data.get("instructions"),
            "metadata": data.get("metadata", {}),
            "webhooks": data.get("webhooks", {})
        }
    
    def _transform_to_retell_format(self, data):
        return {
            "name": data.get("name"),
            "llm": {
                "provider": data.get("model", {}).get("provider", "openai"),
                "model": data.get("model", {}).get("model_name", "gpt-4"),
                "temperature": data.get("model", {}).get("temperature", 0.7)
            },
            "voice": {
                "voice_id": data.get("voice", {}).get("voice_id"),
                "language_code": data.get("voice", {}).get("language_code"),
                "speed": data.get("voice", {}).get("voice_speed", 1.0)
            },
            "system_prompt": data.get("instructions", ""),
            "initial_message": data.get("first_message"),
            "description": data.get("description", ""),
            "metadata": data.get("metadata", {}),
            "webhook_url": data.get("webhooks", {}).get("callback")
        }

service_client = AgentServiceClient()

@app.route('/api/create-agent', methods=['POST'])
def create_agent():
    data = request.json
    
    print(f"Received request: {json.dumps(data, indent=2)}")
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    if "service" not in data:
        return jsonify({"error": "Service parameter is required"}), 400
    if "name" not in data:
        return jsonify({"error": "Name parameter is required"}), 400
    if "voice" not in data or "voice_id" not in data["voice"]:
        return jsonify({"error": "Voice ID is required"}), 400
    
    service = data.get("service").lower()
    
    try:
        if service == ServiceProvider.VAPI:
            result = service_client.create_agent(ServiceProvider.VAPI, data)
        elif service == ServiceProvider.RETELL:
            result = service_client.create_agent(ServiceProvider.RETELL, data)
        else:
            return jsonify({"error": f"Unsupported service: {service}"}), 400
        
        if result.get("error"):
            return jsonify(result), 500
        
        return jsonify(result), 200
        
    except Exception as e:
        import traceback
        print(f"Exception: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
