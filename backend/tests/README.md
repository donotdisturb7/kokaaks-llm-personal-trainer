# 🧪 Tests - KovaaK's AI Trainer Backend

Comprehensive test suite for the backend application.

---

## 📁 Structure

```
tests/
├── conftest.py              # Pytest configuration and shared fixtures
├── unit/                    # Unit tests (isolated, fast)
│   ├── test_constants.py    # Test constants module
│   ├── test_config.py       # Test configuration
│   └── test_embedding_service.py  # Test embedding service
├── integration/             # Integration tests (API endpoints)
│   ├── test_api_health.py   # Health check endpoints
│   ├── test_api_exercises.py  # Exercise endpoints
│   └── test_api_rag.py      # RAG endpoints
└── fixtures/                # Shared test fixtures and mock data
```

---

## 🚀 Running Tests

### Install dependencies
```bash
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run specific test types
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# API tests only
pytest -m api

# Exclude slow tests
pytest -m "not slow"
```

### Run specific test file
```bash
pytest tests/unit/test_constants.py
pytest tests/integration/test_api_exercises.py
```

### Run with verbose output
```bash
pytest -v
pytest -vv  # Extra verbose
```

---

## 📊 Coverage

Generate coverage report:
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

Target: **>80% coverage** for critical code paths.

---

## 🏷️ Test Markers

Tests are organized with markers for selective execution:

| Marker | Description | Example |
|--------|-------------|---------|
| `unit` | Fast, isolated unit tests | `pytest -m unit` |
| `integration` | Integration tests with dependencies | `pytest -m integration` |
| `api` | API endpoint tests | `pytest -m api` |
| `database` | Tests requiring database | `pytest -m database` |
| `external` | Tests requiring external services | `pytest -m "not external"` |
| `slow` | Slow-running tests | `pytest -m "not slow"` |

---

## 🧩 Fixtures

Common fixtures available in `conftest.py`:

### Database Fixtures
- `test_engine` - Test database engine
- `db_session` - Fresh database session per test
- `override_get_db` - Override FastAPI dependency

### Application Fixtures
- `test_app` - FastAPI test client
- `settings` - Application settings

### Mock Data Fixtures
- `mock_user_data` - Sample user data
- `mock_exercise_data` - Sample exercise data
- `mock_rag_query` - Sample RAG query
- `mock_conversation_data` - Sample conversation
- `mock_llm_response` - Sample LLM response

---

## ✅ Writing Tests

### Unit Test Example
```python
import pytest
from app.services.my_service import MyService

@pytest.mark.unit
class TestMyService:
    """Test MyService functionality"""

    @pytest.fixture
    def service(self):
        return MyService()

    def test_method(self, service):
        """Test specific method"""
        result = service.method()
        assert result is not None
```

### Integration Test Example
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.mark.integration
@pytest.mark.api
class TestMyEndpoint:
    """Test my API endpoint"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_endpoint(self, client):
        """Test endpoint returns 200"""
        response = client.get("/api/my-endpoint")
        assert response.status_code == 200
```

### Async Test Example
```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async function"""
    result = await my_async_function()
    assert result is not None
```

---

## 🔧 Configuration

### pytest.ini
Pytest configuration including:
- Test discovery patterns
- Coverage settings
- Markers definitions
- Asyncio mode

### conftest.py
Shared fixtures and test setup:
- Database setup/teardown
- Mock data
- Test client configuration

---

## 🐛 Debugging Tests

### Run specific test with output
```bash
pytest tests/unit/test_constants.py::TestConstants::test_vector_dimension -v -s
```

### Use ipdb for debugging
```python
import ipdb; ipdb.set_trace()
```

### Show print statements
```bash
pytest -s
```

### Show local variables on failure
```bash
pytest -l
```

---

## 📝 Best Practices

### ✅ DO
- Write descriptive test names
- Test one thing per test
- Use fixtures for setup
- Mock external dependencies
- Keep tests fast
- Aim for >80% coverage

### ❌ DON'T
- Test implementation details
- Create test dependencies
- Use sleep() for timing
- Hardcode test data in tests
- Skip writing tests

---

## 🎯 Test Checklist

When adding new features:

- [ ] Write unit tests for new functions/classes
- [ ] Write integration tests for new endpoints
- [ ] Update fixtures if needed
- [ ] Run full test suite
- [ ] Check coverage report
- [ ] Document any test requirements

---

## 🚨 CI/CD Integration

Tests should run automatically on:
- Pull requests
- Main branch commits
- Pre-deployment

Example GitHub Actions:
```yaml
- name: Run tests
  run: |
    cd backend
    pip install -r requirements.txt -r requirements-dev.txt
    pytest --cov=app --cov-report=xml
```

---

## 📚 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio)
- [Coverage.py](https://coverage.readthedocs.io/)
