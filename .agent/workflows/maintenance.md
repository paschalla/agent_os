---
description: System Maintenance & Cleanup (Free RAM)
---

This workflow cleans up heavy development processes to free up system resources.

1. Terminate heavy background processes
   // turbo

```bash
pkill -f "vite" || true && pkill -f "uvicorn" || true && pkill -f "main.py" || true
```

2. Check System Load
   // turbo

```bash
uptime
```

3. (Instructions)
   > **Note**: To fully clear the IDE's visual memory, please press `Ctrl+Shift+P` and select "Reload Window".
