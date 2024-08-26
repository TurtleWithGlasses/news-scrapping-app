import tkinter as tk
from tkinter import ttk
import requests
from bs4 import BeautifulSoup

# Create the main application window
root = tk.Tk()
root.title("News Scraper and Email Sender")
root.geometry("600x400")  # Adjusted window size for better layout

# Set the window icon
icon_path = r"C:\Users\mhmts\PycharmProjects\news-scraping-app-project\newspaper_news_icon.png"
icon = tk.PhotoImage(file=icon_path)
root.iconphoto(True, icon)

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
    "https://www.hurriyet.com.tr/ekonomi/",
    "https://www.sabah.com.tr/ekonomi",
    "https://www.milliyet.com.tr/ekonomi/",
    "https://www.haberturk.com/ekonomi",
    "https://www.aa.com.tr/tr/ekonomi",
    "https://www.dha.com.tr/ekonomi/",
    "https://www.ntv.com.tr/ntvpara",
    "https://www.yenisafak.com/ekonomi",
    "https://www.ensonhaber.com/ekonomi"
]

# Dictionary to hold the state of each checkbox
checkbox_vars = {}

# Add checkboxes to Frame 1
for site in news_sites:
    var = tk.BooleanVar()
    checkbox = tk.Checkbutton(frame1, text=site, variable=var)
    checkbox.pack(anchor="w")  # Align left
    checkbox_vars[site] = var  # Store the variable

# Frame 2: Email Addresses
# Title
email_section_title_label = tk.Label(frame2, text="Email Addresses", font=("Arial", 14))
email_section_title_label.pack(anchor="w", pady=(0, 10))

# Text area for email addresses
email_text = tk.Text(frame2, height=10, width=30)
email_text.pack(fill="both", expand=True)

# Function to scrape headlines and URLs
def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    
    headlines = []
    
    # Example scraping logic (needs to be customized per site structure)
    for item in soup.find_all('a', href=True):
        headline = item.get_text().strip()
        link = item['href']
        if headline and link:
            headlines.append(f"{headline}: {link}")
    
    return headlines

# SEND button
def send_emails():
    # Update status to "Sending..."
    status_label.config(text="Sending...")
    
    # Collect selected websites
    selected_sites = [site for site, var in checkbox_vars.items() if var.get()]
    
    # Collect email addresses
    email_addresses = email_text.get("1.0", tk.END).strip().split('\n')
    
    # Scrape selected websites
    all_headlines = []
    for site in selected_sites:
        headlines = scrape_website(site)
        all_headlines.extend(headlines)
    
    # Create email content
    email_content = "Hello,\n\nHere are the popular news headlines:\n\n"
    email_content += "\n".join(all_headlines)
    
    # (Placeholder) Print the email content and recipient list to console
    print("Sending email to:", email_addresses)
    print("Email content:\n", email_content)
    
    # Simulate sending process with a delay
    root.after(2000, lambda: status_label.config(text="Sent"))

send_button = tk.Button(frame2, text="SEND", command=send_emails)
send_button.pack(pady=(10, 5))

# Status label
status_label = tk.Label(frame2, text="")
status_label.pack()

root.mainloop()
