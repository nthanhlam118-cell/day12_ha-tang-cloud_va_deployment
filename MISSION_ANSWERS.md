# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. **Hardcoded Secrets**: API keys or passwords are in plain text in the code (`app.py`), which is a major security risk.
2. **Fixed Port**: The port is fixed to `8000` rather than being configurable via an environment variable, breaking 12-factor principles.
3. **Debug Mode Enabled**: Running the app in debug mode in production can leak sensitive stack traces and configuration data.
4. **No Health Checks**: There are no `/health` or `/ready` endpoints, so orchestrators (like Kubernetes or Cloud Run) won't know if the app is alive.
5. **No Graceful Shutdown**: The app does not handle OS signals like SIGTERM to finish ongoing requests before terminating.

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config  | Hardcode | Env vars | Allows changing config without code changes and keeps secrets out of version control. |
| Health check | None | `/health` & `/ready` | Enables container orchestrators to automatically restart failed containers or delay routing until the app is ready. |
| Logging | `print()` | JSON | JSON structured logs are easily parsed by centralized logging systems like ELK or Datadog. |
| Shutdown | Abrupt | Graceful | Prevents dropping user requests when deploying a new version or when a container is killed. |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. **Base image:** A python image, usually a larger one like `python:3.11`.
2. **Working directory:** Typically `/app`.
3. **Why COPY requirements.txt first?:** Docker caches layers. By copying `requirements.txt` first and installing dependencies, we avoid re-installing all packages every time application code changes.
4. **CMD vs ENTRYPOINT:** `ENTRYPOINT` sets the primary executable that the container runs, while `CMD` provides default arguments that can easily be overridden.

### Exercise 2.3: Image size comparison
- Develop: ~1000 MB (assuming standard python:3.11 image)
- Production: ~150 MB (using python:3.11-slim and multi-stage builds)
- Difference: ~85% reduction in size. Smaller images pull faster, have a smaller attack surface, and reduce storage costs.

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: `https://[Your-App-Name].railway.app` *(Replace with your actual URL)*
- Screenshot: `[Add screenshot link here]`

## Part 4: API Security

### Exercise 4.1-4.3: Test results
Authentication works by passing the `X-API-Key` header. Requests without it return a 401 Unauthorized error. 
Rate limiting is tracked using Redis via a sliding window pattern. After 10 requests within a minute, it returns 429 Too Many Requests.

### Exercise 4.4: Cost guard implementation
Implemented a budget tracker in Redis (`app/cost_guard.py`). Each time a request is made, we check the current month's usage. If `current_usage + estimated_cost > 10.0`, a 402 Payment Required exception is raised. Otherwise, it increments the usage value and sets an expiration of 32 days.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
- **Health/Readiness:** `/health` simply returns OK (for liveness), while `/ready` pings Redis to ensure backend services are connected before accepting traffic.
- **Graceful Shutdown:** Implemented `signal.signal(signal.SIGTERM, shutdown_handler)` to catch the termination signal, change an internal state, and return 503 for new requests while existing ones finish.
- **Stateless Design:** Removed in-memory state (like `conversation_history = {}`) and moved it entirely to Redis. Now, `agent` containers can be scaled infinitely behind Nginx without losing context.
