# === FastAPI middleware will be written here ======

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time


# Define metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Latency', ['method', 'endpoint'])



class PrometheusMiddleware(BaseHTTPMiddleware):

    """
    Middleware to collect Prometheus metrics for FastAPI applications.
    Measures request count and request latency for every endpoint.
    """

    # define dispatch function :
    async def dispatch(self, request: Request, call_next):

        """
        Intercepts all incoming HTTP requests.

        Args:
            request (Request): The incoming HTTP request.
            call_next: Function to process the request and get a response.

        Returns:
            response: The response from the endpoint, after metrics are recorded.
        """

        start_time = time.time()

        # Process the request :
        response = await call_next(request)

        # Record metrics after request is processed :
        duration = time.time() - start_time
        endpoint = request.url.path

        # Update Prometheus metrics :
        REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(duration)
        REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, status=response.status_code).inc()

        # Return the response so the middleware does not block the request flow :
        return response
        


# Function to set up middleware in the App : 
def setup_metrics(app: FastAPI):
    """
    Setup Prometheus metrics middleware and endpoint
    """
    # Inject Prometheus middleware into the App :
    app.add_middleware(PrometheusMiddleware)

    # Random /endpoint => Secure 
    @app.get("/testqr23wx", include_in_schema=False)                            # include_in_schema = False ==> not displayed on FastAPI docs 
    def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
    










    







   


