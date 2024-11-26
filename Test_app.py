from flask import Flask, request, jsonify, render_template_string
import wikipediaapi

app = Flask(__name__)
wiki = wikipediaapi.Wikipedia('en')  # Set the language to English

# HTML, CSS, and JavaScript embedded into Python
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wikipedia Search</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f9;
            color: #333;
        }
        header {
            background-color: #6200ea;
            color: white;
            padding: 10px;
            text-align: center;
        }
        main {
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
        }
        input {
            width: calc(100% - 22px);
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        button {
            background-color: #6200ea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #3700b3;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
    </style>
</head>
<body>
    <header>
        <h1>Wikipedia Search</h1>
    </header>
    <main>
        <input type="text" id="searchInput" placeholder="Enter a search term..." />
        <button onclick="searchWiki()">Search</button>
        <div id="result" class="result" style="display: none;"></div>
    </main>
    <script>
        async function searchWiki() {
            const query = document.getElementById('searchInput').value;
            const resultDiv = document.getElementById('result');
            resultDiv.style.display = 'none';
            
            if (!query.trim()) {
                alert("Please enter a search term.");
                return;
            }

            const response = await fetch('/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });

            const data = await response.json();
            if (data.success) {
                resultDiv.innerHTML = `<h2>${data.title}</h2><p>${data.summary}</p>`;
            } else {
                resultDiv.innerHTML = `<p>${data.error}</p>`;
            }
            resultDiv.style.display = 'block';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get('query')
    
    if not query:
        return jsonify({'success': False, 'error': 'Invalid query'})
    
    page = wiki.page(query)
    if page.exists():
        return jsonify({'success': True, 'title': page.title, 'summary': page.summary[:500] + '...'})
    else:
        return jsonify({'success': False, 'error': 'Page not found'})

if __name__ == '__main__':
    app.run(debug=True)