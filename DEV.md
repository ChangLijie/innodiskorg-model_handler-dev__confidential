# AccelBrain Model Model Handler

CI/CD workflow.

---

## 🛠️ Build Workflow

1. **Update versioning information**:
   - Edit `CHANGELOG.md` with the new version info

2. **Trigger the GitHub Actions `build-release` workflow**:
   - Push a tag (e.g., `v1.2.3`) to start the workflow
   - Multi-architecture Docker images will be built and published automatically

---

## 📦 Docker Images

- Once built, images will be published to [Docker Hub](https://hub.docker.com/r/innodiskorg/model_handler):
  ```bash
  docker pull innodiskorg/model_handler:<version>
