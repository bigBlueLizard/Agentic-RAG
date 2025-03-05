# Dependencies
## Uvicorn
We are using uvicorn to run our fastapi api which enables us to access our RAG pipeline

# Deployment
We are using Docker for Deployment to Avoid Dependency Issues

# Setup using Docker

Here's a Step-by-Step Guide to run our Setup using Docker:

1. Open Docker Desktop and navigate in its terminal to reach the directory containing the Dockerfile provided along with the code.
2. Run the following command in the terminal:

    ```bash
    docker build -t my-pathway-app .
    ```

3. After completing building the image, open VS Code.
4. Install the following two VS Code Extensions:
    - Docker
    - Dev Containers

5. Press `Ctrl+Shift+P` and run the following command:

    ```
    Dev Containers: Reopen in Container
    ```

6. After the container is successfully started, create a new terminal and run the following command:

    ```bash
    python retrieval_server.py
    ```

   and let it run.

7. Then create a new terminal and execute the following command:

    ```bash
    pip install uvicorn
    ```

8. After installing uvicorn execute the following command:

    ```bash
    uvicorn app:app --reload --port 5000
    ```

9. To access our app, go to the URL:

    ```
    localhost:5000/docs
    ```

