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

2. Generete `cookies.txt` by `yt-dlp` (i don't know how to), or browser extensions (e.g. [cookies.txt](https://addons.mozilla.org/ja/firefox/addon/cookies-txt/)) and place.

    ```
    # Netscape HTTP Cookie File
    # https://curl.haxx.se/rfc/cookie_spec.html

    ...
    ```

### Memo

-   Default user username: `admin` and password: `admin`.
-   Be careful: the script `_clear.py` deletes the database.
