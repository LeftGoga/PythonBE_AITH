from locust import HttpUser, task, between
from prometheus_client import start_http_server, Counter, Histogram
from uuid import uuid4

REQUESTS = Counter('locust_requests_total', 'Total number of requests', ['method', 'endpoint', 'status'])
FAILURES = Counter('locust_failures_total', 'Total number of failures', ['method', 'endpoint', 'status'])
RESPONSE_TIME = Histogram('locust_response_time_seconds', 'Response time', ['method', 'endpoint', 'status'])

class FastAPILoadTest(HttpUser):
    wait_time = between(0, 3)

    @task
    def register_user(self):
        with self.client.post(
            "/user-register",
            json={
                "username": str(uuid4()),
                "name": "Test User",
                "birthdate": "1970-01-01T00:00:00",
                "password": "testpassword123"
            },
            catch_response=True
        ) as response:
            REQUESTS.labels(method="POST", endpoint="/user-register", status=response.status_code).inc()
            RESPONSE_TIME.labels(method="POST", endpoint="/user-register", status=response.status_code).observe(response.elapsed.total_seconds())
            if response.status_code != 200:
                FAILURES.labels(method="POST", endpoint="/user-register", status=response.status_code).inc()




# Запуск сервера Prometheus
start_http_server(9646)