import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import webbrowser

def load_data():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        try:
            df = pd.read_csv(file_path)
            messagebox.showinfo("Success", "File loaded successfully!")
            return df
        except FileNotFoundError:
            messagebox.showerror("Error", "File not found.")
        except pd.errors.EmptyDataError:
            messagebox.showerror("Error", "No data.")
        except pd.errors.ParserError:
            messagebox.showerror("Error", "Parse error.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
    else:
        messagebox.showwarning("Warning", "No file selected.")
    return None

def analyze_data(df):
    # Prompt the user to select a folder to save the images
    root = tk.Tk()
    root.withdraw()
    save_folder = filedialog.askdirectory()
    if not save_folder:
        messagebox.showwarning("Warning", "No folder selected.")
        return

    # Sentiment Analysis
    analyzer = SentimentIntensityAnalyzer()
    df['sentiment'] = df['tweet_text'].apply(lambda x: analyzer.polarity_scores(x)['compound'])
    df['sentiment_category'] = df['sentiment'].apply(lambda x: 'Positive' if x > 0 else ('Negative' if x < 0 else 'Neutral'))

    # Summary Statistics
    sentiment_counts = df['sentiment_category'].value_counts()
    print(sentiment_counts)

    # Plotting Sentiment Distribution
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='sentiment_category', order=['Positive', 'Neutral', 'Negative'], palette="viridis")
    plt.title('Sentiment Distribution')
    plt.xlabel('Sentiment')
    plt.ylabel('Count')
    sentiment_distribution_img_path = os.path.join(save_folder, 'sentiment_distribution.png')
    plt.savefig(sentiment_distribution_img_path)
    plt.close()

    # Most Positive and Negative Tweets
    most_positive_tweet = df.loc[df['sentiment'].idxmax()]['tweet_text']
    most_negative_tweet = df.loc[df['sentiment'].idxmin()]['tweet_text']

    # Creating HTML Report
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sentiment Analysis Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f0f0f0;
            }}
            h1 {{
                text-align: center;
                color: #333;
            }}
            .image-container, .tweet-container {{
                display: none;
                text-align: center;
                margin-bottom: 20px;
            }}
            img {{
                width: 80%;
                height: auto;
                border: 2px solid #ccc;
                box-shadow: 2px 2px 12px #aaa;
                margin-bottom: 20px;
            }}
            .tweet-container {{
                background-color: #fff;
                padding: 20px;
                box-shadow: 2px 2px 12px #aaa;
                border-radius: 5px;
                margin: 10px auto;
                width: 80%;
            }}
            .tweet-container p {{
                font-size: 1.1em;
                color: #555;
            }}
            .button {{
                display: inline-block;
                padding: 10px 20px;
                font-size: 16px;
                cursor: pointer;
                text-align: center;
                text-decoration: none;
                outline: none;
                color: #fff;
                background-color: #4CAF50;
                border: none;
                border-radius: 15px;
                box-shadow: 0 9px #999;
                margin: 5px;
            }}
            .button:hover {{background-color: #3e8e41}}
            .button:active {{
                background-color: #3e8e41;
                box-shadow: 0 5px #666;
                transform: translateY(4px);
            }}
            .emoji {{
                font-size: 2em;
                margin-top: 10px;
            }}
            .balloon-container {{
                position: absolute;
                bottom: 0;
                width: 100%;
                height: 200px;
                pointer-events: none;
                z-index: -1;
            }}
            .balloon {{
                position: absolute;
                bottom: -100px;
                width: 50px;
                height: 70px;
                background-color: red;
                border-radius: 50%;
                animation: riseUp 7s infinite;
            }}
            .balloon:nth-child(2) {{ left: 20%; animation-delay: 2s; }}
            .balloon:nth-child(3) {{ left: 40%; animation-delay: 4s; }}
            .balloon:nth-child(4) {{ left: 60%; animation-delay: 6s; }}
            .balloon:nth-child(5) {{ left: 80%; animation-delay: 8s; }}

            @keyframes riseUp {{
                0% {{ bottom: -100px; opacity: 0; }}
                50% {{ opacity: 1; }}
                100% {{ bottom: 100%; opacity: 0; }}
            }}
        </style>
    </head>
    <body>
        <h1>Sentiment Analysis Report</h1>
        <div style="text-align: center;">
            <button class="button" onclick="showSection('image-container')">Sentiment Distribution</button>
            <button class="button" onclick="showSection('positive-tweet')">Most Positive Tweet</button>
            <button class="button" onclick="showSection('negative-tweet')">Most Negative Tweet</button>
        </div>
        <div id="image-container" class="image-container">
            <h2>Sentiment Distribution</h2>
            <img src="{sentiment_distribution_img_path}" alt="Sentiment Distribution">
            <div class="balloon-container">
                <div class="balloon"></div>
                <div class="balloon"></div>
                <div class="balloon"></div>
                <div class="balloon"></div>
                <div class="balloon"></div>
            </div>
        </div>
        <div id="positive-tweet" class="tweet-container">
            <h2>Most Positive Tweet</h2>
            <p>"{most_positive_tweet}"</p>
            <div class="emoji">👍</div>
        </div>
        <div id="negative-tweet" class="tweet-container">
            <h2>Most Negative Tweet</h2>
            <p>"{most_negative_tweet}"</p>
            <div class="emoji">👎</div>
        </div>
        <script>
            function showSection(sectionId) {{
                document.getElementById('image-container').style.display = 'none';
                document.getElementById('positive-tweet').style.display = 'none';
                document.getElementById('negative-tweet').style.display = 'none';
                document.getElementById(sectionId).style.display = 'block';

                if (sectionId === 'image-container') {{
                    let balloons = document.querySelectorAll('.balloon');
                    balloons.forEach((balloon) => {{
                        balloon.style.animation = 'none';
                        balloon.offsetHeight;  // Trigger reflow
                        balloon.style.animation = '';
                    }});
                }}
            }}
        </script>
    </body>
    </html>
    """

    html_file_path = os.path.join(save_folder, 'sentiment_analysis_report.html')
    with open(html_file_path, 'w', encoding='utf-8') as html_file:  # Ensure UTF-8 encoding
        html_file.write(html_content)

    # Open the HTML file in a web browser
    webbrowser.open(html_file_path)

if __name__ == "__main__":
    df = load_data()
    if df is not None:
        analyze_data(df)
    else:
        print("No data to analyze.")
