import json
from minio import Minio
from main import app

class MinIOService:
    """
    Service class for interacting with MinIO object storage.
    Handles listing, reading, and aggregating analysis files from various buckets.
    """

    def __init__(self):
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """
        Initialize the MinIO client using application configuration.

        The MinIO connection settings (endpoint, credentials, security mode,
        and bucket name) are loaded from the Flask application configuration,
        which is defined in `config.py` at the root of the dashboard directory.
        """
        self.client = Minio(
            endpoint=app.config['MINIO_ENDPOINT'],
            access_key=app.config['MINIO_ACCESS_KEY'],
            secret_key=app.config['MINIO_SECRET_KEY'],
            secure=app.config['MINIO_SECURE']
        )
        self.bucket = app.config['MINIO_BUCKET']
    
    def list_analysis_files(self, prefix=""):
        """
        Scan the storage bucket for processed video analysis files.

        Iterates through the bucket structure to find files indicating completed
        analysis (specifically chart data for NLP or detections for CV). 
        Results are deduplicated so that a video with both analysis types 
        only appears once in the returned list.

        Args:
            prefix (str): Optional directory prefix to filter objects.

        Returns:
            list: A list of dictionaries, each containing metadata (path, date, 
                  session, video_name) for unique analyzed videos.
        """
        try:
            objects = self.client.list_objects(self.bucket, prefix=prefix, recursive=True)
            unique_videos = {} 
            
            for obj in objects:
                path = obj.object_name
                parts = path.split('/')
                
                # Structure expectation: date/session/pipeline_outputs/type/filename
                if len(parts) >= 5 and parts[2] == 'pipeline_outputs':
                    filename = parts[-1]
                    video_name = None
                    
                    # Identify valid analysis files (NLP or CV)
                    if parts[3] == 'analysis' and '.chart_data.json' in filename:
                        video_name = filename.replace('.chart_data.json', '')
                        
                    elif parts[3] == 'cv_analysis' and '.detections.json' in filename:
                        video_name = filename.replace('.detections.json', '')

                    if video_name:
                        # Deduplicate based on folder structure and video name
                        key = f"{parts[0]}/{parts[1]}/{video_name}"
                        
                        if key not in unique_videos:
                            unique_videos[key] = {
                                'path': path,
                                'date_folder': parts[0],
                                'session_folder': parts[1],
                                'video_name': video_name,
                                'last_modified': obj.last_modified
                            }
            
            return list(unique_videos.values())
            
        except Exception as e:
            app.logger.error(f"Error listing MinIO files: {e}")
            return []
    
    def read_json_file(self, object_name):
        """
        Retrieve and parse a JSON object from the storage bucket.

        Args:
            object_name (str): The full path of the object in the MinIO bucket.

        Returns:
            dict: The parsed JSON data if successful, None otherwise.
        """
        response = None
        try:
            response = self.client.get_object(self.bucket, object_name)
            json_bytes = response.read()
            return json.loads(json_bytes.decode('utf-8'))
        except Exception as e:
            app.logger.info(f"Error reading {object_name}: {str(e)}")
            return None
        finally:
            if response:
                response.close()
                response.release_conn()
    
    def load_video_analysis_data(self, date_folder, session_folder, video_name):
        """
        Aggregate all analysis artifacts for a specific video session.

        Fetches NLP data, Computer Vision tracking data, transcripts, and metadata
        from their respective paths and buckets.

        Args:
            date_folder (str): The date directory (YYYY-MM-DD).
            session_folder (str): The specific session directory name.
            video_name (str): The identifier of the video file.

        Returns:
            dict: A dictionary containing keys for 'chart_data', 'insights', 
                  'sentiment', 'detections', 'metadata', etc.
        """
        base_path = f"{date_folder}/{session_folder}/pipeline_outputs"
        
        # Define paths for standard analysis files
        file_mapping = {
            'chart_data': f"{base_path}/analysis/{video_name}.chart_data.json",
            'keyword_cloud': f"{base_path}/analysis/{video_name}.keyword_cloud.json",
            'insights': f"{base_path}/insights/{video_name}.insights.json",
            'sentiment': f"{base_path}/sentiment_analysis/{video_name}.sentiment.json",
            'summary': f"{base_path}/summaries/{video_name}.summary.json",
            'detections': f"{base_path}/cv_analysis/{video_name}.detections.json"
        }
        
        data = {}
        for key, path in file_mapping.items():
            result = self.read_json_file(path)
            if result:
                data[key] = result
        
        # Load Transcript
        transcript_path = f"{date_folder}/{session_folder}/{video_name}.json"
        transcript_base = self.read_json_file(transcript_path)
        if transcript_base:
            data['transcript_base'] = transcript_base

        # Load Metadata from sorted bucket
        try:
            metadata_path = f"{date_folder}/{session_folder}/metadata.json"
            response = self.client.get_object("tastelab-videos-sorted", metadata_path)
            
            metadata = json.loads(response.read().decode('utf-8'))
            data['metadata'] = metadata
            
            response.close()
            response.release_conn()
        except Exception as e:
            app.logger.error(f"Metadata Fetch Error for {video_name}: {e}")
        
        return data