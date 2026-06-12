 # Deployment Information

## Public URL
https://[your-agent-app-name].railway.app
*(Replace the URL above with your actual deployment URL)*

## Platform
Railway

## Test Commands

### Health Check
```bash
curl https://[your-agent-app-name].railway.app/health
# Expected: {"status": "ok"}
```

### API Test (with authentication)
```bash
curl -X POST https://[your-agent-app-name].railway.app/ask \
  -H "X-API-Key: my-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
```

## Environment Variables Set
- `PORT` = 8000
- `REDIS_URL` = [Your Managed Redis URL provided by Railway]
- `AGENT_API_KEY` = my-secret-key
- `LOG_LEVEL` = INFO

## Screenshots
- [Deployment dashboard](screenshots/dashboard.png) *(Add your screenshot here)*
- [Service running](screenshots/running.png) *(Add your screenshot here)*
- [Test results](screenshots/test.png) *(Add your screenshot here)*
