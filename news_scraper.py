
import tkinter as tk
import time
import requests
from requests.exceptions import ConnectionError, Timeout
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import threading

# Create the main application window
root = tk.Tk()
root.title("News Scraper and Email Sender")
root.geometry("600x400")  # Adjusted window size for better layout

EMAIL_FILE = "email.txt"

# Create Frame 1 (for the list of news sites with checkboxes)
frame1 = tk.Frame(root, padx=10, pady=10)
frame1.grid(row=0, column=0, sticky="nsew")

news_sites_title_label = tk.Label(frame1, text="News Sites", font=("Arial", 14))
news_sites_title_label.pack(anchor="w", pady=(0, 10))

# Create Frame 2 (for the list of email addresses)
frame2 = tk.Frame(root, padx=10, pady=10)
frame2.grid(row=0, column=1, sticky="nsew")

# Set grid weights to ensure frames expand with the window
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

# List of news sites
news_sites = [
    ("https://www.hurriyet.com.tr/ekonomi/", "Hurriyet"),
    ("https://www.sabah.com.tr/ekonomi", "Sabah"),
    ("https://www.milliyet.com.tr/ekonomi/", "Milliyet"),
    ("https://www.haberturk.com/ekonomi", "Haberturk"),
    ("https://www.aa.com.tr/tr/ekonomi", "AA"),
    ("https://www.dha.com.tr/ekonomi/", "DHA"),
    ("https://www.ntv.com.tr/ntvpara", "NTV"),
    ("https://www.yenisafak.com/ekonomi", "Yeni Safak"),
    ("https://www.ensonhaber.com/ekonomi", "En Son Haber"),
    ("https://www.iha.com.tr/ekonomi", "İHA")
]

# Dictionary to hold the state of each checkbox
checkbox_vars = {}

# Add select all check box
def toggle_select_all():
    select_all_state = select_all_var.get()
    for url, (var, name) in checkbox_vars.items():
        var.set(select_all_state)

select_all_var = tk.BooleanVar()

select_all_checkbox = tk.Checkbutton(frame1, text="Select All", variable=select_all_var, command=toggle_select_all)
select_all_checkbox.pack(anchor="w", pady=(0, 10))

# Add checkboxes to Frame 1
for url, name in news_sites:
    var = tk.BooleanVar()
    checkbox = tk.Checkbutton(frame1, text=url, variable=var)
    checkbox.pack(anchor="w")  # Align left
    checkbox_vars[url] = (var, name)  # Store the variable and site name

# Frame 2: Email Addresses
# Title
email_section_title_label = tk.Label(frame2, text="Email Addresses", font=("Arial", 14))
email_section_title_label.pack(anchor="w", pady=(0, 10))

# Text area for email addresses
email_text = tk.Text(frame2, height=10, width=30)
email_text.pack(fill="both", expand=True)

def load_emails():
    try:
        with open(EMAIL_FILE, "r") as file:
            emails = file.read()
            email_text.insert("1.0", emails)
    except FileNotFoundError:
        pass

def save_emails():
    emails = email_text.get("1.0", tk.END).strip()
    with open(EMAIL_FILE, "w") as file:
        file.write(emails)

def scrape_website(site_name, url):
# Function to scrape headlines and URLs based on site structure
    retries = 3  # Number of retries if a request fails
    delay = 5    # Delay between retries (in seconds)    
        
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=15)  # Increased timeout
            soup = BeautifulSoup(response.text, 'lxml')

            headlines = []
            
            if "hurriyet.com.tr" in url:
                # Scrape <h2> tags, find the <a> tag inside, and get the text and href
                for item in soup.find_all('h2'):
                    a_tag = item.find('a', href=True)
                    if a_tag:
                        headline = a_tag.get_text().strip()
                        link = a_tag['href']
                        # Ensure the link is absolute
                        if not link.startswith("http"):
                            link = f"https://www.hurriyet.com.tr{link}"
                        if headline and link:
                            headlines.append(f"{headline}: {link}")
                        
            elif "sabah.com.tr" in url:
                # Scrape <a> tags, find the <span> tag inside, and get the text and href
                for item in soup.find_all('a', href=True):
                    span_tag = item.find('span')
                    if span_tag:
                        headline = span_tag.get_text().strip()
                        link = item['href']
                        # Ensure the link is absolute
                        if not link.startswith("http"):
                            link = f"https://www.sabah.com.tr{link}"
                        if headline and link:
                            headlines.append(f"{headline}: {link}")
                        
            elif "milliyet.com.tr" in url:
                # Scrape <a> tags, find the <img> tag inside, and get the text from the "alt" attribute
                for item in soup.find_all('a', href=True, class_='cat-slider__link'):
                    img_tag = item.find('img', alt=True)
                    if img_tag:
                        headline = img_tag['alt'].strip()
                        link = item['href']
                        # Ensure the link is absolute
                        if not link.startswith("http"):
                            link = f"https://www.milliyet.com.tr{link}"
                        if headline and link:
                            headlines.append(f"{headline}: {link}")
                
                for item in soup.find_all('h3', class_='category-card__head'):
                    a_tag = item.find_parent('a', href=True)  # Find the parent <a> tag to get the link
                    if a_tag:
                        headline = item.get_text().strip()
                        link = a_tag['href']
                        # Ensure the link is absolute
                        if not link.startswith("http"):
                            link = f"https://www.milliyet.com.tr{link}"
                        if headline and link:
                            headlines.append(f"{headline}: {link}")
            
            elif "haberturk.com" in url:
                # Scrape <a> tags and get the text from the "title" attribute
                for item in soup.find_all('a', href=True, class_='gtm-tracker'):
                    headline = item.get('title', '').strip()
                    link = item['href']
                    # Ensure the link is absolute
                    if not link.startswith("http"):
                        link = f"https://www.haberturk.com{link}"
                    if headline and link:
                        headlines.append(f"{headline}: {link}")
            
            elif "aa.com.tr" in url:
                        # Scrape <h2> tags, find the <a> tag inside, and get the text and href
                        for item in soup.find_all('h2', class_='pad-5'):
                            a_tag = item.find('a', href=True)
                            if a_tag:
                                headline = a_tag.get_text().strip()
                                link = a_tag['href']
                                # Ensure the link is absolute
                                if not link.startswith("http"):
                                    link = f"https://www.aa.com.tr/tr/ekonomi{link}"
                                if headline and link:
                                    headlines.append(f"{headline}: {link}")
            
            elif "dha.com.tr" in url:
                # Scrape <a> tags, find the <strong> tag inside, and get the text and href
                for item in soup.find_all('a', href=True, class_='cat-slider__link'):
                    strong_tag = item.find('strong', class_='cat-slider__title')
                    if strong_tag:
                        headline = strong_tag.get_text().strip()
                        link = item['href']
                        # Ensure the link is absolute
                        if not link.startswith("http"):
                            link = f"https://www.dha.com.tr{link}"
                        if headline and link:
                            headlines.append(f"{headline}: {link}")
                
                for item in soup.find_all('h3', class_='category-card__head'):
                    a_tag = item.find_parent('a', href=True)  # Find the parent <a> tag to get the link
                    if a_tag:
                        headline = item.get_text().strip()
                        link = a_tag['href']
                        # Ensure the link is absolute
                        if not link.startswith("http"):
                            link = f"https://www.dha.com.tr{link}"
                        if headline and link:
                            headlines.append(f"{headline}: {link}")
            
            elif "ntv.com.tr" in url:
                # Scrape <a> tags and get the text from the "title" attribute
                for item in soup.find_all('a', href=True):
                    headline = item.get('title', '').strip()
                    link = item['href']
                    # Ensure the link is absolute
                    if not link.startswith("http"):
                        link = f"https://www.ntv.com.tr{link}"
                    if headline and link:
                        headlines.append(f"{headline}: {link}")
            
            elif "yenisafak.com" in url:

                # Find all divs with the class 'ys-link news-item'
                for item in soup.find_all('div', class_='ys-link news-item'):
                    # Extract the link from the <a> tag
                    a_tag = item.find('a', href=True)
                    if a_tag:
                        link = a_tag['href']
                        # Ensure the link is absolute
                        if not link.startswith("http"):
                            link = f"https://www.yenisafak.com{link}"
                        
                        # Extract the headline from the <p class="news-title">
                        p_tag = item.find('p', class_='news-title')
                        if p_tag:
                            headline = p_tag.get_text().strip()
                            if headline and link:
                                headlines.append(f"{headline}: {link}")

            
            elif "ensonhaber.com" in url:
                # Scrape <a> tags, find the <img> tag inside, and get the text from the "alt" attribute
                for item in soup.find_all('a', href=True):
                    img_tag = item.find('img', alt=True)
                    if img_tag:
                        headline = img_tag['alt'].strip()
                        link = item['href']
                        # Ensure the link is absolute
                        if not link.startswith("http"):
                            link = f"https://www.ensonhaber.com{link}"
                        if headline and link:
                            headlines.append(f"{headline}: {link}")
            
            elif "iha.com.tr" in url:
                # Scrape <a> tags and get the text from the "title" attribute
                for item in soup.find_all('a', href=True):
                    title = item.get('title', '').strip()
                    if title:
                        link = item['href']
                        # Ensure the link is absolute
                        if not link.startswith("http"):
                            link = f"https://www.iha.com.tr{link}"
                        headlines.append(f"{title}: {link}")

            
            return site_name, headlines
        
        except (ConnectionError, Timeout) as e:
                print(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(delay)  # Wait before retrying
                else:
                    print(f"Failed to retrieve data from {url} after {retries} attempts")
                    return site_name, []
        except Exception as e:
                print(f"An error occurred while scraping {url}: {e}")
                return site_name, []

# SEND button
def send_emails():
    # Update status to "Sending..."
    status_label.config(text="Sending...")
    
    def scrape_and_send():
        # Collect selected websites
        selected_sites = [(name, url) for url, (var, name) in checkbox_vars.items() if var.get()]
        
        # Collect email addresses
        email_addresses = email_text.get("1.0", tk.END).strip().split('\n')
        
        # Scrape selected websites
        all_headlines = []
        for site_name, site_url in selected_sites:
            site_name, headlines = scrape_website(site_name, site_url)
            if headlines:
                all_headlines.append(f"News from {site_name}:\n" + "\n".join(headlines) + "\n")
        
        # Create email content
        email_content = "Hello,\n\nHere are the popular news headlines:\n\n"
        email_content += "\n".join(all_headlines)
        
        # Send email using smtplib
        try:
            # Set up the SMTP server
            smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
            smtp_server.starttls()
            
            # Log in to your email account
            smtp_server.login('mhmtsoylu1928@gmail.com', 'ytit koka hcmw ubiy')
            
            for recipient in email_addresses:
                # Create the email
                msg = MIMEMultipart()
                msg['From'] = 'your_email@gmail.com'
                msg['To'] = recipient
                msg['Subject'] = "Popular news"
                
                # Attach the email content
                msg.attach(MIMEText(email_content, 'plain'))
                
                # Send the email
                smtp_server.send_message(msg)
            
            # Update status to "Sent"
            root.after(2000, lambda: status_label.config(text="Sent"))
            
        except Exception as e:
            # Handle exceptions
            print("Error: unable to send email", e)
            status_label.config(text="Failed")
        
        finally:
            smtp_server.quit()
    
    # Start the scraping and sending process in a new thread
    threading.Thread(target=scrape_and_send).start()

send_button = tk.Button(frame2, text="SEND", command=send_emails)
send_button.pack(pady=(10, 5))

# Status label
status_label = tk.Label(frame2, text="")
status_label.pack()

def on_closing():
    save_emails()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

load_emails()

root.mainloop()