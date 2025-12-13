1# Kursovaya
 
Custom Dockerfile to speedup ci/cd:

FROM ghcr.io/actions/actions-runner:latest

```
FROM ghcr.io/actions/actions-runner:latest

USER root

# Установка Buildah, Podman и зависимостей
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        buildah \
        podman \
        fuse-overlayfs \
        uidmap \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем правильные права и домашний каталог
RUN mkdir -p /home/runner \
    && chown -R 1000:1000 /home/runner \
    && echo "runner:100000:65536" >> /etc/subuid \
    && echo "runner:100000:65536" >> /etc/subgid

# Возвращаемся к непривилегированному пользователю
USER runner
ENV HOME=/home/runner
```

Commands have done to build:
```
docker build -t "ghcr.io/hlebushek87/customarcrunnerwithbuildah:latest" .
docker push ghcr.io/hlebushek87/customarcrunnerwithbuildah
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
          privileged: false
          capabilities:
            add: ["SETFCAP", "MKNOD"]
        name: runner
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
          - name: BUILDAH_FORMAT
            value: docker
          - name: BUILDAH_ISOLATION
            value: chroot
          - name: BUILDAH_STORAGE_DRIVER
            value: vfs
          - name: STORAGE_DRIVER
            value: vfs
          - name: WERF_BUILDER_BUILD_OPTIONS
            value: '--storage-driver=vfs'
          - name: WERF_BUILDER_OPTIONS
            value: '--storage-driver=vfs'
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
