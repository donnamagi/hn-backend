# Hacker News 2.0

The objective of this capstone project was to create an improved version of Hacker News. This is the backend repository for the project. [Frontend repository is here](https://github.com/donnamagi/hn-front).

# Application architecture

![Flowchart - Application architecture](https://github.com/donnamagi/hn-backend/assets/79452941/6898b9ee-3973-4e32-9efa-e92ce6cea26b)

### Tech Stack

- **Frontend**: Built with **Next.js** and hosted on **Vercel**. Allowed me to work with both server-side rendered content and React components for a modern web UI.
- **Backend**: Developed using **FastAPI** and Python, which facilitated data aggregation and working with the Zilliz SDK (a vector database common in data science)
- **Databases**:
  - **PostgreSQL**: Stores structured data such as article metadata and Hacker News state backups.
  - **Zilliz**: Manages vector data for embedded semantic context, enabling similarity search.
 
In this case, a lot of the application logic sits in the frontend. This enabled me to render faster visual updates for the user without complicating the communication between client and server, and made UX-driven development quicker. However, the backend was still crucial for its scheduled processing tasks and communication with external dependencies.

### Data aggregation methodology
A systematic process was employed to collect and process articles from Hacker News. The methodology involved:


| **Step**                | **Description**                                                                                                                                                   |
|-------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Daily Article Retrieval** | The top 30 trending and best articles from Hacker News were retrieved on a daily basis.                                                                           |
| **Metadata Collection**     | Associated metrics, comments, and other relevant data were extracted from Hacker News.                                                                            |
| **Content Acquisition**     | The content of each article was retrieved from their respective source.                                                                                           |
| **Content Processing**      | The article content was cleaned and synthesized using Llama 3-70b, a Large Language Model (LLM).                                                                  |
| **Entity Extraction**       | Mentions of organizations and topics (referred to as "keywords" in the dataset) were extracted from the processed content.                                        |
| **Embedding Generation**    | Vector embeddings were created from the processed content, enabling further analysis and modeling.                                                                |
| **Data Storage**            | The processed data was stored for further analysis and visualization.                                                                                            |


#### Entity Relationship Diagram
![Entity Relationship Diagram - ER diagram-2](https://github.com/user-attachments/assets/bd47541a-2729-48b4-9e56-76b181274b5b)

### API Dependencies
- [Hacker News API](https://github.com/HackerNews/API): Fetches data for content aggregation, and helps maintain consistency with the real-time content on Hacker News.
-  [Voyage AI API](https://www.voyageai.com): Provides embeddings for semantic search and recommendations. Voyage was, at the time of this project, the industry leader in large text embeddings. I chose to integrate their API as part of my data preprocessing workflow. 
- [Groq API](https://wow.groq.com/why-groq/): Handles text synthesis for summarizing articles.

### Sentry

Both the front- and backend are using the Sentry SDK to allow simplified error management and performance analysis. This allowed me as the developer to be notified when scripts failed or queries were getting slow.

### Deployment

The backend was containerized and deployed on AWS, using [AWS Elastic Beanstalk](https://aws.amazon.com/elasticbeanstalk/). Using Elastic Beanstalk (and their CLI tooling) allowed for simple and efficient deployment cycles, and facilitated processes like health checks and graceful handling of failed deploys. 

I also utilized [AWS RDS (PostgreSQL)](https://aws.amazon.com/rds/) for managing the database. As this was also an AWS service, I was able to host them in the same 'Virtual Private Cloud' (VPC) which facilitated security and communication speed between the backend and the database.

# Development Setup

This is a guide on how to set up and run this FastAPI project using Uvicorn (an ASGI server). As mentioned above, many external dependencies are included and need to be (re)configured for the app to successfully start.

## Prerequisites

Ensure you have the following installed:
- Python 3.10+
- pip (Python package installer)

## Installation

Follow these steps to get your development environment set up:

1. **Clone the Repository**

   Clone this repository to your local machine using `git clone`.

   ```
   git clone https://github.com/your-username/your-project-name.git
   ```

2. **Create a Virtual Environment**

   Navigate to the project directory and create a virtual environment.

   ```
   cd your-project-name
   python -m venv venv
   ```

3. **Activate the Virtual Environment**

   - On Windows:
     ```
     .\venv\Scripts\activate
     ```

   - On Unix or MacOS:
     ```
     source venv/bin/activate
     ```

4. **Install Dependencies**

   Install all the required packages using pip.

   ```
   pip install -r requirements.txt
   ```

## External dependencies

This project has external dependencies that need to be set up and configured in order to successfully run the code. All services are free to use (as of July 2024).

You might want to start by creating an `.env` file based on `.env.example`

### Zilliz - vector DB

This project setup heavily depends on a cloud vector database called [Zilliz](https://zilliz.com). Successfully running the app requires [setting up Zilliz](https://docs.zilliz.com/docs/quick-start) and adding the credentials in `.env`.

### PostgreSQL – relational DB

This code talks directly to a hosted database on AWS RDS (a t3.micro instance, the free tier option).

Necessary setup on AWS is explained in [this setup guide](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_GettingStarted.CreatingConnecting.PostgreSQL.html#CHAP_GettingStarted.Connecting.PostgreSQL). After obtaining the necessary credentials from the AWS Console, set the values in `.env` and you should be good to go.

However – there are many other ways to work with a PostgreSQL database. **Using AWS as DB host is not required** as long as you configure the credentials correctly in `.env`

### Voyage - embeddings 

Obtain an API key [here](https://docs.voyageai.com/docs/api-key-and-installation).

### Llama 3 - text synthesis

To clean and synthesize text coming from third party websites, I found [Llama 3-70B](https://llama.meta.com/llama3/), an open-source LLM, to work best. This could be handled with a third-party API, or a locally running model. 

**To run it locally:** Install Ollama ([instructions](https://github.com/ollama/ollama)), and sequentially [following this guide](https://ollama.com/library/llama3) for setting up Llama to run on a local port.

**To call an API**: Depending on your hardware and internet connection, this is most likely the faster option. [groq.com](https://groq.com) offers free API calls to the same Llama model with generous rate limits. 

### Sentry

As a way to monitor performance and catch production errors, this project has integrated [Sentry](https://sentry.io/welcome/). After getting your DSN from their setup, add it to the `.env`

## Running the Application

You can run the application using Uvicorn with the following command:

```
uvicorn app.main:app --reload  
```

## Accessing the Application

- Visit [http://localhost:8000](http://localhost:8000) in your web browser to access the backend.
- Access the automatic interactive API documentation generated by FastAPI at [http://localhost:8000/docs](http://localhost:8000/docs).
