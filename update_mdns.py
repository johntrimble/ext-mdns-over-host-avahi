from pydbus import SystemBus
import json

# Instructive resources:
# https://github.com/flix-tech/k8s-mdns
# https://github.com/balena-io-playground/balena-avahi-dbus

service_records = {}

def get_hostname(service):
    return service.get('metadata', {}).get('annotations', {}).get('mdns.johntrimble.com/hostname', None)

def get_publicip(service):
    ingresses = service.get('status', {}).get('loadBalancer', {}).get('ingress', [])
    for ingress in ingresses:
        # technically, we could find multiple IP addresses here, but avahi
        # will throw a fit if we attempt to map multiple IP addresses to the
        # same hostname
        ip = ingress.get('ip')
        if ip:
            return ip

def get_uid(service):
    return service.get('metadata', {}).get('uid')

# Base avahi object
bus = SystemBus()
avahi = bus.get('org.freedesktop.Avahi', '/')

def update_record(service):
    uid = get_uid(service)
    print(uid, "update record")
    if not uid:
        # cannot do anything if we don't have a uid
        return
    hostname = get_hostname(service)
    publicip = get_publicip(service)
    print(uid, "hostname", hostname, "publicip", publicip)
    record = service_records.get(uid)
    if record:
        if hostname != record.get('hostname') or publicip != record.get('publicip'):
            delete_record(service)
        else:
            # we have a record already and it is up-to-date
            return

    if hostname and publicip:
        entry_path = avahi.EntryGroupNew()
        entry = bus.get('org.freedesktop.Avahi', entry_path)
        print(uid, "Adding address", publicip, hostname)
        entry.AddAddress(-1, # all interfances
                         -1, # no specific protocol
                         0, # flags
                         hostname,
                         publicip)
        entry.Commit()
        service_records[uid] = {
            'hostname': hostname,
            'publicip': publicip,
            'entrygroup': entry
        }

def delete_record(service):
    uid = get_uid(service)
    if not uid:
        # cannot do anything if we don't have a uid
        return
    record = service_records.get(uid)
    if record:
        entry = record.get('entrygroup')
        if entry:
            print(uid, "Removing address")
            entry.Free()
            del service_records[uid]

def service_added(service):
    update_record(service)

def service_modified(service):
    update_record(service)

def service_deleted(service):
    delete_record(service)

def process_event(event):
    event_funcs = {
        'ADDED': service_added,
        'MODIFIED': service_modified,
        'DELETED': service_deleted
    }

    func = event_funcs.get(event.get('type'))
    if func and event.get('object'):
        print("processing event", json.dumps(event))
        func(event.get('object'))

if __name__ == '__main__':
    import fileinput

    for line in fileinput.input():
        line = line.rstrip()
        if line:
            try:
                event = json.loads(line)
                process_event(event)
            except:
                # error processing this event
                pass
