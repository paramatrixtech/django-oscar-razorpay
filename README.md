# Basic Django Project Setup and Run with `venv`

This README outlines the basic steps to create a new Django project and run it using a virtual environment (`venv`). This ensures your project dependencies are isolated from your system-wide Python installation.

## Prerequisites

*   **Python 3:** Make sure you have Python 3 installed (Python 3.6 or later is recommended).  You can check by running `python3 --version` or `python --version` in your terminal.  If it's not installed, download and install it from [python.org](https://www.python.org/).
*   **pip:**  `pip` is the package installer for Python. It usually comes bundled with Python.  You can verify its installation by running `pip3 --version` or `pip --version`. If you don't have it, you can install it using your system's package manager (e.g., `sudo apt install python3-pip` on Debian/Ubuntu, `brew install python3` on macOS, or get it through `get-pip.py` as described on [pip's website](https://pip.pypa.io)).

## Steps

1.  **Create a Project Directory:**

    Create a directory for your project. This is where all your project files will live.

    ```bash
    mkdir my_django_project
    cd my_django_project
    ```

2.  **Create a Virtual Environment:**

    It's crucial to use a virtual environment to isolate your project's dependencies.  This prevents conflicts with other Python projects on your system.  We'll use the built-in `venv` module.

    ```bash
    python3 -m venv venv
    ```
    This command creates a directory named `venv` (you can name it anything, but `venv` is a common convention) within your project directory.  This directory contains a self-contained Python installation.

3.  **Activate the Virtual Environment:**

    Before you can use the virtual environment, you need to activate it.  The activation script modifies your shell's environment variables so that `python` and `pip` commands point to the virtual environment's versions.

    *   **On macOS and Linux:**

        ```bash
        source venv/bin/activate
        ```

    *   **On Windows (Command Prompt):**

        ```bash
        venv\Scripts\activate.bat
        ```
    *   **On Windows (PowerShell):**

        ```powershell
        venv\Scripts\Activate.ps1
        ```
    
    After activation, your terminal prompt will usually change to indicate that the virtual environment is active (e.g., it might show `(venv)` at the beginning).

4.  **Install Django:**

    Now that your virtual environment is active, install Django using `pip`:

    ```bash
    pip install django
    ```
    This installs the latest stable version of Django within your virtual environment.  It will *not* affect your system-wide Python installation.

5.  **Create a Django Project:**

    Use the `django-admin` command to create a new Django project.  The project is the overall container for your website.

    ```bash
    django-admin startproject myproject .
    ```
    *   `myproject` is the name of your project (you can choose a different name).
    *   The `.` (dot) at the end is *important*.  It tells Django to create the project structure in the *current* directory (your `my_django_project` directory), without creating an extra nested directory.  If you omit the dot, you'll get `my_django_project/myproject/myproject/...`, which is usually not what you want for a basic setup.

    This command will create the following directory structure:

    ```
    my_django_project/
    ├── manage.py
    └── myproject/
        ├── __init__.py
        ├── settings.py
        ├── urls.py
        └── wsgi.py
        └── asgi.py
    ```

    *   `manage.py`:  A command-line utility for interacting with your Django project.
    *   `myproject/`:  The actual Python package for your project.
        *   `__init__.py`:  An empty file that tells Python this directory is a package.
        *   `settings.py`:  Configuration for your Django project.
        *   `urls.py`:  URL declarations for your project.
        *   `wsgi.py`:  Entry point for WSGI-compatible web servers.
        *   `asgi.py`: Entry-point for ASGI-compatible web servers (for asynchronous applications).

6.  **Run the Development Server:**

    Django comes with a built-in lightweight development web server.  You can start it using `manage.py`:

    ```bash
    python manage.py runserver
    ```

    By default, the server will run on `http://127.0.0.1:8000/`.  You should see output similar to this:

    ```
    Watching for file changes with StatReloader
    Performing system checks...

    System check identified no issues (0 silenced).
    ...
    Django version 4.x.x, using settings 'myproject.settings'
    Starting development server at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.
    ```

7.  **View Your Project in a Browser:**

    Open your web browser and go to  `http://127.0.0.1:8000/`. You should see the default Django welcome page, confirming that your project is running correctly.

8.  **Stop the Server:**

    To stop the development server, press `Ctrl+C` in the terminal where it's running.

9. **Deactivate the Virtual Environment (Optional):**

When you're finished working on your project, you can deactivate the virtual environment:

```bash
deactivate
```

# Installing and Configuring django-oscar-razorpay

This guide explains how to install and configure the `django-oscar-razorpay` package, which provides Razorpay integration for Django Oscar e-commerce projects.

## Prerequisites

*   **A Running Django Oscar Project:** You should already have a Django Oscar project set up and running. If you don't, follow the instructions in the Django Oscar documentation to create one.
*   **Razorpay Account:**  You will need a Razorpay account.  Sign up for one at [https://razorpay.com/](https://razorpay.com/).  You'll need your **Key Id** and **Key Secret** from your Razorpay dashboard.
*  **Activated Virtual Environment:** Ensure that the virtual environment for your Django Oscar project is activated.

## Installation Steps

1.  **Install the Package:**

    Use `pip` to install `django-oscar-razorpay` within your activated virtual environment:

    ```bash
    pip install django-oscar-razorpay
    ```

2.  **Add to `INSTALLED_APPS`:**

    Open your project's `settings.py` file (usually located in `yourproject/yourproject/settings.py`).  Add `'oscar_razorpay'` to the `INSTALLED_APPS` list.  It's important to place it *after* Oscar's core apps and any other Oscar apps you're using, but *before* any of your custom apps that might override Oscar's functionality.  Here's an example, assuming you have a basic Oscar setup and a custom app called `my_shop`:

    ```python
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.sites',
        'django.contrib.flatpages',

        'oscar',
        'oscar.apps.analytics',
        'oscar.apps.checkout',
        'oscar.apps.address',
        'oscar.apps.shipping',
        # ... other Oscar apps ...
        'oscar.apps.payment',
        'oscar.apps.offer',
        'oscar.apps.basket',
        'oscar.apps.search',
        'oscar.apps.voucher',
        'oscar.apps.wishlists',
        'oscar.apps.dashboard',
        'oscar.apps.dashboard.reports',
        # ... other Oscar dashboard apps ...
        'oscar.apps.customer',

        'widget_tweaks',
        'haystack',
        'treebeard',

        # Add django-oscar-razorpay here:
        'rzpay',
    ]

    SITE_ID = 1  # Ensure SITE_ID is set correctly
    ```

3.  **Configure Razorpay Settings:**

    Add the following settings to your `settings.py` file, replacing the placeholders with your actual Razorpay credentials and URLs:

    ```python
    RAZORPAY_KEY_ID = 'YOUR_RAZORPAY_KEY_ID'  # From your Razorpay dashboard
    RAZORPAY_KEY_SECRET = 'YOUR_RAZORPAY_KEY_SECRET'  # From your Razorpay dashboard

    # URLs for success and failure redirects
    RAZORPAY_SUCCESS_URL = "/checkout/success/"  # Replace with your actual success URL
    RAZORPAY_FAILURE_URL = "/checkout/failure/"  # Replace with your actual failure URL

    # Checkout page customization
    RAZORPAY_VENDOR_NAME = "Example Store"  # Replace with your store's name
    RAZORPAY_DESCRIPTION = "Payment for your Example Order"  # Replace with a suitable description
    RAZORPAY_THEME_COLOR = "#007BFF"  # Checkout page theme color (blue example)
    RAZORPAY_VENDOR_LOGO = "https://example.com/logo.png"  # Replace with your logo URL or leave blank
    RAZORPAY_TIMEOUT = 600  # Checkout timeout in seconds (10 minutes) - integer value
    IS_RAZORPAY_TIMEOUT = True  # Enable or disable the timeout (True/False)

    ```

    *   **`RAZORPAY_KEY_ID`**: Your Razorpay Key ID (obtained from your Razorpay dashboard).
    *   **`RAZORPAY_KEY_SECRET`**: Your Razorpay Key Secret (obtained from your Razorpay dashboard).
    *   **`RAZORPAY_SUCCESS_URL`**: The URL Razorpay will redirect to after a *successful* payment.  **Must be a valid URL within your Django project.**
    *   **`RAZORPAY_FAILURE_URL`**: The URL Razorpay will redirect to after a *failed* payment. **Must be a valid URL within your Django project.**
    *   **`RAZORPAY_VENDOR_NAME`**: The name of your store/business displayed on the checkout page.
    *   **`RAZORPAY_DESCRIPTION`**: A short description of the transaction displayed on the checkout page.
    *   **`RAZORPAY_THEME_COLOR`**:  (Optional) The primary color of the Razorpay checkout interface (hex color code).
    *   **`RAZORPAY_VENDOR_LOGO`**:  (Optional)  The URL of your store's logo image (must be publicly accessible).
    *   **`RAZORPAY_TIMEOUT`**: (Optional) The timeout (in seconds) for the Razorpay checkout.  *Must be an integer.*
    *   **`IS_RAZORPAY_TIMEOUT`**: (Optional)  A boolean value (`True` or `False`) to enable or disable the timeout.
   

4.  **Include Oscar's URLs (if not already included):**
    
    Make sure your project's main `urls.py` file includes Oscar's URLs.  This is usually done during the initial Oscar setup, but it's essential to verify:

    ```python
    from django.contrib import admin
    from django.urls import include, path

    urlpatterns = [
        path('admin/', admin.site.urls),
        path("razorpay/", include("rzpay.urls")),  # Include Razorpay's URLs
    ]
    ```

5. **Migrate your database:**

   Run database migrations to create the necessary tables for `django-oscar-razorpay`:

    ```bash
    python manage.py migrate
    ```

6. **Run the Server:**

   Start the Django development server:

    ```bash
    python manage.py runserver
    ```

## Testing and Usage

1.  **Checkout Process:**  During the checkout process in your Oscar store, Razorpay should now be available as a payment option.

2.  **Test Payments:**  Use Razorpay's test cards (available in their documentation) to simulate successful and failed payments.  This is crucial to ensure everything is working correctly before going live.

3.  **Dashboard Integration (Optional):** `django-oscar-razorpay` also provides dashboard integration.  To use this, you would typically add links or views in your custom dashboard app to interact with Razorpay data (e.g., view payment details, issue refunds).  This is a more advanced topic and depends on how you've customized your Oscar dashboard.

## URL Explanations

Here's a breakdown of the URL patterns provided by `django-oscar-razorpay`:

### `razorpay/payment/` (Initiating Razorpay Checkout)

*   **URL:** `https://example.com/razorpay/payment/`
*   **Pattern:** `path('payment/', views.PaymentView.as_view(), name='razorpay-payment')`
*   **View:** `views.PaymentView.as_view()`
*   **Purpose:** This URL serves as the entry point for initiating the Razorpay checkout process.  When a user adds items to their cart and proceeds to checkout, the Oscar checkout process should redirect them to this URL.  The `PaymentView` (provided by `django-oscar-razorpay`) interacts with the Razorpay API to create a payment request and then redirects the user to the Razorpay checkout page.  You generally *do not* link to this URL directly from your templates; the Oscar checkout flow handles the redirection.

### `razorpay/transaction/` (Transaction List)

*   **URL:** `https://example.com/razorpay/transaction/`
*   **Pattern:** `path('transaction/', TransactionListView.as_view(), name='razorpay-transaction-list')`
*   **View:** `TransactionListView.as_view()`
*   **Purpose:** This URL displays a *list* of all Razorpay transactions associated with your store.  It's typically used in a dashboard or order management section, enabling administrators to view all payments processed through Razorpay.
### `razorpay/transaction/<transaction_id>/` (Transaction Detail)

*   **URL:** `https://example.com/razorpay/transaction/<transaction_id>/` (e.g., `https://example.com/razorpay/transaction/123/`)
*   **Pattern:** `re_path(r'^transaction/(?P<pk>\d+)/$', TransactionDetailView.as_view(), name='razorpay-transaction-detail')`
*   **View:** `TransactionDetailView.as_view()`
*   **Purpose:** This URL displays the details of a *specific* Razorpay transaction. The `<transaction_id>` portion of the URL is a dynamic parameter (captured as `pk` in the URL pattern) representing the unique ID of the transaction. This view is typically used in a dashboard or order history section, allowing administrators or users to view the details of a particular payment.

