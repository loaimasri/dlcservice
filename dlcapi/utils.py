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

def run_dlc_pipeline(file_name:str,supabase_object_url: str, model_name: str = "superanimal_quadruped", pcutoff: float = 0.15):
    parsed = urlparse(supabase_object_url)
    object_path = parsed.path.replace("/storage/v1/object/", "", 1)

    with tempfile.TemporaryDirectory() as tmpdir:
        input_filename = os.path.basename(object_path)
        local_input_path = os.path.join(tmpdir, input_filename)
        
        # 1. Download input video
        download_from_supabase(object_path, local_input_path)
        
        # 2. Prepare video extension (without dot)
        ext = os.path.splitext(local_input_path)[1]
        videotype = ext[1:] if ext else 'mp4'  # Handle no-extension case
        
        # 3. Run DeepLabCut with explicit output directory
        deeplabcut.video_inference_superanimal(
            [local_input_path],
            model_name,
            model_name="hrnet_w32",
            detector_name="fasterrcnn_resnet50_fpn_v2",
            videotype=videotype,
            video_adapt=True,
            video_adapt_batch_size=4,
            scale_list=[],
            pcutoff=pcutoff,
            dest_folder=tmpdir,  # Use tmpdir for outputs
        )
        
        # 4. Find labeled video file (flexible naming)
        base_name = os.path.splitext(input_filename)[0]
        
        # Possible filename patterns
        possible_patterns = [
            f"{base_name}_{model_name}_labeled.mp4",  # With model name
            f"{base_name}_labeled.mp4",              # Without model name
            f"{base_name}_{model_name}_labeled.avi",  # AVI format
            f"{base_name}_labeled.avi"
        ]
        
        labeled_path = None
        for pattern in possible_patterns:
            candidate = os.path.join(tmpdir, pattern)
            if os.path.exists(candidate):
                labeled_path = candidate
                break
        
        # Fallback: Search for any labeled video
        if not labeled_path:
            labeled_files = [f for f in os.listdir(tmpdir) 
                            if "labeled" in f and (f.endswith(".mp4") or f.endswith(".avi"))]
            if labeled_files:
                labeled_path = os.path.join(tmpdir, labeled_files[0])
        
        if not labeled_path:
            raise Exception("Labeled video file not found after processing.")
        
        # 5. Upload and return results
        output_dest_path = f"{object_path.rsplit('/', 1)[0]}/{os.path.basename(labeled_path)}"
        success = upload_to_supabase(labeled_path, output_dest_path)
        
        return {
            "message": "Video processed and uploaded",
            "filename": file_name,
            "file_path": f"horse-videos-processed/{output_dest_path}",
            "mime_type": "video/mp4" if labeled_path.endswith(".mp4") else "video/avi",
            "file_size": os.path.getsize(labeled_path),
            "uploaded": success
        }