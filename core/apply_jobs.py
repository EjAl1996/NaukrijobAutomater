import csv
import os

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

from core.chatGpt_api import chat_gpt_response


class NaukriAutomation:
    def __init__(self):
        try:
            # Get the current script directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(current_dir)

            # Setup paths
            self.driver_path = os.path.join(project_dir, "drivers", "geckodriver.exe")
            self.binary = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"

            # Verify Firefox installation
            if not os.path.exists(self.binary):
                # Try 32-bit Firefox path
                self.binary = "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe"
                if not os.path.exists(self.binary):
                    raise FileNotFoundError("Firefox not found. Please install Firefox browser.")

            # Verify geckodriver exists
            if not os.path.exists(self.driver_path):
                raise FileNotFoundError(f"Geckodriver not found at: {self.driver_path}")

            # Setup Firefox options
            self.options = Options()
            self.options.binary_location = self.binary

            # Setup Service
            self.service = Service(
                executable_path=self.driver_path,
                log_path=os.path.join(project_dir, "logs", "geckodriver.log")
            )

            # Initialize driver
            print("Initializing Firefox WebDriver...")
            self.driver = webdriver.Firefox(
                service=self.service,
                options=self.options
            )
            # Initialize WebDriverWait
            self.wait = WebDriverWait(self.driver, timeout=10)
            print("Firefox WebDriver initialized successfully!")

        except Exception as e:
            print(f"Error during initialization: {str(e)}")
            raise
    def login(self, username, password):
        """Manual login to Naukri"""
        try:
            self.driver.get('https://www.naukri.com/nlogin/login')
            time.sleep(2)

            # Find and fill username
            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "usernameField"))
            )
            username_field.send_keys(username)

            # Find and fill password
            password_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "passwordField"))
            )
            password_field.send_keys(password)

            # Click login button
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login')]"))
            )
            login_button.click()
            time.sleep(3)

            print("Successfully logged in!")
            return True
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    def search_jobs(self, job_title, location, experience):
        """Search for jobs based on criteria"""
        try:
            # Click to activate the search bar (if it's collapsed)
            search_bar = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "nI-gNb-sb__placeholder"))
            )
            search_bar.click()
            time.sleep(2) 

            # Wait for job title input and fill it
            search_box = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "suggestor-input"))
            )
            search_box.clear()
            search_box.send_keys(job_title)

            # Fill location input field
            location_box = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter location']"))
            )
            location_box.clear()
            location_box.send_keys(location)

            # Handle experience dropdown
            try:
                # Click to open the experience dropdown
                exp_dropdown = self.wait.until(
                    EC.element_to_be_clickable((By.ID, "experienceDD"))
                )
                exp_dropdown.click()
                time.sleep(2) 

                # Use XPath to select the appropriate experience level from the dropdown list
                exp_option = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, f"//li[@title='{experience} years']"))
                )
                exp_option.click()
                time.sleep(1)  

            except Exception as e:
                print(f"Error setting experience: {str(e)}")

            # Click the search button
            try:
                # Try finding the search button by its class name
                search_button = self.wait.until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "nI-gNb-sb__icon-wrapper"))
                )
            except:
                # Alternate approach: find by button text or icon
                search_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'nI-gNb-sb__icon-wrapper')]"))
                )

            # Click search using JavaScript (more reliable)
            self.driver.execute_script("arguments[0].click();", search_button)
            time.sleep(10)  

            print("Search completed successfully!")
            return True

        except Exception as e:
            print(f"Search failed: {str(e)}")
            return False

    def apply_to_jobs(self, max_applications=10):
        """Apply to jobs from search results"""
        applied = 0
        applied_jobs = set()  

        # Load existing URLs from CSV file to avoid duplicates
        csv_file = "job_links.csv"
        if os.path.exists(csv_file):
            with open(csv_file, mode="r", newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    applied_jobs.add(row[0])  

        while applied < max_applications:
            try:
                # Find all job listings on the current page
                job_listings = self.wait.until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "srp-jobtuple-wrapper"))
                )

                for job in job_listings:
                    if applied >= max_applications:
                        break

                    try:
                        # Click on job to view details
                        job.click()
                        time.sleep(2)

                        # Switch to job detail tab/window
                        self.driver.switch_to.window(self.driver.window_handles[-1])

                        # Get the job URL as a unique identifier
                        job_url = self.driver.current_url

                        # Check if already applied or saved in the CSV file
                        if job_url in applied_jobs:
                            print("Already applied or link stored for this job, skipping...")
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[0])
                            continue

                        # Check if "Apply on company site" button is present
                        apply_on_site_button = self.driver.find_elements(By.XPATH,
                                                                         "//*[text()='Apply on company site']")
                        if apply_on_site_button:
                            print("Found 'Apply on company site' button, storing link...")

                            # **Check if the URL is already in the applied_jobs set**
                            if job_url not in applied_jobs:
                                # Store job link and unique identifier in CSV
                                with open(csv_file, mode="a", newline='') as file:
                                    writer = csv.writer(file)
                                    writer.writerow([job_url])
                                    applied_jobs.add(job_url)  #

                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[0])
                            continue

                        # Check if already applied
                        already_applied = self.driver.find_elements(By.ID, "already-applied")
                        if already_applied:
                            print("Already applied to this job, skipping...")
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[0])
                            continue

                        # Find and click apply button
                        apply_button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, "//*[text()='Apply']"))
                        )
                        apply_button.click()

                        # Wait to see if the chatbot opens
                        time.sleep(2)  # Give time for the chatbot to appear

                        # Check if chatbot appears by locating chatbot container
                        chatbot_container = self.driver.find_elements(By.CLASS_NAME, "_chatBotContainer")
                        if chatbot_container:
                            print("Chatbot detected, answering questions...")
                            self.handle_application_questions()

                        # Check for success message after chatbot interaction
                        success_message = self.wait.until(
                            EC.presence_of_element_located((By.XPATH,
                                                            "//span[contains(@class, 'apply-message') and contains(text(), 'successfully applied')]"))
                        )
                        if success_message:
                            applied += 1
                            print(f"Successfully applied! ({applied}/{max_applications})")

                        # **Save job URL to CSV if not already saved**
                        if job_url not in applied_jobs:
                            with open(csv_file, mode="a", newline='') as file:
                                writer = csv.writer(file)
                                writer.writerow([job_url])
                                applied_jobs.add(job_url) 

                        # Close job detail tab and switch back to main window
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])

                    except Exception as e:
                        print(f"Error applying to job: {str(e)}")
                        if len(self.driver.window_handles) > 1:
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[0])

                # Click next page if available
                # Click next page if available
                try:
                    # Locate the "Next" button using XPath
                    next_button = self.wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//a[contains(@class, 'styles_btn-secondary__2AsIP') and contains(., 'Next')]"))
                    )

                    # Scroll the button into view (just to ensure it's visible, even though we will use JavaScript click)
                    self.driver.execute_script("arguments[0].scrollIntoView();", next_button)

                    # Use JavaScript to click on the button directly to avoid issues with overlapping elements
                    self.driver.execute_script("arguments[0].click();", next_button)

                    print("Clicked on 'Next' page button")
                    time.sleep(2)  # Add some delay to allow page load

                except Exception as e:
                    print(f"Error navigating to next page: {str(e)}")
                    break




            except Exception as e:
                print(f"Error processing page: {str(e)}")
                break

    def handle_application_questions(self):
        """Handle any questions during application process"""
        try:
            while True:
                # Wait for the latest question from the bot
                question_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "(//li[contains(@class, 'botItem')]//span)[last()]"))
                )
                question = question_element.text
                # print(f"Question: {question}")  

                # Check if it's a privacy agreement question
                if "privacy" in question.lower():
                    print("Handling Privacy Agreement")
                    # Locate the "Yes" button and click it
                    yes_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//div[@class='chatbot_Chip chipInRow chipItem']/span[text()='Yes']"))
                    )
                    yes_button.click()

                    # Wait for the next question after clicking "Yes"
                    time.sleep(6)
                    continue 

                # Check for radio button questions
                radio_buttons_container = self.driver.find_elements(By.CLASS_NAME, "singleselect-radiobutton")
                if radio_buttons_container:
                    # There are radio buttons present, so proceed to fetch them
                    radio_buttons = radio_buttons_container[0].find_elements(By.CLASS_NAME, "ssrc__radio-btn-container")

                    if radio_buttons:
                        options = []
                        for button in radio_buttons:
                            label = button.find_element(By.CSS_SELECTOR, "label").text
                            options.append(label)

                        print("Available options:", options)  # Debugging line to show available options

                        # Get AI response for the question
                        options_str = "\n".join(f"{i + 1}. {opt}" for i, opt in enumerate(options))
                        response = chat_gpt_response(f"{question}\n{options_str}")

                        # Extract selected option from response
                        try:
                            # Get index from response
                            selected_option_index = int(response.split('.')[0]) - 1  
                            if 0 <= selected_option_index < len(options):
                                selected_button = radio_buttons[selected_option_index].find_element(By.CSS_SELECTOR,
                                                                                                    "input")
                                self.driver.execute_script("arguments[0].click();", selected_button)
                            else:
                                print("Invalid index from response.")
                        except ValueError:
                            print("Response does not contain a valid index.")

                    # After handling the radio button question, click the "Save" button to submit and get the next question
                    save_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'sendMsg')]"))
                    )
                    save_button.click()
                    time.sleep(6)
                    continue 

                # Check for text input questions
                text_input = self.driver.find_elements(By.XPATH, "//div[@class='textArea']")
                if text_input:
                    question_element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "(//li[contains(@class, 'botItem')]//span)[last()]"))
                    )
                    question = question_element.text
                    response = chat_gpt_response(question)
                    text_input[0].send_keys(response if response else "None")

                    # After handling the text input question, click the "Save" button
                    save_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'sendMsg')]"))
                    )
                    save_button.click()
                    time.sleep(6)
                    continue  # Continue to next question

                # Check if the application is complete
                success_message = self.driver.find_elements(
                    By.XPATH, "//span[contains(@class, 'apply-message') and contains(text(), 'successfully applied')]"
                )
                if success_message:
                    print("Application completed successfully!")
                    break  

        except Exception as e:
            print(f"Error handling application questions: {str(e)}")

    def close(self):
        """Close the browser"""
        self.driver.quit()


# Usage example
def main():
    bot = NaukriAutomation()

    # Login
    username = "your naukri username"
    password = "your naukri password"
    if bot.login(username, password):
        # Search parameters
        job_title = "java developer"
        location = "bengaluru"
        experience = "3"  

        # Perform search
        bot.search_jobs(job_title, location, experience)

        # Apply to jobs
        bot.apply_to_jobs(max_applications=5)

    # Close browser
    bot.close()


if __name__ == "__main__":
    main()