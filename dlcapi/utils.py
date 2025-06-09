import os
import deeplabcut

def run_dlc_pipeline(video_rel_path: str, model_name: str = "superanimal_quadruped", pcutoff: float = 0.15):
    abs_path = os.path.abspath(video_rel_path)
    videotype = os.path.splitext(abs_path)[1]
    scale_list = []

    deeplabcut.video_inference_superanimal(
    [abs_path],
    model_name,
    model_name="hrnet_w32",
    detector_name="fasterrcnn_resnet50_fpn_v2",
    videotype=videotype,
    video_adapt=True,
    scale_list=scale_list,
    pcutoff=pcutoff,
)
    video_name = os.path.splitext(abs_path)[0]
    labelled_video_path = f"{video_name}_{model_name}_hrnetw32_labeled_after_adapt.mp4"
    print(f"Labelled video saved at: {labelled_video_path}")
    
    return {
        "message": "Video processing completed",
        "input_video": abs_path,
        "output_dir": os.path.dirname(abs_path),
    }


