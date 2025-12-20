# Kursovaya 
 
Custom Dockerfile to speedup ci/cd:

FROM ghcr.io/actions/actions-runner:latest

```
FROM ghcr.io/actions/actions-runner:latest

USER root

RUN curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash

USER runner
```

Commands have done to build:
```
docker build -t "ghcr.io/hlebushek87/customarcrunnerwithhelm:latest" .
docker push ghcr.io/hlebushek87/customarcrunnerwithhelm
```

Secret with private docker server credentials:
```
kubectl create secret docker-registry ghcr-pull-secret --docker-server=ghcr.io --docker-username=Hlebushek87 --docker-password=<PAT> -n arc-runners
```

ARC runner yaml configuration for helm chart installation:
```
githubConfigUrl: https://github.com/Hlebushek87/Kursovaya
githubConfigSecret:
  github_token: <PAT>
template:
  spec:
    serviceAccountName: arc-runner-sa
    imagePullSecrets:
    - name: ghcr-pull-secret
    securityContext:
      runAsUser: 1000
      runAsGroup: 1000
    containers:
      - securityContext:
          privileged: true
          capabilities:
            add: ["SETFCAP", "MKNOD", "SYS_ADMIN"]
        name: runner
        image: ghcr.io/hlebushek87/customarcrunnerwithhelm:latest
        command: ["/home/runner/run.sh"]
        env:
          - name: ACTIONS_RUNNER_CONTAINER_HOOKS
            value: /home/runner/k8s/index.js
          - name: ACTIONS_RUNNER_POD_NAME
            valueFrom:
              fieldRef:
                fieldPath: metadata.name
          - name: ACTIONS_RUNNER_CONTAINER_HOOK_TEMPLATE
            value: /home/runner/job-template/content
        volumeMounts:
          - name: work
            mountPath: /home/runner/_work
        resources:
          requests:
            cpu: 200m
            memory: 300Mi
    volumes:
      - name: work
        ephemeral:
          volumeClaimTemplate:
            spec:
              accessModes: ["ReadWriteOnce"]
              storageClassName: local-path
              resources:
                requests:
                  storage: 1Gi
job:
  enabled: true
  resources:
    requests:
      cpu: 200m
      memory: 512Mi
    limits:
      memory: 512Mi
```

Commands to update ARC runner's chart:
```
helm uninstall arc-runner-set -n arc-runners
helm install arc-runner-set -f values.yaml oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set -n arc-runners
```
