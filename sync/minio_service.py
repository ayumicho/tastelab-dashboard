import json
from minio import Minio
from main import app
class MinIOService:
    def __init__(self):
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize MinIO client with config"""
        self.client = Minio(
            endpoint=app.config['MINIO_ENDPOINT'],
            access_key=app.config['MINIO_ACCESS_KEY'],
            secret_key=app.config['MINIO_SECRET_KEY'],
            secure=app.config['MINIO_SECURE']
        )
        self.bucket = app.config['MINIO_BUCKET']
    
    def list_analysis_files(self, prefix=""):
        """List all analysis files in bucket"""
        try:
            objects = self.client.list_objects(self.bucket, prefix=prefix, recursive=True)
            analysis_files = []
            
            for obj in objects:
                path = obj.object_name
                parts = path.split('/')
                
                # Filter for chart_data.json files (your main analysis indicator)
                if (len(parts) >= 5 and 
                    parts[2] == 'pipeline_outputs' and 
                    parts[3] == 'analysis' and 
                    '.chart_data.json' in parts[-1]):
                    
                    analysis_files.append({
                        'path': path,
                        'date_folder': parts[0],
                        'session_folder': parts[1],
                        'video_name': parts[-1].replace('.chart_data.json', ''),
                        'last_modified': obj.last_modified
                    })
            
            return analysis_files
        except Exception as e:
            app.logger.error(f"Error listing MinIO files: {e}")
            return []
    
    def read_json_file(self, object_name):
        """Read and parse JSON file from MinIO"""
        response = None
        try:
            response = self.client.get_object(self.bucket, object_name)
            json_bytes = response.read()
            return json.loads(json_bytes.decode('utf-8'))
        except Exception as e:
            app.logger.error(f"Error reading {object_name}: {str(e)[:100]}")
            return None
        finally:
            if response:
                response.close()
                response.release_conn()
    
    def load_video_analysis_data(self, date_folder, session_folder, video_name):
        """Load all JSON files for a specific video"""
        base_path = f"{date_folder}/{session_folder}/pipeline_outputs"
        
        file_mapping = {
            'chart_data': f"{base_path}/analysis/{video_name}.chart_data.json",
            'keyword_cloud': f"{base_path}/analysis/{video_name}.keyword_cloud.json",
            'insights': f"{base_path}/insights/{video_name}.insights.json",
            'sentiment': f"{base_path}/sentiment_analysis/{video_name}.sentiment.json",
            'summary': f"{base_path}/summaries/{video_name}.summary.json"
        }
        
        data = {}
        for key, path in file_mapping.items():
            result = self.read_json_file(path)
            if result:
                data[key] = result
        
        return data