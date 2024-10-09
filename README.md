Summary of Key Components

**Initialization (__init__):**

Sets up the Firefox WebDriver and checks for the necessary executables (Firefox and geckodriver).
Initializes the WebDriverWait for handling dynamic page loading.

**Login (login):**

Navigates to the Naukri login page, fills in the credentials, and clicks the login button.
Handles exceptions if login fails.

**Job Search (search_jobs):**

Activates the search bar and enters job title and location.
Selects the experience level from a dropdown and clicks the search button.

**Applying to Jobs (apply_to_jobs):**

Iterates through job listings, checks if an application has already been submitted using a CSV file, and applies if not.
Handles any job-specific interactions, such as dealing with chatbots or success messages after applying.





