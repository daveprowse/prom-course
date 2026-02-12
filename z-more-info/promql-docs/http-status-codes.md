# HTTP Status Codes for `code` Label

## 2xx - Success
- `200` - OK
- `201` - Created
- `202` - Accepted
- `204` - No Content

## 3xx - Redirection
- `301` - Moved Permanently
- `302` - Found
- `304` - Not Modified
- `307` - Temporary Redirect
- `308` - Permanent Redirect

## 4xx - Client Errors
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `405` - Method Not Allowed
- `408` - Request Timeout
- `429` - Too Many Requests

## 5xx - Server Errors
- `500` - Internal Server Error
- `501` - Not Implemented
- `502` - Bad Gateway
- `503` - Service Unavailable
- `504` - Gateway Timeout

## Common PromQL Patterns

```promql
# All successful requests (2xx)
prometheus_http_requests_total{code=~"2.."}

# All errors (4xx and 5xx)
prometheus_http_requests_total{code=~"[45].."}

# Specific errors
prometheus_http_requests_total{code=~"404|500"}
```

## Check Available Codes

**To see what codes exist in your system:**

```promql
prometheus_http_requests_total
```

View in Table mode to see all `code` label values present in your metrics.