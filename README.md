
# 🤖 AI-Powered Resume Agent

A smart recruitment assistant built using **Python**, **Streamlit**, **LangChain**, and **OpenAI API**. This project analyzes resumes, extracts key information, and assists in intelligent job matching.

Deployed using **Docker**, **GitHub Actions**, and **AWS EC2**.

---

## 📌 Features

-  Upload and analyze resumes (PDF/Text)
-  Extract skills, education, and experience using LangChain & LLM
-  Use OpenAI API for intelligent response generation
-  Integrate job description parsing
-  PDF generation for recommendations
-  Streamlit-based web interface
-  Dockerized for smooth deployment
-  Deployed on AWS EC2 with CI/CD via GitHub Actions

---

##  Tech Stack

| Tool         | Purpose                          |
|--------------|----------------------------------|
| Python       | Core application logic           |
| Streamlit    | Interactive UI                   |
| LangChain    | LLM orchestration and chaining   |
| OpenAI API   | Resume parsing & NLP tasks       |
| Docker       | Containerization                 |
| GitHub Actions | CI/CD pipeline                 |
| AWS EC2      | App Hosting & Deployment         |
| Git + GitHub | Version control & collaboration  |
 PyPDF2        | PDF parsing & manipulation       |
---

## 📂 Project Structure

```

AI-powered-resume\_agent/
├── app.py                  # Main Streamlit App
├── agents.py               # LLM and LangChain logic
├── ui.py                   # Streamlit UI helpers
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker container config
├── .github/workflows/      # GitHub Actions CI/CD
│   └── deploy.yml
├── nginx/                  # (Optional) Reverse proxy configs
├── scripts/                # Deployment & helper scripts
├── .gitignore
└── README.md

````

---

##  Setup & Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/KiranRathod4/AI-powered-resume_agent.git
cd AI-powered-resume_agent
````

### 2. Create Virtual Environment & Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set Your OpenAI API Key

Create a `.env` file in the root:

```env
OPENAI_API_KEY=your-openai-key-here
```

Or set it as an environment variable:

```bash
export OPENAI_API_KEY=your-openai-key-here
```

### 4. Run the Streamlit App

```bash
streamlit run app.py
```

---

##  Run with Docker

### 1. Build Docker Image

```bash
docker build -t resume-agent .
```

### 2. Run Docker Container

```bash
docker run -e OPENAI_API_KEY=your-key -p 8501:8501 resume-agent
```

---

## Deployment on AWS EC2

### 1. Launch EC2 Instance (Ubuntu)

* Use t2.micro or higher
* Open ports: 22, 80, 8501

### 2. SSH into Instance

```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### 3. Install Dependencies

```bash
sudo apt update && sudo apt install docker.io git -y
sudo systemctl start docker
```

### 4. Clone Repository on EC2

```bash
git clone https://github.com/KiranRathod4/AI-powered-resume_agent.git
cd AI-powered-resume_agent
```

### 5. Build and Run Docker

```bash
docker build -t resume-agent .
docker run -d -p 80:8501 -e OPENAI_API_KEY=your-key resume-agent
```

Now visit `http://your-ec2-public-ip` in your browser.

---

## CI/CD with GitHub Actions

###  `.github/workflows/deploy.yml` (included)

Automatically deploy to EC2 on push to `main`. The workflow will:

* SSH into EC2
* Pull the latest code
* Rebuild and restart the Docker container

### 🔐 Required Secrets in GitHub

Go to **Repo → Settings → Secrets → Actions**, add:

* `EC2_HOST`
* `EC2_USER`
* `EC2_KEY` (your private SSH key)
* `OPENAI_API_KEY`

---

##  Future Enhancements

* Add MongoDB or PostgreSQL for user storage
* Enhance UI with animations and chatbot features
* Integrate with other AI models (e.g., sentiment analysis)

---

## License

This project is licensed under the **MIT License**.

---

## Author

Created with ❤️ by [Kiran Rathod](https://github.com/KiranRathod4)

