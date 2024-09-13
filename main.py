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
    # Disable web security to bypass CORS (for testing purposes)
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Fetch the page
        driver.get(URL)

        # Give the page time to load fully
        time.sleep(5)  # Adjust if necessary

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

                // Optionally inline scripts, but be cautious
                function inlineScripts() {
                    var scripts = Array.from(document.scripts);
                    scripts.forEach(function(script) {
                        if (script.src) {
                            try {
                                var xhr = new XMLHttpRequest();
                                xhr.open('GET', script.src, false);
                                xhr.send(null);
                                if (xhr.status === 200) {
                                    var inlineScript = document.createElement('script');
                                    inlineScript.textContent = xhr.responseText;
                                    script.parentNode.replaceChild(inlineScript, script);
                                }
                            } catch(e) {
                                console.log('Error inlining script:', e);
                            }
                        }
                    });
                }

                inlineCSS();
                inlineImages();
                // inlineScripts(); // Uncomment if necessary, but be cautious with scripts

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

