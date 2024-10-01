
# Financial Transaction Processor with Django and Celery

This project is a Django-based application for processing financial transactions asynchronously using Celery. It includes functionality to track task states, ensure data integrity, and handle retries for sensitive operations like deposits and withdrawals.

## Features

- **Asynchronous Task Processing**: Uses Celery to handle transaction processing asynchronously.
- **Task State Tracking**: Stores task progress and results in a `TaskTracker` model.
- **Atomic Transactions**: Ensures all financial operations are executed within safe database transactions.
- **Task Retries and Error Handling**: Automatically retries tasks upon failure with customizable backoff intervals.
- **Real-time Monitoring**: Can be extended with Flower for real-time task tracking.

## Prerequisites

Ensure you have the following installed on your system:

- Python (>= 3.6)
- Django (>= 3.0)
- Celery (>= 5.0)
- A message broker (Redis or RabbitMQ)
- A result backend for Celery (Redis, PostgreSQL, etc.)