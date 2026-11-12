---
type: operations
title: Local web service and artifact cache
description: How SmartKit starts a shared loopback host, serves its applications, and publishes selected files from immutable artifact groups.
tags: [local-web, artifacts, loopback, autostart, previews]
verified:
  - by: openwiki/0.9.0
    at: 2026-11-12T04:28:05.666Z
sources:
  - id: openwiki-source-40ccb77e3286f565b0b3a0df
    resource: repo://docs/adr/0022-enable-explicit-current-user-login-startup-for-local-web.md
  - id: openwiki-source-f9847ac12369e9e76044e98e
    resource: repo://runtime/local_web/artifacts.py
  - id: openwiki-source-434b76fe18a0c30f36d5a64d
    resource: repo://runtime/local_web/http_server.py
  - id: openwiki-source-e4e65ac72cd9c6299fc8d0e8
    resource: repo://runtime/local_web/service.py
generated: { by: "smartkit", at: "2026-11-12T04:28:05.666Z" }
---

# Local web service and artifact cache

The [local web CLI](../../runtime/local_web/cli.py) exposes service status and control, readiness and setup pages, diff links, and artifact commands. Session hooks use a shared local host on `127.0.0.1:47821`. Startup takes a lock, checks persisted service identity against its authenticated health response, and reuses an eligible instance. An older or otherwise replaceable verified instance can be restarted. A process occupying the port without verification is preserved and startup reports the conflict. A failed startup only cleans up the child it launched. [Service lifecycle](../../runtime/local_web/service.py)

The request handler validates the host and origin and uses separate routes for live diffs, captured previews, and private service and project pages. Private endpoints require the service key. Preview responses require a published, unexpired artifact and a file declared for public access. [HTTP routing](../../runtime/local_web/http_server.py) · [Human review](../workflows/human-review.md)

## Capture, publish, and expire

Artifact capture writes one fixed group with bounded bytes and file counts. It can run without the HTTP service and defaults to private files. Publication starts or reuses the host, verifies the declared public files, and returns URLs only for those files. Publication keeps the original expiry. Periodic cleanup runs independently of request handling and readiness. The cache and web-service tests cover private capture, publication scope, modified or expired payloads, and preserving an unknown port owner. [Artifact store](../../runtime/local_web/artifacts.py) · [Service tests](../../tests/test_web_service.py) · [Cache tests](../../tests/test_artifact_cache.py)

## Login startup

Login startup records an explicit current-user preference. Windows uses a Startup shortcut. Linux uses a working user systemd manager or a supported XDG desktop startup mechanism. A stable launcher points at a verified installed runtime and session hooks can refresh that pointer. Registration status, ownership, and the user's saved choice are checked independently. Disabling removes only recorded, unchanged registration and helper files. [Login startup ADR](../../docs/adr/0022-enable-explicit-current-user-login-startup-for-local-web.md) · [Autostart implementation](../../runtime/local_web/autostart.py)
