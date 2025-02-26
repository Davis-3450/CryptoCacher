# CryptoCacher

A high-performance API service that caches Binance cryptocurrency data using Redis.

## Project Overview

CryptoCacher demonstrates the performance benefits of implementing a caching layer between your application and external APIs. By caching responses from the Binance API in Redis, we can:

- Significantly reduce response times for repeated queries
- Decrease load on the Binance API
- Avoid hitting rate limits
- Provide consistent data availability even if the Binance API is temporarily unavailable

## Technical Stack

- **Backend**: Flask web framework
- **Caching**: Redis for fast in-memory data storage
- **Data Source**: Binance API for cryptocurrency data
- **Testing**: Pytest for unit/integration tests, stress testing framework for performance comparison
- **Containerization**: Docker and Docker Compose for easy deployment

## Features

- Fast and reliable cryptocurrency data access
- Intelligent caching with configurable TTL (Time To Live)
- Performance metrics to compare cached vs. direct API access
- Automatic cache invalidation strategies
- Comprehensive error handling

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.8+ | uv astral
- Binance API credentials
