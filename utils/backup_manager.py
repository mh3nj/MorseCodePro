"""
Automatic and Manual Backup System
"""

import shutil
import json
import zipfile
from datetime import datetime
from pathlib import Path
import threading
import time

class BackupManager:
    def __init__(self, app_dir):
        self.app_dir = Path(app_dir)
        self.backup_dir = self.app_dir / "data" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.auto_backup_enabled = True
        self.backup_interval = 3600  # 1 hour in seconds
        
    def manual_backup(self, backup_name=None):
        """Create a manual backup"""
        if backup_name is None:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = self.backup_dir / f"{backup_name}.zip"
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Backup database
            db_path = self.app_dir / "data" / "history.db"
            if db_path.exists():
                zipf.write(db_path, "history.db")
            
            # Backup custom maps
            maps_dir = self.app_dir / "config" / "morse_maps"
            if maps_dir.exists():
                for map_file in maps_dir.glob("*.json"):
                    zipf.write(map_file, f"morse_maps/{map_file.name}")
            
            # Backup settings
            settings_file = self.app_dir / "config" / "user_settings.json"
            if settings_file.exists():
                zipf.write(settings_file, "user_settings.json")
        
        return backup_path
    
    def auto_backup_loop(self):
        """Background thread for auto backups"""
        while self.auto_backup_enabled:
            time.sleep(self.backup_interval)
            try:
                self.manual_backup(f"auto_{datetime.now().strftime('%Y%m%d')}")
                print(f"Auto backup created at {datetime.now()}")
            except Exception as e:
                print(f"Auto backup failed: {e}")
    
    def start_auto_backup(self):
        """Start automatic backup thread"""
        backup_thread = threading.Thread(target=self.auto_backup_loop, daemon=True)
        backup_thread.start()
    
    def list_backups(self):
        """List all available backups"""
        backups = []
        for backup_file in self.backup_dir.glob("*.zip"):
            backups.append({
                'name': backup_file.stem,
                'path': backup_file,
                'size': backup_file.stat().st_size,
                'created': datetime.fromtimestamp(backup_file.stat().st_mtime)
            })
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    def restore_backup(self, backup_name):
        """Restore from a backup file"""
        backup_path = self.backup_dir / f"{backup_name}.zip"
        if not backup_path.exists():
            return False
        
        # Create restore point first
        self.manual_backup("pre_restore")
        
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extractall(self.app_dir)
        
        return True
    
    def delete_old_backups(self, keep_count=10):
        """Delete old backups, keep only recent N"""
        backups = self.list_backups()
        for backup in backups[keep_count:]:
            backup['path'].unlink()
