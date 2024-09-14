import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def fetch_graph():
    """Downloads the fully rendered DOM content and saves it as a self-contained HTML file."""
    URL = "https://jandee.vercel.app/b-d-e?footer=false"

    # Set up Selenium to use Chrome WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run headless for no GUI
    options.add_argument("--window-size=1920,430")  # Set window size to capture full page
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Fetch the page
        driver.get(URL)

        # Give the page time to load fully
        time.sleep(5)  # Adjust if necessary

        # Inline all external resources and add themes
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

                function addThemes() {
                    var themeStyle = document.createElement('style');
                    themeStyle.textContent = `
                    [data-theme=light] {
                        color-scheme: light;
                        --bg: #EEEEEE;
                        --bg-light: #CBCDCD;
                        --text: #41474E;
                        --text-light: #646868;
                        --accent: #D26878;
                        --accent-light: #e08f67;
                        --accent-text: var(--bg);
                        --border: #646868;
                        --link: #5690AF;
                    }

                    [data-theme=dark] {
                        color-scheme: dark;
                        --bg: #222529;
                        --bg-light: #464949;
                        --text: #D6D6D6;
                        --text-light: #DBD5BC;
                        --accent: #78B6AD;
                        --accent-light: #87C9E5;
                        --accent-text: var(--bg);
                        --border: #DBD5BC;
                        --link: #E2AEA2;
                    }
                    `;
                    document.head.appendChild(themeStyle);
                    document.documentElement.setAttribute('data-theme', 'light');  // Set the default theme to light
                }

                inlineCSS();
                inlineImages();
                addThemes();

                return new XMLSerializer().serializeToString(document);
            } catch (e) {
                return 'Error: ' + e.message;
            }
        })();
        """

        # Execute the script and get the inlined HTML
        inlined_html = driver.execute_script(inline_resources_script)

        # Check if an error occurred
        if inlined_html is None or inlined_html.startswith('Error:'):
            print("JavaScript error occurred:")
            print(inlined_html)
        else:
            # Save the HTML to a file
            with open('git_commit_graph.html', 'w', encoding='utf-8') as f:
                f.write(inlined_html)

            print("Page saved as 'git_commit_graph.html'")

    finally:
        # Close the browser
        driver.quit()

if __name__ == '__main__':
    fetch_graph()
