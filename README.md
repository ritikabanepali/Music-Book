# Music Book: A Spotify Album Review App

Music Book is a full-stack web application that allows users to browse the extensive Spotify music catalog, rate their favorite albums, and write and share reviews with other users. It leverages the Spotify Web API for album and artist data and provides a custom backend for user management and review storage.

## Features

* **User Authentication**: Secure user registration and login system using JWT (JSON Web Tokens).
* **Spotify Integration**: Users can connect their Spotify account to unlock browsing and searching features.
* **Album and Artist Search**: Search the entire Spotify catalog for any artist or album.
* **Browse New Releases**: View a list of the latest album releases directly from Spotify.
* **Rate and Review**: Users can leave a rating (1-5 stars) and a text comment on any album.
* **Combined Album View**: Album pages display official Spotify data (cover art, tracklist) combined with user-generated reviews from the app's database.
* **Personal Review Page**: A dedicated page for users to view a list of all the reviews they have personally written.

---

## Technology Stack

This project is a full-stack application with a decoupled frontend and backend.

* **Backend**:
    * **Framework**: Django & Django REST Framework
    * **Database**: PostgreSQL
    * **Authentication**: Simple JWT for token-based auth
* **Frontend**:
    * **Library**: React
    * **API Client**: Axios
    * **Routing**: React Router
* **Containerization**:
    * Docker & Docker Compose

---

## Getting Started

### Prerequisites

* Docker and Docker Compose installed on your machine.
* A Spotify Developer account with an application created to get your Client ID and Client Secret.

### Setup and Installation

1.  **Clone the Repository**
    ```bash
    git clone <your-repository-url>
    cd <your-project-directory>
    ```

2.  **Configure Environment Variables**
    In the project's root directory, create a `.env` file by copying the example file:
    ```bash
    cp .env.example .env
    ```
    Now, open the `.env` file and fill in your specific credentials:
    * `SECRET_KEY`: Your Django secret key.
    * `SPOTIFY_CLIENT_ID`: Your client ID from the Spotify Developer Dashboard.
    * `SPOTIFY_CLIENT_SECRET`: Your client secret from the Spotify Developer Dashboard.
    * Ensure `SPOTIFY_REDIRECT_URI` is set to `http://127.0.0.1:8000/api/spotify/callback/` and that this exact URL is also added to your application's settings in the Spotify Developer Dashboard.

3.  **Build and Run the Application**
    From the project's root directory, run the following command to build the images and start all the services (backend, frontend, and database):
    ```bash
    docker-compose up --build
    ```

4.  **Run Database Migrations**
    Once the containers are running, open a **new terminal window** and execute the following command to set up the database schema:
    ```bash
    docker-compose exec web python manage.py migrate
    ```

5.  **Create a Superuser**
    To access the Django admin panel and create test users, run:
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```
    Follow the prompts to create your admin account.

### Accessing the Application

* **Frontend (React App)**: Open your browser and navigate to `http://localhost:3000`
* **Backend API**: The API is accessible at `http://localhost:8000/api/`
* **Django Admin**: Access the admin panel at `http://localhost:8000/admin/`
