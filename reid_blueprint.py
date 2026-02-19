"""
Person Re-Identification Labeling Blueprint
============================================
Add this blueprint to your existing Flask app for manual person labeling.

Integration:
    from reid_blueprint import reid_bp
    app.register_blueprint(reid_bp, url_prefix="/reid")

Routes created:
    /reid/                  - Dashboard showing labeling jobs
    /reid/label/<job_id>    - Labeling interface for a specific job
    /reid/api/jobs          - API: List all jobs (for Dagster sensor)
    /reid/api/jobs/<id>     - API: Get job status
    /reid/api/label         - API: Submit label
    /reid/api/undo/<id>     - API: Undo last label
"""

import json
import io
import base64
from datetime import datetime
from flask import Blueprint, render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from minio import Minio
from minio.error import S3Error
from flask_login import login_required, current_user

# Blueprint definition
reid_bp = Blueprint('reid', __name__, template_folder='templates/reid_templates')

# ============================================================================
# MinIO Configuration - Uses same credentials as your existing setup
# ============================================================================

def get_minio_client():
    """Get MinIO client using existing app config or defaults"""
    return Minio(
        endpoint=current_app.config.get('MINIO_ENDPOINT', '194.171.191.226:3135'),
        access_key=current_app.config.get('MINIO_ACCESS_KEY', 'tastelab_admin'),
        secret_key=current_app.config.get('MINIO_SECRET_KEY', 'tastelabpassword123'),
        secure=current_app.config.get('MINIO_SECURE', False)
    )

# Bucket configuration
PROCESSED_BUCKET = 'tastelab-videos-processed'
REID_SUBFOLDER = 'reid_data'  # Subfolder within session's pipeline_outputs

# ============================================================================
# Helper Functions
# ============================================================================

def list_labeling_jobs():
    """
    List all labeling jobs from MinIO.
    Jobs are stored in: {date}/{session}/pipeline_outputs/reid_data/jobs/{job_id}/job.json
    """
    client = get_minio_client()
    jobs = []
    
    try:
        objects = client.list_objects(PROCESSED_BUCKET, recursive=True)
        
        for obj in objects:
            path = obj.object_name
            # Look for job.json files in reid_data/jobs/
            if 'reid_data/jobs/' in path and path.endswith('job.json'):
                try:
                    response = client.get_object(PROCESSED_BUCKET, path)
                    job_data = json.loads(response.read().decode('utf-8'))
                    response.close()
                    response.release_conn()
                    
                    # Extract session info from path
                    parts = path.split('/')
                    job_data['date_folder'] = parts[0] if len(parts) > 0 else ''
                    job_data['session_folder'] = parts[1] if len(parts) > 1 else ''
                    job_data['path'] = path
                    
                    jobs.append(job_data)
                except Exception as e:
                    current_app.logger.error(f"Error reading job {path}: {e}")
                    
    except S3Error as e:
        current_app.logger.error(f"MinIO error listing jobs: {e}")
    
    # Sort by created_at descending
    jobs.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jobs


def get_job(job_id):
    """Get a specific labeling job by ID"""
    jobs = list_labeling_jobs()
    for job in jobs:
        if job.get('job_id') == job_id:
            return job
    return None


def get_job_crops(job):
    """
    Get all crop images for a labeling job.
    Crops are in: {date}/{session}/pipeline_outputs/reid_data/crops/{track_id}/
    """
    client = get_minio_client()
    crops_by_track = {}
    
    date_folder = job.get('date_folder', '')
    session_folder = job.get('session_folder', '')
    crops_prefix = f"{date_folder}/{session_folder}/pipeline_outputs/reid_data/crops/"
    
    try:
        objects = client.list_objects(PROCESSED_BUCKET, prefix=crops_prefix, recursive=True)
        
        for obj in objects:
            path = obj.object_name
            if path.lower().endswith(('.jpg', '.jpeg', '.png')):
                # Extract track_id from path
                rel_path = path.replace(crops_prefix, '')
                parts = rel_path.split('/')
                if len(parts) >= 2:
                    track_id = parts[0]
                    filename = parts[-1]
                    
                    if track_id not in crops_by_track:
                        crops_by_track[track_id] = []
                    
                    crops_by_track[track_id].append({
                        'path': path,
                        'filename': filename,
                        'track_id': track_id
                    })
    except S3Error as e:
        current_app.logger.error(f"MinIO error getting crops: {e}")
    
    return crops_by_track


def get_crop_image_base64(path):
    """Get a crop image as base64 for display"""
    client = get_minio_client()
    try:
        response = client.get_object(PROCESSED_BUCKET, path)
        image_data = response.read()
        response.close()
        response.release_conn()
        
        # Determine image type
        ext = path.lower().split('.')[-1]
        mime_type = 'image/jpeg' if ext in ['jpg', 'jpeg'] else 'image/png'
        
        b64 = base64.b64encode(image_data).decode('utf-8')
        return f"data:{mime_type};base64,{b64}"
    except S3Error as e:
        current_app.logger.error(f"Error getting image {path}: {e}")
        return None


def save_label(job_id, track_id, person_id):
    """
    Save a label assignment.
    Labels stored in: {date}/{session}/pipeline_outputs/reid_data/labeled/{person_id}/
    Also updates job.json with progress
    """
    client = get_minio_client()
    job = get_job(job_id)
    
    if not job:
        return False, "Job not found"
    
    date_folder = job.get('date_folder', '')
    session_folder = job.get('session_folder', '')
    
    # Source: crops/{track_id}/
    # Destination: labeled/{person_id}/
    crops_prefix = f"{date_folder}/{session_folder}/pipeline_outputs/reid_data/crops/{track_id}/"
    labeled_prefix = f"{date_folder}/{session_folder}/pipeline_outputs/reid_data/labeled/person_{person_id}/"
    
    try:
        # Copy all images from track to labeled folder
        objects = list(client.list_objects(PROCESSED_BUCKET, prefix=crops_prefix))
        copied = 0
        
        for obj in objects:
            src_path = obj.object_name
            if src_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                filename = src_path.split('/')[-1]
                # Add track_id to filename to avoid collisions
                new_filename = f"{track_id}_{filename}"
                dest_path = f"{labeled_prefix}{new_filename}"
                
                # Copy object
                client.copy_object(
                    PROCESSED_BUCKET,
                    dest_path,
                    f"{PROCESSED_BUCKET}/{src_path}"
                )
                copied += 1
        
        # Update job progress
        update_job_progress(job, track_id, person_id)
        
        return True, f"Labeled {copied} images as person {person_id}"
        
    except S3Error as e:
        current_app.logger.error(f"Error saving label: {e}")
        return False, str(e)


def update_job_progress(job, track_id, person_id):
    """Update job.json with labeling progress"""
    client = get_minio_client()
    
    # Initialize labeled_tracks if not present
    if 'labeled_tracks' not in job:
        job['labeled_tracks'] = {}
    
    # Record the label
    job['labeled_tracks'][track_id] = {
        'person_id': person_id,
        'labeled_at': datetime.now().isoformat(),
        'labeled_by': current_user.username if current_user.is_authenticated else 'anonymous'
    }
    
    # Update status
    total_tracks = job.get('total_tracks', 0)
    labeled_count = len(job['labeled_tracks'])
    
    if labeled_count >= total_tracks:
        job['status'] = 'completed'
        job['completed_at'] = datetime.now().isoformat()
    else:
        job['status'] = 'in_progress'
    
    job['labeled_count'] = labeled_count
    job['updated_at'] = datetime.now().isoformat()
    
    # Save back to MinIO
    job_path = job.get('path')
    if job_path:
        # Remove fields we added for display
        job_copy = {k: v for k, v in job.items() 
                   if k not in ['date_folder', 'session_folder', 'path']}
        
        job_json = json.dumps(job_copy, indent=2).encode('utf-8')
        client.put_object(
            PROCESSED_BUCKET,
            job_path,
            io.BytesIO(job_json),
            len(job_json),
            content_type='application/json'
        )


def undo_label(job_id, track_id):
    """Undo a label by removing from labeled folder and updating job"""
    client = get_minio_client()
    job = get_job(job_id)
    
    if not job:
        return False, "Job not found"
    
    labeled_tracks = job.get('labeled_tracks', {})
    if track_id not in labeled_tracks:
        return False, "Track not labeled"
    
    date_folder = job.get('date_folder', '')
    session_folder = job.get('session_folder', '')
    person_id = labeled_tracks[track_id]['person_id']
    
    # Remove images from labeled folder
    labeled_prefix = f"{date_folder}/{session_folder}/pipeline_outputs/reid_data/labeled/person_{person_id}/"
    
    try:
        objects = list(client.list_objects(PROCESSED_BUCKET, prefix=labeled_prefix))
        
        for obj in objects:
            # Only delete files that start with this track_id
            if f"{track_id}_" in obj.object_name:
                client.remove_object(PROCESSED_BUCKET, obj.object_name)
        
        # Update job
        del job['labeled_tracks'][track_id]
        job['labeled_count'] = len(job['labeled_tracks'])
        job['status'] = 'in_progress' if job['labeled_count'] > 0 else 'pending'
        job['updated_at'] = datetime.now().isoformat()
        
        # Save job
        job_path = job.get('path')
        if job_path:
            job_copy = {k: v for k, v in job.items() 
                       if k not in ['date_folder', 'session_folder', 'path']}
            job_json = json.dumps(job_copy, indent=2).encode('utf-8')
            client.put_object(
                PROCESSED_BUCKET,
                job_path,
                io.BytesIO(job_json),
                len(job_json),
                content_type='application/json'
            )
        
        return True, f"Undid label for track {track_id}"
        
    except S3Error as e:
        return False, str(e)


# ============================================================================
# Web Routes
# ============================================================================

@reid_bp.route('/')
@login_required
def dashboard():
    """Main dashboard showing all labeling jobs"""
    jobs = list_labeling_jobs()
    
    # Categorize jobs
    pending = [j for j in jobs if j.get('status') == 'pending']
    in_progress = [j for j in jobs if j.get('status') == 'in_progress']
    completed = [j for j in jobs if j.get('status') == 'completed']
    
    return render_template('reid_templates/reid_dashboard.html',
                         user=current_user,  
                         pending=pending,
                         in_progress=in_progress,
                         completed=completed,
                         total_jobs=len(jobs))


@reid_bp.route('/label/<job_id>')
@login_required
def label_job(job_id):
    """Labeling interface for a specific job"""
    job = get_job(job_id)
    
    if not job:
        return render_template('reid_templates/reid_error.html', user=current_user, message="Job not found"), 404
    
    # Get all crops organized by track
    crops_by_track = get_job_crops(job)
    
    # Filter out already labeled tracks
    labeled_tracks = set(job.get('labeled_tracks', {}).keys())
    unlabeled_tracks = {k: v for k, v in crops_by_track.items() if k not in labeled_tracks}
    
    # Get preview images for each track (first 4 images)
    tracks_preview = []
    for track_id, crops in unlabeled_tracks.items():
        preview_crops = crops[:4]  # Max 4 preview images
        preview_images = []
        for crop in preview_crops:
            img_data = get_crop_image_base64(crop['path'])
            if img_data:
                preview_images.append(img_data)
        
        tracks_preview.append({
            'track_id': track_id,
            'total_images': len(crops),
            'preview_images': preview_images
        })
    
    # Sort by track_id
    tracks_preview.sort(key=lambda x: x['track_id'])
    
    # Person options (configurable)
    person_options = job.get('person_ids', list(range(1, 7)))  # Default: 1-6
    
    return render_template('reid_templates/reid_label.html',
                         user=current_user,  
                         job=job,
                         tracks=tracks_preview,
                         person_options=person_options,
                         labeled_count=len(labeled_tracks),
                         total_tracks=len(crops_by_track))


# ============================================================================
# API Routes (for Dagster sensor and AJAX)
# ============================================================================

@reid_bp.route('/api/jobs')
def api_list_jobs():
    """API: List all labeling jobs (used by Dagster sensor)"""
    jobs = list_labeling_jobs()
    
    # Return simplified data for API
    return jsonify({
        'jobs': [{
            'job_id': j.get('job_id'),
            'session': f"{j.get('date_folder')}/{j.get('session_folder')}",
            'status': j.get('status'),
            'total_tracks': j.get('total_tracks', 0),
            'labeled_count': j.get('labeled_count', 0),
            'created_at': j.get('created_at'),
            'completed_at': j.get('completed_at')
        } for j in jobs]
    })


@reid_bp.route('/api/jobs/<job_id>')
def api_get_job(job_id):
    """API: Get specific job status"""
    job = get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify({
        'job_id': job.get('job_id'),
        'session': f"{job.get('date_folder')}/{job.get('session_folder')}",
        'status': job.get('status'),
        'total_tracks': job.get('total_tracks', 0),
        'labeled_count': job.get('labeled_count', 0),
        'labeled_tracks': job.get('labeled_tracks', {}),
        'created_at': job.get('created_at'),
        'completed_at': job.get('completed_at')
    })


@reid_bp.route('/api/label', methods=['POST'])
@login_required
def api_label():
    """API: Submit a label"""
    data = request.get_json()
    
    job_id = data.get('job_id')
    track_id = data.get('track_id')
    person_id = data.get('person_id')
    
    if not all([job_id, track_id, person_id]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    success, message = save_label(job_id, track_id, person_id)
    
    if success:
        job = get_job(job_id)
        return jsonify({
            'success': True,
            'message': message,
            'labeled_count': job.get('labeled_count', 0),
            'status': job.get('status')
        })
    else:
        return jsonify({'error': message}), 500


@reid_bp.route('/api/undo/<job_id>/<track_id>', methods=['POST'])
@login_required
def api_undo(job_id, track_id):
    """API: Undo a label"""
    success, message = undo_label(job_id, track_id)
    
    if success:
        job = get_job(job_id)
        return jsonify({
            'success': True,
            'message': message,
            'labeled_count': job.get('labeled_count', 0)
        })
    else:
        return jsonify({'error': message}), 500


@reid_bp.route('/api/skip', methods=['POST'])
@login_required  
def api_skip():
    """API: Skip a track (mark as 'unknown' or 'skip')"""
    data = request.get_json()
    
    job_id = data.get('job_id')
    track_id = data.get('track_id')
    
    if not all([job_id, track_id]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Save as person_id = 0 (unknown/skip)
    success, message = save_label(job_id, track_id, person_id=0)
    
    if success:
        job = get_job(job_id)
        return jsonify({
            'success': True,
            'message': 'Track skipped',
            'labeled_count': job.get('labeled_count', 0),
            'status': job.get('status')
        })
    else:
        return jsonify({'error': message}), 500
