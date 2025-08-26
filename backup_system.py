import os
import shutil
import sqlite3
import json
import zipfile
import schedule
import time
from datetime import datetime, timedelta
import threading
import psutil
from pathlib import Path

class BackupSystem:
    def __init__(self, app_path=None):
        self.app_path = app_path or os.getcwd()
        self.backup_dir = os.path.join(self.app_path, 'backups')
        self.config_file = os.path.join(self.app_path, 'backup_config.json')
        self.ensure_backup_directory()
        self.load_config()
    
    def ensure_backup_directory(self):
        """إنشاء مجلد النسخ الاحتياطية إذا لم يكن موجوداً"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def load_config(self):
        """تحميل إعدادات النسخ الاحتياطي"""
        default_config = {
            "auto_backup_enabled": True,
            "backup_interval_hours": 6,
            "max_backups": 10,
            "backup_database": True,
            "backup_uploads": True,
            "backup_config": True,
            "compression_enabled": True,
            "last_backup": None
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                # دمج الإعدادات الافتراضية مع الموجودة
                for key, value in default_config.items():
                    if key not in self.config:
                        self.config[key] = value
            except:
                self.config = default_config
        else:
            self.config = default_config
        
        self.save_config()
    
    def save_config(self):
        """حفظ إعدادات النسخ الاحتياطي"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"خطأ في حفظ إعدادات النسخ الاحتياطي: {e}")
    
    def create_backup(self, backup_type="manual"):
        """إنشاء نسخة احتياطية شاملة"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{backup_type}_{timestamp}"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            # إنشاء مجلد النسخة الاحتياطية
            os.makedirs(backup_path, exist_ok=True)
            
            backup_info = {
                "timestamp": timestamp,
                "type": backup_type,
                "created_at": datetime.now().isoformat(),
                "app_version": "1.0.0",
                "files_backed_up": [],
                "size_mb": 0
            }
            
            # نسخ قاعدة البيانات
            if self.config["backup_database"]:
                self._backup_database(backup_path, backup_info)
            
            # نسخ الملفات المرفوعة
            if self.config["backup_uploads"]:
                self._backup_uploads(backup_path, backup_info)
            
            # نسخ ملفات الإعدادات
            if self.config["backup_config"]:
                self._backup_config_files(backup_path, backup_info)
            
            # نسخ الملفات الثابتة المهمة
            self._backup_static_files(backup_path, backup_info)
            
            # حفظ معلومات النسخة الاحتياطية
            info_file = os.path.join(backup_path, "backup_info.json")
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, ensure_ascii=False, indent=2)
            
            # ضغط النسخة الاحتياطية إذا كان مفعلاً
            if self.config["compression_enabled"]:
                compressed_path = self._compress_backup(backup_path)
                shutil.rmtree(backup_path)  # حذف المجلد غير المضغوط
                backup_path = compressed_path
            
            # حساب حجم النسخة الاحتياطية
            backup_size = self._get_folder_size(backup_path)
            backup_info["size_mb"] = round(backup_size / (1024 * 1024), 2)
            
            # تحديث آخر نسخة احتياطية
            self.config["last_backup"] = datetime.now().isoformat()
            self.save_config()
            
            # تنظيف النسخ القديمة
            self._cleanup_old_backups()
            
            return {
                "success": True,
                "backup_path": backup_path,
                "backup_info": backup_info,
                "message": f"تم إنشاء النسخة الاحتياطية بنجاح: {backup_name}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"فشل في إنشاء النسخة الاحتياطية: {e}"
            }
    
    def _backup_database(self, backup_path, backup_info):
        """نسخ قاعدة البيانات"""
        db_path = os.path.join(self.app_path, "supermarket.db")
        if os.path.exists(db_path):
            backup_db_path = os.path.join(backup_path, "database")
            os.makedirs(backup_db_path, exist_ok=True)
            
            # نسخ ملف قاعدة البيانات
            shutil.copy2(db_path, os.path.join(backup_db_path, "supermarket.db"))
            
            # تصدير البيانات كـ SQL
            self._export_database_sql(db_path, os.path.join(backup_db_path, "database_export.sql"))
            
            backup_info["files_backed_up"].append("database/supermarket.db")
            backup_info["files_backed_up"].append("database/database_export.sql")
    
    def _export_database_sql(self, db_path, output_path):
        """تصدير قاعدة البيانات كملف SQL"""
        try:
            conn = sqlite3.connect(db_path)
            with open(output_path, 'w', encoding='utf-8') as f:
                for line in conn.iterdump():
                    f.write('%s\n' % line)
            conn.close()
        except Exception as e:
            print(f"خطأ في تصدير قاعدة البيانات: {e}")
    
    def _backup_uploads(self, backup_path, backup_info):
        """نسخ الملفات المرفوعة"""
        uploads_path = os.path.join(self.app_path, "static", "uploads")
        if os.path.exists(uploads_path):
            backup_uploads_path = os.path.join(backup_path, "uploads")
            shutil.copytree(uploads_path, backup_uploads_path)
            backup_info["files_backed_up"].append("uploads/")
    
    def _backup_config_files(self, backup_path, backup_info):
        """نسخ ملفات الإعدادات"""
        config_files = [
            "backup_config.json",
            ".env",
            "config.py"
        ]
        
        config_backup_path = os.path.join(backup_path, "config")
        os.makedirs(config_backup_path, exist_ok=True)
        
        for config_file in config_files:
            file_path = os.path.join(self.app_path, config_file)
            if os.path.exists(file_path):
                shutil.copy2(file_path, config_backup_path)
                backup_info["files_backed_up"].append(f"config/{config_file}")
    
    def _backup_static_files(self, backup_path, backup_info):
        """نسخ الملفات الثابتة المهمة"""
        static_files = [
            "requirements.txt",
            "app.py",
            "backup_system.py"
        ]
        
        static_backup_path = os.path.join(backup_path, "app_files")
        os.makedirs(static_backup_path, exist_ok=True)
        
        for static_file in static_files:
            file_path = os.path.join(self.app_path, static_file)
            if os.path.exists(file_path):
                shutil.copy2(file_path, static_backup_path)
                backup_info["files_backed_up"].append(f"app_files/{static_file}")
    
    def _compress_backup(self, backup_path):
        """ضغط النسخة الاحتياطية"""
        zip_path = backup_path + ".zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, backup_path)
                    zipf.write(file_path, arcname)
        return zip_path
    
    def _get_folder_size(self, folder_path):
        """حساب حجم المجلد"""
        if os.path.isfile(folder_path):
            return os.path.getsize(folder_path)
        
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += os.path.getsize(file_path)
        return total_size
    
    def _cleanup_old_backups(self):
        """تنظيف النسخ الاحتياطية القديمة"""
        try:
            backups = []
            for item in os.listdir(self.backup_dir):
                item_path = os.path.join(self.backup_dir, item)
                if os.path.isfile(item_path) or os.path.isdir(item_path):
                    backups.append((item, os.path.getctime(item_path)))
            
            # ترتيب حسب تاريخ الإنشاء
            backups.sort(key=lambda x: x[1], reverse=True)
            
            # حذف النسخ الزائدة
            max_backups = self.config["max_backups"]
            if len(backups) > max_backups:
                for backup_name, _ in backups[max_backups:]:
                    backup_path = os.path.join(self.backup_dir, backup_name)
                    if os.path.isfile(backup_path):
                        os.remove(backup_path)
                    elif os.path.isdir(backup_path):
                        shutil.rmtree(backup_path)
                    print(f"تم حذف النسخة الاحتياطية القديمة: {backup_name}")
        
        except Exception as e:
            print(f"خطأ في تنظيف النسخ الاحتياطية: {e}")
    
    def restore_backup(self, backup_path):
        """استعادة نسخة احتياطية"""
        try:
            # التحقق من وجود النسخة الاحتياطية
            if not os.path.exists(backup_path):
                return {"success": False, "message": "النسخة الاحتياطية غير موجودة"}
            
            # إنشاء نسخة احتياطية من الحالة الحالية قبل الاستعادة
            current_backup = self.create_backup("pre_restore")
            
            # استخراج النسخة الاحتياطية إذا كانت مضغوطة
            if backup_path.endswith('.zip'):
                extract_path = backup_path[:-4]
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    zipf.extractall(extract_path)
                backup_path = extract_path
            
            # استعادة قاعدة البيانات
            db_backup_path = os.path.join(backup_path, "database", "supermarket.db")
            if os.path.exists(db_backup_path):
                current_db_path = os.path.join(self.app_path, "supermarket.db")
                shutil.copy2(db_backup_path, current_db_path)
            
            # استعادة الملفات المرفوعة
            uploads_backup_path = os.path.join(backup_path, "uploads")
            if os.path.exists(uploads_backup_path):
                current_uploads_path = os.path.join(self.app_path, "static", "uploads")
                if os.path.exists(current_uploads_path):
                    shutil.rmtree(current_uploads_path)
                shutil.copytree(uploads_backup_path, current_uploads_path)
            
            # استعادة ملفات الإعدادات
            config_backup_path = os.path.join(backup_path, "config")
            if os.path.exists(config_backup_path):
                for config_file in os.listdir(config_backup_path):
                    src = os.path.join(config_backup_path, config_file)
                    dst = os.path.join(self.app_path, config_file)
                    shutil.copy2(src, dst)
            
            return {
                "success": True,
                "message": "تم استعادة النسخة الاحتياطية بنجاح",
                "pre_restore_backup": current_backup
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"فشل في استعادة النسخة الاحتياطية: {e}"
            }
    
    def list_backups(self):
        """عرض قائمة النسخ الاحتياطية"""
        backups = []
        try:
            for item in os.listdir(self.backup_dir):
                item_path = os.path.join(self.backup_dir, item)
                
                # قراءة معلومات النسخة الاحتياطية
                info_file = None
                if os.path.isdir(item_path):
                    info_file = os.path.join(item_path, "backup_info.json")
                elif item.endswith('.zip'):
                    # استخراج معلومات من الملف المضغوط
                    try:
                        with zipfile.ZipFile(item_path, 'r') as zipf:
                            info_content = zipf.read("backup_info.json")
                            backup_info = json.loads(info_content.decode('utf-8'))
                    except:
                        backup_info = {"timestamp": "unknown", "type": "unknown"}
                
                if info_file and os.path.exists(info_file):
                    with open(info_file, 'r', encoding='utf-8') as f:
                        backup_info = json.load(f)
                else:
                    backup_info = {
                        "timestamp": datetime.fromtimestamp(os.path.getctime(item_path)).strftime("%Y%m%d_%H%M%S"),
                        "type": "unknown"
                    }
                
                backup_info["name"] = item
                backup_info["path"] = item_path
                backup_info["size_mb"] = round(self._get_folder_size(item_path) / (1024 * 1024), 2)
                backup_info["created_at"] = datetime.fromtimestamp(os.path.getctime(item_path)).isoformat()
                
                backups.append(backup_info)
            
            # ترتيب حسب تاريخ الإنشاء
            backups.sort(key=lambda x: x["created_at"], reverse=True)
            
        except Exception as e:
            print(f"خطأ في عرض النسخ الاحتياطية: {e}")
        
        return backups
    
    def setup_auto_backup(self):
        """إعداد النسخ الاحتياطي التلقائي"""
        if not self.config["auto_backup_enabled"]:
            return
        
        interval_hours = self.config["backup_interval_hours"]
        schedule.every(interval_hours).hours.do(lambda: self.create_backup("auto"))
        
        # تشغيل المجدول في خيط منفصل
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # فحص كل دقيقة
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        print(f"تم تفعيل النسخ الاحتياطي التلقائي كل {interval_hours} ساعة")
    
    def get_system_info(self):
        """الحصول على معلومات النظام"""
        return {
            "disk_usage": psutil.disk_usage(self.app_path),
            "memory_usage": psutil.virtual_memory(),
            "cpu_percent": psutil.cpu_percent(),
            "backup_dir_size": self._get_folder_size(self.backup_dir),
            "last_backup": self.config.get("last_backup"),
            "total_backups": len(self.list_backups())
        }

# تشغيل النظام
if __name__ == "__main__":
    backup_system = BackupSystem()
    backup_system.setup_auto_backup()
    
    # إنشاء نسخة احتياطية تجريبية
    result = backup_system.create_backup("initial")
    print(result["message"])
