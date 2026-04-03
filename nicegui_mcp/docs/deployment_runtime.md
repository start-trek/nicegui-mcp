# Deployment and Runtime

Sources
- https://nicegui.io/documentation

## ASGI and WebSockets

NiceGUI runs as an ASGI application and relies on websocket behavior for interactive updates.

- use an ASGI-capable runtime
- make sure reverse proxies forward websocket traffic correctly
- treat deployment and dev reload settings as separate concerns

## Reverse Proxy Notes

- keep websocket support enabled in nginx or similar proxies
- keep base URL and forwarded headers correct
- test interactive flows, not just static page loads

## On Air and Remote Access

NiceGUI On Air is convenient, but runtime assumptions can differ from a direct deployment.

- do not build IP-based business logic around tunnel behavior
- keep sensitive production networking decisions outside demo tooling

## Reload Mode

`reload=True` is for development. It should not be the default in production-style entrypoints.
