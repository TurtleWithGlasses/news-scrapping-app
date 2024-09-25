import tkinter as tk
import requests
from requests.exceptions import ConnectionError, Timeout
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import threading
import time

# Create the main application window
root = tk.Tk()
root.title("News Scraper and Email Sender")

# Set the window icon
# icon_path = "C:\\Users\\mhmts\\PycharmProjects\\news-scraping-app-project\\newspaper_news_icon.ico"
# icon = tk.PhotoImage(file=icon_path)
# root.iconphoto(True, icon)

EMAIL_FILE = "emails.txt"  # File to store email addresses

# --- Frame 1 with Scrollbar for News Websites ---
frame1 = tk.Frame(root, padx=5, pady=5)
frame1.grid(row=0, column=0, sticky="nsew")

# Add a canvas for scrolling
canvas = tk.Canvas(frame1)
scrollbar = tk.Scrollbar(frame1, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Set minimum height for the scrollable area to make scrollbar visible
scrollable_frame.update_idletasks()
canvas.configure(scrollregion=canvas.bbox("all"))

# Place the canvas and scrollbar
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

news_sites_title_label = tk.Label(scrollable_frame, text="News Sites", font=("Arial", 14))
news_sites_title_label.pack(anchor="w", pady=(0, 10))

def _on_mousewheel(event):
    if event.num == 5 or event.delta == -120:
        canvas.yview_scroll(1, "units")
    elif event.num == 4 or event.delta == 120:
        canvas.yview_scroll(-1, "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows and MacOS
canvas.bind_all("<Button-4>", _on_mousewheel)    # Linux scroll up
canvas.bind_all("<Button-5>", _on_mousewheel) 

# --- Frame 2 for Email Addresses ---
frame2 = tk.Frame(root, padx=10, pady=10)
frame2.grid(row=0, column=1, sticky="nsew")

root.geometry("700x400")  # Adjusted window size for better layout

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
    ("https://www.iha.com.tr/ekonomi", "İHA"),
    ("https://www.aksam.com.tr/ekonomi/", "Akşam"),
    ("https://www.turkiyegazetesi.com.tr/ekonomi", "Türkiye"),
    ("https://www.posta.com.tr/ekonomi/", "Posta")
]

# Dictionary to hold the state of each checkbox and label for "OK" message
checkbox_vars = {}
status_labels = {}

# Add select all check box
def toggle_select_all():
    select_all_state = select_all_var.get()
    for url, (var, name) in checkbox_vars.items():
        var.set(select_all_state)

select_all_var = tk.BooleanVar()

select_all_checkbox = tk.Checkbutton(scrollable_frame, text="Select All", variable=select_all_var, command=toggle_select_all)
select_all_checkbox.pack(anchor="w", pady=(0, 10))

# Add checkboxes and status labels to Frame 1
for url, name in news_sites:
    var = tk.BooleanVar()
    checkbox_frame = tk.Frame(scrollable_frame)
    checkbox = tk.Checkbutton(checkbox_frame, text=url, variable=var)
    checkbox.pack(side="left", anchor="w")  # Align left
    
    # Add a label for showing the "OK" message after scraping
    status_label = tk.Label(checkbox_frame, text="", fg="green")  # Label for OK message
    status_label.pack(side="left", padx=10)
    
    checkbox_frame.pack(anchor="w", pady=(2, 2))
    
    checkbox_vars[url] = (var, name)
    status_labels[url] = status_label  # Store the label for updating the "OK" message

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
            
            elif "aksam.com.tr" in url:
                # Scrape <a> tags and get the headline from the <div> inside
                for item in soup.find_all('a', href=True):
                    div_tag = item.find('div', style=True)
                    if div_tag:
                        headline = div_tag.get_text().strip()
                        link = item['href']
                        # Ensure the link is absolute
                        if not link.startswith("http"):
                            link = f"https://www.aksam.com.tr{link}"
                        if headline and link:
                            headlines.append(f"{headline}: {link}")
                
                for item in soup.find_all('a', href=True, class_='full-link'):
                    headline = item.get_text().strip()
                    link = item['href']
                    # Ensure the link is absolute
                    if not link.startswith("http"):
                        link = f"https://www.aksam.com.tr{link}"
                    if headline and link:
                        headlines.append(f"{headline}: {link}")

            elif "turkiyegazetesi.com.tr" in url:
                # Scrape <a> tags and get the headline from the <div> inside
                for item in soup.find_all('a', href=True, class_='category-dashboard__item'):
                    headline_div = item.find('div', class_='category-dashboard__label')
                    if headline_div:
                        headline = headline_div.get_text().strip()
                        link = item['href']
                        # Ensure the link is absolute
                        if not link.startswith("http"):
                            link = f"https://www.turkiyegazetesi.com.tr{link}"
                        if headline and link:
                            headlines.append(f"{headline}: {link}")
                
                for item in soup.find_all('a', href=True, class_='category-dashboard__item'):
                    # Scrape both regular and small label classes
                    label_div = item.find('div', class_='category-dashboard__label')
                    small_label_div = item.find('div', class_='category-dashboard__label--small')
                    
                    # Handle both regular and small label types
                    if label_div:
                        headline = label_div.get_text().strip()
                    elif small_label_div:
                        headline = small_label_div.get_text().strip()
                    else:
                        continue
                    
                    link = item['href']
                    # Ensure the link is absolute
                    if not link.startswith("http"):
                        link = f"https://www.turkiyegazetesi.com.tr{link}"
                    
                    if headline and link:
                        headlines.append(f"{headline}: {link}")
            
            elif "posta.com.tr" in url:
                # Scrape <a> tags and get the headline from the <span> inside
                for item in soup.find_all('a', href=True, class_='swiper-slide__link'):
                    span_tag = item.find('span', class_='swiper-slide__text')
                    
                    if span_tag:
                        headline = span_tag.get_text().strip()
                        link = item['href']
                        # Ensure the link is absolute
                        if not link.startswith("http"):
                            link = f"https://www.posta.com.tr{link}"
                        
                        if headline and link:
                            headlines.append(f"{headline}: {link}")
                
                for item in soup.find_all('a', href=True):
                    h3_tag = item.find('h3', class_='main-card__head')
                    
                    if h3_tag:
                        headline = h3_tag.get_text().strip()
                        link = item['href']
                        # Ensure the link is absolute
                        if not link.startswith("http"):
                            link = f"https://www.posta.com.tr{link}"
                        
                        if headline and link:
                            headlines.append(f"{headline}: {link}")

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

def show_error_message(message):
    # Create a new Toplevel window (popup window)
    error_window = tk.Toplevel(root)
    error_window.title("Error")

    # Set size and make sure it's centered
    error_window.geometry("300x150")
    error_window.transient(root)  # Keep it above the main window

    # Add a message label with the error message
    label = tk.Label(error_window, text=message, padx=20, pady=20, fg="red", wraplength=250)
    label.pack()

    # Add an OK button to close the popup
    ok_button = tk.Button(error_window, text="OK", command=error_window.destroy)
    ok_button.pack(pady=10)

    # This makes sure the popup is modal (user cannot interact with the main window until the popup is closed)
    error_window.grab_set()


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
                status_labels[site_url].config(text="OK")  # Set OK for successful scrape

        # Create email content
        email_content = "Hello,\n\nHere are the popular news headlines:\n\n"
        email_content += "\n".join(all_headlines)

        # If there are no headlines scraped, stop the process and notify the user
        if not all_headlines:
            show_error_message("No headlines to send. Please select sites with content.")
            status_label.config(text="Failed")
            return

        # Now proceed to send emails using smtplib
        try:
            # Set up the SMTP server
            smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
            smtp_server.starttls()

            # Log in to your email account
            smtp_server.login('your-email-address', 'your-password')

            # Send email to each recipient
            for recipient in email_addresses:
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

        except smtplib.SMTPException as e:
            # Catch any SMTP-related errors and show an error message
            print("Error: unable to send email", e)
            show_error_message(f"Failed to send emails via Google: {str(e)}")
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