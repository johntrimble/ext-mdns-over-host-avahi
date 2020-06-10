# ext-mdns-over-host-avahi

ext-mdns-over-host-avahi provides external Multicast DNS hostnames names to Kubernetes Services by leveraging the hosts avahi-daemon.

## Summary

ext-mdns-over-host-avahi is targeted towards bare-metal Kubernetes clusters providing services on a home network (e.g. MicroK8s on a Raspberry Pi). 

Services can be given an mDNS hostname by adding a `mdns.johntrimble.com/hostname` annotation to services of `type=LoadBalancer`. ext-mdns-over-host-avahi monitors services with this annotation and uses D-Bus to connect to the host's avahi-daemon to add appropriate address/hostname mappings making the hostnames resolvable on the local area network.

## Prerequisites 

- avahi-daemon installed on kubernetes nodes
- update any relevant AppArmor policies to allow access to D-Bus (I had to add 'dbus' to /etc/apparmor.d/cri-containerd.apparmor.d for MicroK8s)
- a load balancer such as [MetalLB](https://metallb.universe.tf/)

## Quickstart

Install ext-mdns-over-host-avahi with:

```
microk8s kubectl apply -f https://raw.githubusercontent.com/johntrimble/ext-mdns-over-host-avahi/master/deployment.yaml
```

To test it, make an nginx deployment by putting the following in a file named `example-deployment.yaml`:

```
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: my-nginx
  name: my-nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: my-nginx
  template:
    metadata:
      labels:
        app: my-nginx
    spec:
      containers:
      - image: nginx
        name: nginx
```

Now apply it:

```
kubectl apply -f example-deployment.yaml
```

This will deploy nginx, but it will only be accessible withing the kubernetes cluster. To expose it on the network with an mDNS hostname, create a service like the following and save it to a file named `example-service.yaml`:

```
apiVersion: v1
kind: Service
metadata:
  annotations:
    mdns.johntrimble.com/hostname: foo.local
  labels:
    app: my-nginx
  name: my-nginx
spec:
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  selector:
    app: my-nginx
  type: LoadBalancer
```

Now apply it:

```
kubectl apply -f example-service.yaml
```

You should now be able to access the nginx welcome page by using the URL [http://foo.local](http://foo.local).
