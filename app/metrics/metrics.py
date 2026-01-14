from prometheus_client import Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST

ACTIVE_CARS = Gauge(
    "active_cars",
    "Number of cars in the system",
)

ONGOING_RENTALS = Gauge(
    "ongoing_rentals",
    "Number of ongoing rentals",
)

OPERATION_TIME = Histogram(
    "operation_time_seconds",
    "Time spent in operations",
    ["operation"],
)


def metrics_response():
    data = generate_latest()
    return data, CONTENT_TYPE_LATEST
