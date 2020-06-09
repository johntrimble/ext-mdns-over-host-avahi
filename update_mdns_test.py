from update_mdns import process_event
import subprocess
import time

def resolve_hostname(hostname):
    result = subprocess.run(["avahi-resolve-host-name", "-4", "-n", hostname], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, input="Hello from the other side")
    if result.returncode != 0 or result.stderr.startswith('Fail'):
        return None
    return result.stdout.rstrip().split()[1]

# Add service with no public ip
process_event({
    "type":"ADDED",
    "object":{
        "metadata":{
            "uid":"cedfd733-0b43-433c-b5dd-844efde8d0f1"
        },
        "status":{"loadBalancer":{}}
    }
})

time.sleep(5)

# Modified service with hostname but no public ip
process_event({
    "type":"MODIFIED",
    "object":{
        "metadata":{
            "uid":"cedfd733-0b43-433c-b5dd-844efde8d0f1",
            "annotations": {
                "mdns.johntrimble.com/hostname": "billybob779.local"
            }
        },
        "status":{"loadBalancer":{}}
    }
})

time.sleep(5)
assert resolve_hostname("billybob779.local") is None

# Modified so we now have an IP address
process_event({
    "type":"MODIFIED",
    "object":{
        "metadata":{
            "uid":"cedfd733-0b43-433c-b5dd-844efde8d0f1",
            "annotations": {
                "mdns.johntrimble.com/hostname": "billybob779.local"
            }
        },
        "status":{"loadBalancer":{"ingress":[{"ip":"192.168.0.199"}]}}
    }
})

time.sleep(5)
assert resolve_hostname("billybob779.local") == "192.168.0.199"

# Change hostname
process_event({
    "type":"MODIFIED",
    "object":{
        "metadata":{
            "uid":"cedfd733-0b43-433c-b5dd-844efde8d0f1",
            "annotations": {
                "mdns.johntrimble.com/hostname": "frank779.local"
            }
        },
        "status":{"loadBalancer":{"ingress":[{"ip":"192.168.0.199"}]}}
    }
})

time.sleep(5)
assert resolve_hostname("billybob779.local") is None
assert resolve_hostname("frank779.local") == "192.168.0.199"

# Change IP address
process_event({
    "type":"MODIFIED",
    "object":{
        "metadata":{
            "uid":"cedfd733-0b43-433c-b5dd-844efde8d0f1",
            "annotations": {
                "mdns.johntrimble.com/hostname": "frank779.local"
            }
        },
        "status":{"loadBalancer":{"ingress":[{"ip":"192.168.0.198"}]}}
    }
})

time.sleep(10)
assert resolve_hostname("frank779.local") == "192.168.0.198"

# Remove service
process_event({
    "type":"DELETED",
    "object":{
        "metadata":{
            "uid":"cedfd733-0b43-433c-b5dd-844efde8d0f1",
            "annotations": {
                "mdns.johntrimble.com/hostname": "frank779.local"
            }
        },
        "status":{"loadBalancer":{"ingress":[{"ip":"192.168.0.198"}]}}
    }
})

time.sleep(5)
assert resolve_hostname("frank779.local") is None
