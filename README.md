# DLC Service

## A Django-based service for managing DLC (Deep Learning Container) applications

### Exposed Endpoints

- `POST /api/run/`: Runs a DLC model on a specified video.
  - **Request Body**:
    - `video_path`: Path to the video file.
    - `model`: Name of the model to use (e.g., `superanimal_quadruped`).
    - `pcutoff`: Probability cutoff for predictions (default is `0.15`).

### Running the Service

1. **Install Conda**: Ensure you have Conda installed on your system.
2. **Create a Conda Environment**:

   ```bash
   conda create -f DEEPLABCUT.yml -n dlcservice
   ```

3. **Activate the Environment**:

   ```bash
    conda activate dlcservice
    ```

4. **Run the Service**:

   ```bash
   python manage.py runserver
   ```

### Note

When you trying to deploy the service, you should increse the timeout in the `gunicorn` command to avoid timeout issues, for example:

```bash
gunicorn dlcservice.wsgi:application --timeout 600 # where 600 is the timeout in seconds
```
