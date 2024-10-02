import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def fetch_graph_and_save_variants():
    """Downloads the fully rendered DOM content once and saves both dark and light variants as self-contained HTML files."""
    URL = "https://jandee.vercel.app/b-d-e?footer=false&tz=Europe/London"

    # Set up Selenium to use Chrome WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run headless for no GUI
    options.add_argument("--window-size=1920,430")  # Set window size to capture full page
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Define the file names and background colors for the two themes
    dark_background_color = '#222529'
    light_background_color = '#EEEEEE'
    dark_file_name = 'dark.html'
    light_file_name = 'light.html'

    # Define color schemes for the graph squares (multi-level)
    light_mode_colors = {
        # '--color-calendar-graph-day-bg': '#ebedf0',    # Very light background for the grid
        '--color-calendar-graph-day-L1-bg': '#D0E8F2',  # Lightest blue
        '--color-calendar-graph-day-L2-bg': '#A9D6EB',  # Medium blue
        '--color-calendar-graph-day-L3-bg': '#82C4E3',  # Darker blue
        '--color-calendar-graph-day-L4-bg': '#5BB2DB',  # Darkest blue
        '--color-calendar-graph-day-border': 'rgba(27,31,35,.06)'
    }

    dark_mode_colors = {
        '--color-calendar-graph-day-bg': '#222',          # Dark background for the grid
        '--color-calendar-graph-day-L1-bg': '#E8A67B',    # Muted light orange
        '--color-calendar-graph-day-L2-bg': '#D67C4E',    # Muted medium orange
        '--color-calendar-graph-day-L3-bg': '#BF5F34',    # Muted darker orange
        '--color-calendar-graph-day-L4-bg': '#A3461A',    # Muted darkest orange
        '--color-calendar-graph-day-border': 'rgba(27,31,35,.06)'
    }

    try:
        # Fetch the page
        driver.get(URL)

        # Give the page time to load fully
        time.sleep(2)  # Adjust if necessary

        # Inline all external resources
        inline_resources_script = """
        return (function() {
            try {
                function inlineCSS() {
                    var stylesheets = Array.from(document.styleSheets);
                    stylesheets.forEach(function(sheet) {
                        if (sheet.href) {
                            try {
                                var xhr = new XMLHttpRequest();
                                xhr.open('GET', sheet.href, false);
                                xhr.send(null);
                                if (xhr.status === 200) {
                                    var style = document.createElement('style');
                                    style.textContent = xhr.responseText;
                                    document.head.appendChild(style);
                                    sheet.disabled = true;
                                }
                            } catch(e) {
                                console.log('Error inlining CSS:', e);
                            }
                        }
                    });
                }

                function inlineImages() {
                    var images = Array.from(document.images);
                    images.forEach(function(img) {
                        if (img.src && !img.src.startsWith('data:')) {
                            var canvas = document.createElement('canvas');
                            canvas.width = img.width;
                            canvas.height = img.height;
                            var ctx = canvas.getContext('2d');
                            ctx.drawImage(img, 0, 0);
                            img.src = canvas.toDataURL('image/png');
                        }
                    });
                }

                inlineCSS();
                inlineImages();

                return new XMLSerializer().serializeToString(document);
            } catch (e) {
                return 'Error: ' + e.message;
            }
        })();
        """

        # Execute the script to inline resources
        inlined_html = driver.execute_script(inline_resources_script)

        # Check for errors during inlining
        if inlined_html is None or inlined_html.startswith('Error:'):
            print("JavaScript error occurred during inlining:")
            print(inlined_html)
            return

        # Save the light mode version first with blue shades
        driver.execute_script(f"document.body.style.backgroundColor = '{light_background_color}';")
        driver.execute_script(f"""
        (function() {{
            var root = document.documentElement;
            {''.join([f"root.style.setProperty('{key}', '{value}');" for key, value in light_mode_colors.items()])}
        }})();
        """)
        light_html = driver.execute_script("return new XMLSerializer().serializeToString(document);")

        with open(light_file_name, 'w', encoding='utf-8') as f:
            f.write(light_html)
        print(f"Page saved as '{light_file_name}'")

        # Now apply dark mode changes with muted orange shades
        driver.execute_script(f"document.body.style.backgroundColor = '{dark_background_color}';")
        driver.execute_script(f"""
        (function() {{
            var root = document.documentElement;
            {''.join([f"root.style.setProperty('{key}', '{value}');" for key, value in dark_mode_colors.items()])}
        }})();
        """)
        dark_html = driver.execute_script("return new XMLSerializer().serializeToString(document);")

        # Save the dark mode version
        with open(dark_file_name, 'w', encoding='utf-8') as f:
            f.write(dark_html)
        print(f"Page saved as '{dark_file_name}'")

    finally:
        # Close the browser
        driver.quit()

if __name__ == '__main__':
    fetch_graph_and_save_variants()
