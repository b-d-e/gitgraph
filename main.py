import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def fetch_graph(theme):
    """Downloads the fully rendered DOM content and saves it as a self-contained HTML file with specified theme."""
    URL = "https://jandee.vercel.app/b-d-e?footer=false"

    # Set up Selenium to use Chrome WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run headless for no GUI
    options.add_argument("--window-size=1920,430")  # Set window size to capture full page
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Define file name and background color based on the theme
    if theme == 'dark':
        file_name = 'dark.html'
        background_color = '#222529'
    else:
        file_name = 'light.html'
        background_color = '#EEEEEE'

    try:
        # Fetch the page
        driver.get(URL)

        # Give the page time to load fully
        time.sleep(2)  # Adjust if necessary

        # Inline all external resources and apply themes
        inline_resources_and_theme_script = f"""
        return (function() {{
            try {{
                function inlineCSS() {{
                    var stylesheets = Array.from(document.styleSheets);
                    stylesheets.forEach(function(sheet) {{
                        if (sheet.href) {{
                            try {{
                                var xhr = new XMLHttpRequest();
                                xhr.open('GET', sheet.href, false);
                                xhr.send(null);
                                if (xhr.status === 200) {{
                                    var style = document.createElement('style');
                                    style.textContent = xhr.responseText;
                                    document.head.appendChild(style);
                                    sheet.disabled = true;
                                }}
                            }} catch(e) {{
                                console.log('Error inlining CSS:', e);
                            }}
                        }}
                    }});
                }}

                function inlineImages() {{
                    var images = Array.from(document.images);
                    images.forEach(function(img) {{
                        if (img.src && !img.src.startsWith('data:')) {{
                            var canvas = document.createElement('canvas');
                            canvas.width = img.width;
                            canvas.height = img.height;
                            var ctx = canvas.getContext('2d');
                            ctx.drawImage(img, 0, 0);
                            img.src = canvas.toDataURL('image/png');
                        }}
                    }});
                }}

                // Apply theme background color
                document.body.style.backgroundColor = '{background_color}';

                inlineCSS();
                inlineImages();

                return new XMLSerializer().serializeToString(document);
            }} catch (e) {{
                return 'Error: ' + e.message;
            }}
        }})();
        """

        # Execute the script and get the inlined HTML
        inlined_html = driver.execute_script(inline_resources_and_theme_script)

        # Check if an error occurred
        if inlined_html is None or inlined_html.startswith('Error:'):
            print("JavaScript error occurred:")
            print(inlined_html)
        else:
            # Save the HTML to a file
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(inlined_html)

            print(f"Page saved as '{file_name}'")

    finally:
        # Close the browser
        driver.quit()

if __name__ == '__main__':
    fetch_graph('dark')
    fetch_graph('light')
