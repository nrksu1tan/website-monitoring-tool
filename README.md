# Website Change Monitor

A Python script to monitor changes on a specific website by comparing HTML content, DOM elements, screenshots, and CSS files.


## Overview

This script is designed to monitor the Lenovo Gaming website for any changes. It performs various checks to detect alterations in the website's content and structure, including:

- Comparing HTML hashes.
- Comparing HTML structures using BeautifulSoup.
- Checking DOM elements.
- Detecting changes in headers (`<h1>` and `<h2>`).
- Comparing screenshots of the website.
- Comparing CSS files.

---

## Features

- **Automated Monitoring**: Continuously monitors the specified website for changes.
- **Multi-level Comparison**: Uses multiple methods to detect changes, ensuring high accuracy.
- **Cookie Management**: Handles cookie acceptance automatically.
- **User Interaction**: Allows manual checks and displays detailed results.
- **Logging and Reporting**: Outputs the status of each check with clear formatting.

---

## Requirements

- Python 3.x
- Selenium WebDriver
- ChromeDriver (Ensure it matches your Chrome browser version)
- Additional Python packages:
  - `requests`
  - `beautifulsoup4`
  - `Pillow`
  - `tqdm`
  - `colorama`

---
## Setup

### ChromeDriver Path
- **Update the** `CHROMEDRIVER_PATH` variable in the script to point to the location of your `chromedriver.exe`.  
For example:
```python
CHROMEDRIVER_PATH = "C:\\path\\to\\chromedriver.exe"
```
## Configuration

- **Target URL:** Modify the `URL` variable to the website you wish to monitor:

  ```python
  URL = "https://example.com"
  ```
  ```python
  CHECK_INTERVAL = 7200  # Checks every 2 hours
  ```
## Usage
- Run the script using Python:

    ```python
    python monitor.py
    ```
- While the script is running, you can manually trigger a **```check```** by typing check and pressing Enter. To stop the script, press ```Ctrl+C```.

---

## Future Enhancements
 - Email Notifications: Implement functionality to send email alerts when changes are detected.
- GUI Interface: Develop a graphical user interface for easier interaction.
- Extended Browser Support: Add compatibility with browsers other than Chrome.
- Detailed Logging: Enhance logging to provide more comprehensive information about detected changes.
- Contributing
- Contributions are welcome! Please fork the repository and submit a pull request with your improvements.


  
