# Backend

## Setup

We recommend using `uv`.

1. Setup

    ```sh
    # Copy the base .env file
    cp .env.example .env

    # Migrate changes and create admin account
    uv run _setup.py

    # Run
    uv run manage.py runserver
    ```

2. Optionally provide a `cookies.txt` file in Netscape cookies.txt format for use when fetching information from external websites. You can also use browser extensions to extract them from a session (e.g. [cookies.txt](https://addons.mozilla.org/ja/firefox/addon/cookies-txt/)).

### Notes

-   Default user username specified in .env.example: `admin` and password: `admin`.
-   Be careful: the script `_clear.py` deletes the database.
