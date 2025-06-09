from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import run_dlc_pipeline

class RunDLCView(APIView):
    def post(self, request):
        video_path = request.data.get("video_path")
        model = request.data.get("model", "superanimal_quadruped")
        pcutoff = float(request.data.get("pcutoff", 0.15))

        if not video_path:
            return Response({"error": "Missing 'video_path'"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = run_dlc_pipeline(video_path, model, pcutoff)
            return Response(result)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
