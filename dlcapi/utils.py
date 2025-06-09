import os
import tempfile
import requests
import deeplabcut
from urllib.parse import urlparse

SUPABASE_URL = "https://nidduqpsocsudhgdwlom.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5pZGR1cXBzb2NzdWRoZ2R3bG9tIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk0NzU4ODksImV4cCI6MjA2NTA1MTg4OX0.519vPiblwbD-wIhBY2VcpGfg-IUrGrkaAIG8tbcV9cs"
SUPABASE_BUCKET = "dlcservice/horse-videos-processed"

def download_from_supabase(object_path: str, destination_path: str):
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
    }
    res = requests.get(
        f"{SUPABASE_URL}/storage/v1/object/{object_path}",
        headers=headers,
        stream=True,
    )
    if res.status_code == 200:
        with open(destination_path, "wb") as f:
            for chunk in res.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        raise Exception(f"Failed to download video: {res.status_code}, {res.text}")

def upload_to_supabase(file_path: str, dest_path: str) -> bool:
    with open(file_path, "rb") as f:
        res = requests.post(
            f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{dest_path}",
            headers={
                "apikey": SUPABASE_API_KEY,
                "Authorization": f"Bearer {SUPABASE_API_KEY}",
                "Content-Type": "application/octet-stream",
            },
            data=f.read()
        )
    return res.ok

def run_dlc_pipeline(supabase_object_url: str, model_name: str = "superanimal_quadruped", pcutoff: float = 0.15):
    parsed = urlparse(supabase_object_url)
    object_path = parsed.path.replace("/storage/v1/object/", "", 1)

    with tempfile.TemporaryDirectory() as tmpdir:
        input_filename = os.path.basename(object_path)
        local_input_path = os.path.join(tmpdir, input_filename)

        # 1. Download input video
        download_from_supabase(object_path, local_input_path)

        # 2. Run DeepLabCut
        deeplabcut.video_inference_superanimal(
            [local_input_path],
            model_name,
            model_name="hrnet_w32",
            detector_name="fasterrcnn_resnet50_fpn_v2",
            videotype=os.path.splitext(local_input_path)[1],
            video_adapt=True,
            video_adapt_batch_size=4,
            scale_list=[],
            pcutoff=pcutoff,
        )

        # 3. Determine output labeled file path
        video_base = os.path.splitext(local_input_path)[0]
        labeled_path = f"{video_base}_{model_name}_hrnetw32_labeled_after_adapt.mp4"
        output_name = os.path.basename(labeled_path)
        output_dest_path = object_path.rsplit("/", 1)[0] + "/" + output_name

        # 4. Upload labeled video
        success = upload_to_supabase(labeled_path, output_dest_path)

        # 5. Return results
        return {
            "message": "Video processed and uploaded",
            "filename": input_filename,
            "file_path": f"/{SUPABASE_BUCKET}/{output_dest_path}",
            "file_size": os.path.getsize(labeled_path),
            "uploaded": success
        }