## Project Overview

This project is a Django-based AI Sales application. It utilizes a number of third-party packages including Django REST Framework for building Web APIs, Simple JWT for token-based authentication, and LangChain for AI-powered features. The project is configured to use a PostgreSQL database and has a custom user model. The application is divided into several apps: `users`, `home`, `emailModule`, and `aiModule`.

## Building and Running

### Prerequisites

*   Python >= 3.13
*   `uv` for package management

### Installation

1.  Install the required packages:
    ```bash
    uv add -r requirements.txt
    ```

### Running the application

1.  Apply database migrations:
    ```bash
    uv run python manage.py migrate
    ```
2.  Start the development server:
    ```bash
    uv run python manage.py runserver
    ```

### Testing

To run the tests, use the following command:

```bash
uv run python manage.py test
```

## Development Conventions

*   The project follows the standard Django project structure.
*   The custom user model is located in `apps/users/models/user_model.py`.
*   API documentation is available at `/api/docs/`.
*   The project uses `python-dotenv` to manage environment variables. A `.env.example` file is provided as a template.
*   The project uses `uv` for package management.
