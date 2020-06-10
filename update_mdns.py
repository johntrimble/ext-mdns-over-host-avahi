from pydbus import SystemBus
import json
import os
import logging

# Configure logging
loglevel = os.getenv('LOG_LEVEL', 'INFO')
numeric_level = getattr(logging, loglevel.upper(), None)
invalid_log_level = False
if not isinstance(numeric_level, int):
    numeric_level = logging.INFO
    raise ValueError('Invalid log level: {}'.format(loglevel))
logging.basicConfig(level=numeric_level)
if invalid_log_level:
    logging.warn('Environment variable LOG_LEVEL set to invalid level %s', loglevel)

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

logging.info('Connecting to system bus DBUS_SYSTEM_BUS_ADDRESS=%s', os.getenv('DBUS_SYSTEM_BUS_ADDRESS'))

# Base avahi object
bus = SystemBus()
avahi = bus.get('org.freedesktop.Avahi', '/')

def get_namespaced_name(resource):
    if resource:
        metadata = resource.get('metadata', {})
        namespace = metadata.get('namespace')
        name = metadata.get('name')
        return '{}/{}'.format(namespace, name)
    else:
        return ''

def update_record(service):
    uid = get_uid(service)
    if not uid:
        # cannot do anything if we don't have a uid
        return
    hostname = get_hostname(service)
    publicip = get_publicip(service)
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
        logging.info('Adding entry resource-namespaced-name=%s hostname=%s publicip=%s',
            get_namespaced_name(service), hostname, publicip)
        entry.AddAddress(-1, # all interfances
                         -1, # no specific protocol
                         0,  # flags
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
            logging.info('Removing entry resource-namespaced-name=%s hostname=%s publicip=%s',
                get_namespaced_name(service), record['hostname'], record['publicip'])
            entry.Free()
            del service_records[uid]

def service_added(service):
    update_record(service)

def service_modified(service):
    update_record(service)

def service_deleted(service):
    delete_record(service)

def process_event(event):
    logging.info('Received event type=%s resource-namespaced-name=%s', 
        event.get('type'), get_namespaced_name(event.get('object')))
    event_funcs = {
        'ADDED': service_added,
        'MODIFIED': service_modified,
        'DELETED': service_deleted
    }

    func = event_funcs.get(event.get('type'))
    if func and event.get('object'):
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
                logging.exception('Could not process event: %s', line)
