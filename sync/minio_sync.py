import time
from datetime import datetime
from main import app
from models import db, NlpAnalysis, Experiment
from sync.minio_service import MinIOService
from sync.data_import import insert_analysis_data

def sync_new_analyses(max_imports=None):
    """
    Check MinIO for new analysis files and import them
    
    Args:
        max_imports (int, optional): Maximum number of files to import per run. 
                                     If None, imports all new files.
    
    Returns:
        dict: Results containing new_imports, skipped, errors, and duration
    """
    start_time = time.time()
    app.logger.info("Starting MinIO sync check...")
    
    minio_service = MinIOService()

    # Get all analysis files from MinIO
    list_start = time.time()
    analysis_files = minio_service.list_analysis_files()
    list_duration = time.time() - list_start

    app.logger.info(f"Found {len(analysis_files)} files in MinIO (took {list_duration:.2f}s)")
    
    new_imports = 0
    skipped = 0
    errors = 0
    
    for idx, file_info in enumerate(analysis_files, 1):
        # Stop if we hit the max import limit
        if max_imports and new_imports >= max_imports:
            app.logger.info(f"Reached import limit ({max_imports}), will continue next cycle")
            break
        
        # Log progress every 10 files
        if idx % 10 == 0:
            elapsed = time.time() - start_time
            app.logger.info(f"Progress: {idx}/{len(analysis_files)} files checked ({elapsed:.1f}s)")
        
        # Check if already imported by checking source_filename
        existing = NlpAnalysis.query.filter_by(
            source_filename=file_info['video_name']
        ).first()
        
        if existing:
            skipped += 1
            continue
        
        try:
            file_start = time.time()
            
            # Load all related JSON files
            session_data = minio_service.load_video_analysis_data(
                file_info['date_folder'],
                file_info['session_folder'],
                file_info['video_name']
            )
            
            if not session_data or 'sentiment' not in session_data:
                app.logger.warning(f"Incomplete data for {file_info['video_name']}")
                continue
            
            # Import using refactored function
            analysis_id = insert_analysis_data(
                session_data,
                file_info['date_folder'],
                file_info['session_folder'],
                file_info['video_name']
            )
            
            file_duration = time.time() - file_start
            
            if analysis_id:
                new_imports += 1
                app.logger.info(f"✓ Imported {file_info['video_name']} in {file_duration:.2f}s (Analysis ID: {analysis_id})")
            
        except Exception as e:
            errors += 1
            app.logger.error(f"✗ Error importing {file_info['video_name']}: {str(e)}")
            import traceback
            app.logger.error(traceback.format_exc())
    
    total_duration = time.time() - start_time
    app.logger.info(f"Sync complete in {total_duration:.2f}s: {new_imports} new, {skipped} skipped, {errors} errors")
    
    return {
        'new_imports': new_imports,
        'skipped': skipped,
        'errors': errors,
        'duration': round(total_duration, 2)
    }