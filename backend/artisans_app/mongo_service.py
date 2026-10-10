"""
MongoDB Document Database Service
Handles unstructured telemetry, deep AI spectral analysis logs, sensory readings, and artisan heritage archives.
Integrates PyMongo with automatic local persistent fallback if MongoDB daemon is offline.
"""

import os
import json
import uuid
import datetime
from pathlib import Path

try:
    from pymongo import MongoClient
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False

DATA_DIR = Path(__file__).resolve().parent.parent / 'data'
DATA_DIR.mkdir(exist_ok=True)
VAULT_FILE = DATA_DIR / 'mongo_document_vault.json'

class MongoVaultService:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="artisan_market_db"):
        self.uri = uri
        self.db_name = db_name
        self.is_connected = False
        self.client = None
        self.db = None
        
        # Try connecting to live MongoDB
        if PYMONGO_AVAILABLE:
            try:
                self.client = MongoClient(self.uri, serverSelectionTimeoutMS=1000)
                # Check connection
                self.client.server_info()
                self.db = self.client[self.db_name]
                self.is_connected = True
                print(f"[MongoDB] Connected successfully to live MongoDB at {self.uri} (DB: {self.db_name})")
            except Exception as e:
                self.is_connected = False
                print(f"[MongoDB] Live server not detected ({e}). Using embedded high-performance document vault.")
        else:
            print("[MongoDB] PyMongo not present; utilizing JSON document vault.")
            
        self._init_vault()

    def _init_vault(self):
        if not VAULT_FILE.exists():
            default_data = {
                'ai_spectral_scans': [],
                'artisan_heritage_stories': [],
                'telemetry_sensor_logs': [],
                'audit_events': []
            }
            with open(VAULT_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=2)

    def _read_vault(self):
        try:
            with open(VAULT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {'ai_spectral_scans': [], 'artisan_heritage_stories': [], 'telemetry_sensor_logs': [], 'audit_events': []}

    def _write_vault(self, data):
        with open(VAULT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

    # 1. AI Spectral Scan Documents (Unstructured Computer Vision + Spectral analysis)
    def insert_spectral_scan(self, document):
        doc = dict(document)
        doc['_id'] = str(uuid.uuid4())
        doc['timestamp'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        if self.is_connected and self.db is not None:
            try:
                self.db['ai_spectral_scans'].insert_one(dict(doc))
            except Exception as e:
                print(f"[MongoDB Error] {e}, falling back to vault")
                
        # Always mirror to document vault for seamless dual persistence
        data = self._read_vault()
        data['ai_spectral_scans'].insert(0, doc)
        # keep last 100
        data['ai_spectral_scans'] = data['ai_spectral_scans'][:100]
        self._write_vault(data)
        return doc

    def get_spectral_scans(self, limit=20):
        if self.is_connected and self.db is not None:
            try:
                cursor = self.db['ai_spectral_scans'].find({}, {'_id': 0}).sort('timestamp', -1).limit(limit)
                return list(cursor)
            except Exception:
                pass
        data = self._read_vault()
        return data.get('ai_spectral_scans', [])[:limit]

    # 2. Artisan Heritage Stories & Multi-Media Archives
    def insert_artisan_story(self, story):
        doc = dict(story)
        doc['_id'] = str(uuid.uuid4())
        doc['created_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        if self.is_connected and self.db is not None:
            try:
                self.db['artisan_heritage_stories'].insert_one(dict(doc))
            except Exception:
                pass
                
        data = self._read_vault()
        data['artisan_heritage_stories'].insert(0, doc)
        self._write_vault(data)
        return doc

    def get_artisan_stories(self, category=None):
        data = self._read_vault()
        stories = data.get('artisan_heritage_stories', [])
        if category:
            stories = [s for s in stories if s.get('category') == category]
        return stories

    # 3. Security & Transaction Audit Logs
    def log_audit(self, action, user, metadata=None):
        doc = {
            '_id': str(uuid.uuid4()),
            'action': action,
            'user': user,
            'metadata': metadata or {},
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        data = self._read_vault()
        data['audit_events'].insert(0, doc)
        data['audit_events'] = data['audit_events'][:200]
        self._write_vault(data)
        return doc

# Global Singleton instance
mongo_service = MongoVaultService()
