import sys
import requests

def send_command(server: str, device_id: str, command: dict):
    url = f"{server.rstrip('/')}/devices/{device_id}/commands"
    r = requests.post(url, json=command)
    r.raise_for_status()
    print(r.json())


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python send_command.py <server> <device_id> <json_command>")
        print('Example: python send_command.py http://localhost:8000 my-device "{\"action\": \"ping\"}"')
        sys.exit(1)
    server = sys.argv[1]
    device_id = sys.argv[2]
    import json
    command = json.loads(sys.argv[3])
    send_command(server, device_id, command)
