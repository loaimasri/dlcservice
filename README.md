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

5. **For Production**: Use supervisord to run the service in production mode:

   ```bash
   supervisord -c supervisord.conf
   ```

   - Note that you need to have `supervisord` installed and configured properly.

   ```sh
   pip install supervisor
   ```

### Note

When you trying to deploy the service, you should increse the timeout in the `gunicorn` command to avoid timeout issues, for example:

```bash
gunicorn dlcservice.wsgi:application --bind 0.0.0.0:8000 --timeout 600
```
