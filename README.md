## Project Overview

CryptoCacher is a project that shows the benefits of implementing a caching layer between your application and external APIs. By caching responses from the Binance API in Redis, we can:

- Significantly reduce response times for repeated queries, which will allow for further scaling.
- Decrease load on the Binance API.
- Avoid hitting rate limits.
- Provide consistent data availability even if the Binance API is temporarily unavailable

Note: this is a learning project

## Technical Stack

- **Backend**: FastAPI web framework
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
-

### Prerequisites

- Docker and Docker Compose
- Python 3.8+ | uv astral
- Binance API credentials

### Roadmap

- [] Docker image
- [] Real time strategy testing (eg: tringular arbitrage)
- [] Implement tests - pytest
- [] GUI -> maybe streamlit / gradio / front with flask
