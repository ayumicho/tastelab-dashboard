import time
from datetime import datetime
from main import app
from models import NlpAnalysis, TrackingAnalysis, TranscriptSummary
from sync.minio_service import MinIOService
from sync.data_import import insert_analysis_data, find_or_create_experiment

def sync_new_analyses(max_imports=None):
    """
    Synchronize analysis data from MinIO to the local database.

    This function scans the MinIO storage for new analysis files (NLP or CV).
    It checks against the local database to avoid duplicate processing.
    If new data is found (or if one type of analysis is missing locally), 
    it retrieves the full analysis payload and triggers the import process.

    Args:
        max_imports (int, optional): Limit the number of files processed in one run.
                                     Useful for batch processing to avoid timeouts.

    Returns:
        dict: A summary of the sync operation containing counts for 
              new_imports, skipped files, errors, and total duration.
    """
    start_time = time.time()
    app.logger.info("Starting MinIO sync check...")
    
    minio_service = MinIOService()

    # Fetch file list
    list_start = time.time()
    analysis_files = minio_service.list_analysis_files()
    list_duration = time.time() - list_start

    app.logger.info(f"Found {len(analysis_files)} files in MinIO (took {list_duration:.2f}s)")
    
    results = {
        'new_imports': 0,
        'skipped': 0,
        'errors': 0
    }
    
    for idx, file_info in enumerate(analysis_files, 1):
        # Stop early if a batch limit is configured
        if max_imports and results['new_imports'] >= max_imports:
            app.logger.info(f"Reached import limit ({max_imports}), will continue next cycle")
            break
        
        # Emit progress logs for long-running sync jobs
        if idx % 10 == 0:
            elapsed = time.time() - start_time
            app.logger.info(f"Progress: {idx}/{len(analysis_files)} files checked ({elapsed:.1f}s)")
        
        video_name = file_info['video_name']

        try:
            # Ensure an experiment exists for this video/session context
            experiment = find_or_create_experiment(
                video_name, 
                file_info['date_folder'], 
                file_info['session_folder']
            )

            # Check if NLP analysis already exists for this experiment/video
            existing_nlp = NlpAnalysis.query.filter_by(
                experiment_id=experiment.id,
                source_filename=video_name
            ).first()

            # Check if CV / tracking analysis already exists
            existing_cv = TrackingAnalysis.query.filter_by(
                experiment_id=experiment.id,
                source_filename=video_name
            ).first()

            # Check if there is a summary
            missing_summary = False
            if existing_nlp:
                has_summary = TranscriptSummary.query.filter_by(analysis_id=existing_nlp.id).first() is not None
                if not has_summary:
                    missing_summary = True

            # Determine if analysis is present
            is_present = existing_nlp is not None or existing_cv is not None

            # Skip if present (and not missing a required summary)
            if is_present and not missing_summary:
                results['skipped'] += 1
                continue
            
            # Retrieve full dataset from MinIO
            file_start = time.time()
            session_data = minio_service.load_video_analysis_data(
                file_info['date_folder'],
                file_info['session_folder'],
                video_name,
            )
            
            # Validate data presence
            has_nlp = 'sentiment' in session_data
            has_detections = 'detections' in session_data

            if not has_nlp and not has_detections:
                app.logger.warning(f"Incomplete data for {video_name} (No sentiment or detections)")
                continue
            
            # Insert or update analysis data in the database
            analysis_id = insert_analysis_data(
                session_data,
                file_info['date_folder'],
                file_info['session_folder'],
                video_name,
            )
            
            file_duration = time.time() - file_start
            
            if analysis_id:
                results['new_imports'] += 1
                app.logger.info(f"✓ Processed {video_name} in {file_duration:.2f}s (ID: {analysis_id})")
            
        except Exception as e:
            results['errors'] += 1
            app.logger.error(f"✗ Error importing {video_name}: {str(e)}")
            import traceback
            app.logger.error(traceback.format_exc())
    
    total_duration = time.time() - start_time
    app.logger.info(
        f"Sync complete in {total_duration:.2f}s: "
        f"{results['new_imports']} processed, {results['skipped']} skipped, {results['errors']} errors"
    )
    
    results['duration'] = round(total_duration, 2)
    return results