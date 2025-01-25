```markdown
# Glasses3D Generative AI System

This project is an advanced AI-driven system that generates **3D models of glasses** from product images and descriptions. It uses a combination of web scraping, AI analysis, and 3D modeling to automate the entire process.

---

## 🚀 Key Features

- **Automated Data Collection**: Scrapes product details and images from websites using Playwright and BeautifulSoup.
- **AI-Powered Analysis**: Uses DeepSeek-R1 to analyze images and extract technical specifications (e.g., material, measurements, branding).
- **3D Model Generation**: Creates high-quality 3D models using FAL Rodin API.
- **Error-Resilient Workflow**: Built with Pydantic for data validation and retry mechanisms for API calls.

---

## 🛠️ How It Works

The system works in **three main layers**:

1. **Data Collection Layer**  
   - Scrapes product details and images from websites.
   - Cleans and organizes data using LangChain and BeautifulSoup.

2. **AI Processing Layer**  
   - Analyzes images and text using DeepSeek-R1.
   - Generates detailed prompts for 3D modeling.

3. **Data Processing Layer**  
   - Creates 3D models using FAL Rodin API.
   - Validates data and ensures accuracy using Pydantic.

---

## 📂 File Structure

```
Glasses3D/
├── main.py                 # Main script to run the pipeline
├── model_processor.py      # Handles 3D model generation using FAL Rodin API
├── deepseek_client.py      # Integrates DeepSeek-R1 for AI analysis
├── config_generator.py     # Generates configuration for 3D modeling
├── prompt_generator.py     # Creates detailed prompts for the AI
├── product_scraper.py      # Scrapes product details and images
└── README.md               # This file
```

---

## 🧰 Technologies Used

- **Web Scraping**: Playwright, BeautifulSoup
- **AI Analysis**: DeepSeek-R1
- **3D Modeling**: FAL Rodin API
- **Data Validation**: Pydantic
- **Automation**: LangChain, Selenium

---

## 🚨 Limitations

1. **Single-View Constraints**:  
   - The system uses only one or two images, so complex details (e.g., curved lenses) may not be perfectly recreated.

2. **Material Ambiguity**:  
   - It can’t always determine if a material is shiny, matte, or translucent from a single image.

3. **Economic Constraints**:  
   - Training a custom AI model for this task would be expensive, so the system relies on existing tools.

---

## 🛠️ Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install playwright beautifulsoup4 langchain pydantic selenium
   ```

2. **Set Up API Keys**:
   - Add your DeepSeek and FAL API keys to a `.env` file:
     ```
     DEEPSEEK_API_KEY=your_api_key
     FAL_API_KEY=your_api_key
     ```

3. **Run the Pipeline**:
   ```bash
   python main.py
   ```

---

## 📊 Example Workflow

1. **Input**: Provide a product URL (e.g., Warby Parker glasses).
2. **Scraping**: The system scrapes the website for product details and images.
3. **AI Analysis**: DeepSeek-R1 analyzes the images and generates a detailed description.
4. **3D Modeling**: FAL Rodin creates a 3D model based on the description.
5. **Output**: Download the 3D model in GLB format.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Playwright**: For browser automation.
- **DeepSeek**: For AI-powered image and text analysis.
- **FAL Rodin**: For 3D model generation.
```
