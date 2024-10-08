# Grants.gov Data Extraction Automation Repository

This repository contains a Python script that automates the extraction of grant information from the Grants.gov website using Selenium. The script is designed to navigate through the website, download grant data in CSV format, and then process individual grant links to gather detailed information.

# Overview:

This Python-based solution is tailored to extract grant-related data efficiently and robustly from the Grants.gov website. The script leverages Selenium to automate interactions with the Grants.gov portal, enabling users to collect detailed information about grant opportunities for further analysis. The workflow involves downloading grant data in CSV format, iterating over each grant link for detailed extraction, and saving the results.

# Key Features:

## Automated Data Extraction:

1- Uses Selenium to automate browsing, clicking, and data scraping from the Grants.gov website.

2- Automated interactions include navigating pages, clicking on export buttons, and extracting textual information to minimize manual intervention.

## Browser Automation with Anti-bot Evasion:

1- Uses Chrome in a customized headless configuration to minimize detection as a bot.

2- Chrome options are adjusted to avoid detection methods used by websites to block automated scripts, ensuring higher success rates.

## Exception Handling and Robustness:

1- Includes error-handling mechanisms for common exceptions like TimeoutException and NoSuchElementException to enhance resilience during execution.

2- The script handles scenarios such as elements not found or pages timing out gracefully.

## CSV Data Persistence:

1- Downloads a CSV file of grant opportunities and saves detailed information extracted from each link.

2- Outputs the final dataset into a well-structured CSV file for further analysis and reporting.

## How to Run:

1- Clone the Repository.

2- Create and activate a virtual environment and install required dependencies.

3- Run the Script.

## Folder Structure:

- code.py: Main script for extracting grants data.

- requirements.txt: Contains Python dependencies required for running the script.

- grantsEnv.yaml: YAML file to create a conda environment as an alternative.

- README.md: Documentation for understanding the setup and usage.



## Troubleshooting:

- Timeout Issues: If elements are not loading within the expected time, increase the WebDriverWait timeout duration.

- ChromeDriver Issues: Ensure ChromeDriver is compatible with your installed Chrome version. You can update it using webdriver-manager automatically.

- Bot Detection: If Grants.gov detects the bot, consider adjusting the delay (time.sleep()) between actions or running the script in non-headless mode for debugging.
