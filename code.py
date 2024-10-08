import pandas as pd
import time
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Function to get Chrome options
def get_chrome_options():
    """
    Configures and returns Chrome options for a Selenium WebDriver instance.

    The options set include:
    - Disabling the sandbox environment.
    - Disabling the use of /dev/shm.
    - Setting the log level to 3 to disable info and warning logs.
    - Configuring download preferences to avoid prompts and enable safe browsing.
    - Excluding automation switches to prevent detection of automation.
    - Disabling Blink features related to automation control.

    Returns:
        Options: A configured instance of Chrome options.
    """
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=3")  # Disable info and warning logs
    chrome_options.add_experimental_option("prefs", {
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    return chrome_options

# Function to download the CSV file from the grants page using Selenium
def download_grants_csv():
    """
    Downloads a CSV file of grant results from grants.gov.
    This function configures Chrome options to set a specific download directory,
    initializes a Chrome WebDriver, and navigates to the grants.gov search page.
    It waits for the "Export Results" button to become clickable, then clicks it
    to download the CSV file. The function waits for a few seconds to ensure the
    file is downloaded before quitting the WebDriver.
    Raises:
        TimeoutException: If the "Export Results" button could not be found or was
                          not available in time.
    """
    chrome_options = get_chrome_options()
    download_dir = "C:\\Users\\jhond\\Desktop\\Diego\\Personal\\Portfolio\\Tablero Grants" # Change this to the desired download directory
    prefs = {"download.default_directory": download_dir}
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
    })
    try:
        # Open the grants page
        driver.get("https://www.grants.gov/search-grants")
        time.sleep(5)  # Wait a bit before interacting with the page
        
        # Wait for the export button to be available and click it
        export_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'usa-link') and contains(text(), 'Export Results')]")
        ))
        driver.execute_script("arguments[0].scrollIntoView(true);", export_button)
        time.sleep(2)
        driver.execute_script("arguments[0].click();", export_button)
        
        # Wait a few seconds for the file to download
        time.sleep(20)
    except TimeoutException:
        print("The export button could not be found or was not available in time.")
    finally:
        driver.quit()

# Generalized function to extract information from a section
def extract_info(driver, xpath):
    """
    Extracts information from a web page section identified by an XPath.

    Args:
        driver (WebDriver): The Selenium WebDriver instance used to interact with the web page.
        xpath (str): The XPath string used to locate the section of the web page.

    Returns:
        dict: A dictionary containing the extracted information where the keys are the field names and the values are the corresponding field values.

    Raises:
        NoSuchElementException: If the section identified by the given XPath is not found.
    """
    info = {}
    try:
        section = driver.find_element(By.XPATH, xpath)
        rows = section.find_elements(By.XPATH, ".//tr")
        for row in rows:
            columns = row.find_elements(By.TAG_NAME, "td")
            if len(columns) == 2:
                field = columns[0].text.strip()
                value = columns[1].text.strip()
                info[field] = value
    except NoSuchElementException:
        print(f"Section with xpath '{xpath}' not found")
    return info

# Function to process the grant links
def process_links(links):
    """
    Processes a list of grant links and extracts relevant information from each link.
    Args:
        links (list): A list of strings, where each string is a unique identifier for a grant.
    Returns:
        list: A list of dictionaries, where each dictionary contains combined information
              extracted from the grant page, including general information, eligibility information,
              additional information, and the link to the grant page.
    Raises:
        NoSuchElementException: If the required elements are not found on the page.
        TimeoutException: If the page takes too long to load the required elements.
    Notes:
        - This function uses Selenium WebDriver to navigate to each grant page and extract information.
        - The function waits for specific elements to load on the page before attempting to extract information.
        - If information cannot be extracted from a page, a warning message is printed and the page is skipped.
    """
    data = []

    for link in links:
        chrome_options = get_chrome_options()
        url = f"https://www.grants.gov/search-results-detail/{link}"
        with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) as driver:
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
            })
            try:
                driver.get(url)

                # Wait for the grant information to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'display-flex flex-row flex-justify')]"))
                )

                # Extract information using the generalized function
                general_info = extract_info(driver, "//div[contains(@class, 'display-flex flex-row flex-justify')]")
                eligibility_info = extract_info(driver, "//div[contains(@class, 'display-flex flex-row flex-align-stretch')]")
                additional_info = extract_info(driver, "//h2[contains(text(), 'Additional Information')]/following-sibling::div[contains(@class, 'border border-base-light padding-2 radius-lg shadow-1')]")
                
                # Combine all information into a single dictionary
                combined_info = {**general_info, **eligibility_info, **additional_info}
                combined_info['Link'] = url  # Add the link to the dictionary
                
                # Add the information to the list
                data.append(combined_info)
            except (NoSuchElementException, TimeoutException):
                print(f"Warning: Could not extract information from the page {url}.")

    return data

# Main function to download the links file and save the data
def main():
    """
    Main function to download, process, and save grant information.
    Steps:
    1. Downloads the grants CSV file.
    2. Searches for the downloaded CSV file in the specified directory or the default Downloads folder.
    3. Reads the CSV file and extracts the 'OPPORTUNITY NUMBER' column.
    4. Sorts the 'OPPORTUNITY NUMBER' values in ascending order and limits the number of links for testing.
    5. Extracts the IDs of the links from the 'OPPORTUNITY NUMBER' column.
    6. Processes the links to get the required information.
    7. Creates a DataFrame with the processed data.
    8. Saves the DataFrame to both CSV and XLSX files.
    Raises:
        FileNotFoundError: If the CSV file is not found.
        pd.errors.EmptyDataError: If the CSV file is empty.
        KeyError: If the 'OPPORTUNITY NUMBER' column is not found in the CSV file.
    """
    # Download the grants CSV file
    download_grants_csv()

    # Define the path of the downloaded CSV file
    download_dir = "C:\\Users\\jhond\\Desktop\\Diego\\Personal\\Portfolio\\Tablero Grants" # Change this to the desired download directory
    pattern = "grants-gov-opp-search-.*\.csv"
    downloaded_files = [f for f in os.listdir(download_dir) if re.match(pattern, f)]
    if not downloaded_files:
        # If not found in the specified path, search in the default Downloads folder
        download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        downloaded_files = [f for f in os.listdir(download_dir) if re.match(pattern, f)]
    
    if downloaded_files:
        csv_path = max([os.path.join(download_dir, f) for f in downloaded_files], key=os.path.getctime)
    else:
        print("No file matching the download pattern was found.")
        return

    try:
        # Read the links from the CSV file
        links_df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: Could not find the file {csv_path}")
        return
    except pd.errors.EmptyDataError:
        print("Error: The CSV file is empty.")
        return

    if 'OPPORTUNITY NUMBER' not in links_df.columns:
        print("The column 'OPPORTUNITY NUMBER' is not found in the CSV file.")
        return

    # Sort the 'OPPORTUNITY NUMBER' values in ascending order
    links_df = links_df.sort_values(by='OPPORTUNITY NUMBER', ascending=True)
    links_column = links_df['OPPORTUNITY NUMBER'].tolist()[:4]  # Limit the number of links for testing

    # Extract the IDs of the links from the HYPERLINK formula
    links = []
    for link in links_column:
        match = re.search(r'https://www\.grants\.gov/search-results-detail/([0-9]+)', link)
        if match:
            links.append(match.group(1))

    # Process the links and get the information
    data = process_links(links)

    # Create a DataFrame with the data
    df = pd.DataFrame(data)

    # Save to CSV
    df.to_csv('grants_info.csv', index=False)
    # Save to XLSX
    df.to_excel('grants_info.xlsx', index=False)
    
    print("Information saved in grants_info.csv")

if __name__ == "__main__":
    main()
