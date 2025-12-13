1# Kursovaya
 
Custom Dockerfile to speedup ci/cd:

FROM ghcr.io/actions/actions-runner:latest

```
FROM ghcr.io/actions/actions-runner:latest

# 1. ПЕРЕКЛЮЧАЕМСЯ НА ROOT для системных операций
USER root

# Установка Buildah и зависимостей для rootless-режима
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        buildah \
        fuse-overlayfs \
        uidmap \
    && rm -rf /var/lib/apt/lists/*

# Рекомендуемые настройки для Buildah rootless в контейнерах:
# Добавление subuid/subgid записей для пользователя runner
RUN echo "runner:100000:65536" >> /etc/subuid && \
    echo "runner:100000:65536" >> /etc/subgid

# 2. ВОЗВРАЩАЕМСЯ К ПОЛЬЗОВАТЕЛЮ RUNNER для безопасности
# (Пользователь "runner" - стандартный для этого базового образа)
USER runner
```

Commands have done to build:
```
docker build -t "ghcr.io/hlebushek87/customarcrunnerwithbuildah:latest" .
docker push ghcr.io/hlebushek87/customarcrunnerwithbuildah
```

ARC runner yaml configuration for helm chart installation:
```
githubConfigUrl: https://github.com/Hlebushek87/Kursovaya
githubConfigSecret:
  github_token: <PAT>
template:
  spec:
    serviceAccountName: arc-runner-sa
    containers:
      - name: runner
        image: ghcr.io/hlebushek87/customarcrunnerwithbuildah:latest
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
          - name: job-template
            mountPath: /home/runner/job-template
            readOnly: true
        resources:
          requests:
            cpu: 200m
            memory: 300Mi
    volumes:
      - name: job-template
        configMap:
          name: job-template-gha-runner-werf
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
