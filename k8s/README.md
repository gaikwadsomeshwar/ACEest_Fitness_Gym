# Kubernetes Deployment Strategies

This directory contains Kubernetes manifests for several deployment strategies.

## Core Resources

- `deployment.yaml` - Standard deployment with rolling update strategy.
- `service.yaml` - NodePort service exposing port 5000.

## Advanced Deployment Patterns

- `blue-green.yaml` - Two deployments (`blue` and `green`) plus a service that can be switched to route traffic.
- `canary.yaml` - Primary and canary deployments. Canary traffic can be controlled by service selectors or ingress routing.
- `rolling-update.yaml` - Explicit rolling update deployment strategy.
- `shadow-deployment.yaml` - Shadow deployment plus a separate shadow service for non-production traffic.
- `ab-testing.yaml` - Two variant deployments for A/B testing experiments.

## Local Deployment Example

Apply the core resources locally with Minikube or any Kubernetes cluster:

```bash
kubectl apply -f k8s/deployment.yaml -f k8s/service.yaml
```

## Switch Traffic for Blue/Green

Apply both blue and green deployments, then point the service selector to the active release.

## Canary Deployment

Start with a small canary deployment and then promote the canary to primary once validated.

## Notes

These manifests are designed as templates. For real production traffic shaping, connect them to an ingress controller or service mesh that supports weighted routing.
