"""
Load GTFS data into SQLite database for fast querying
"""

import sqlite3
import pandas as pd
from pathlib import Path
import time

GTFS_DATA_DIR = Path(__file__).parent.parent / "gtfs_data"
DB_PATH = Path(__file__).parent.parent / "database" / "transit.db"

class GTFSLoader:
    def __init__(self, gtfs_dir=GTFS_DATA_DIR, db_path=DB_PATH):
        self.gtfs_dir = Path(gtfs_dir)
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
    def load_all(self, force=False):
        """Load all GTFS files into database"""
        
        if not force and self.db_path.exists():
            print(f"✓ Database already exists at {self.db_path}")
            print("  Use force=True to rebuild")
            return
        
        print(f"Loading GTFS data from {self.gtfs_dir}...")
        start_time = time.time()
        
        # Check if GTFS files exist
        required_files = ['routes.txt', 'stops.txt', 'trips.txt', 'stop_times.txt']
        missing = [f for f in required_files if not (self.gtfs_dir / f).exists()]
        
        if missing:
            print(f"✗ Missing GTFS files: {missing}")
            print(f"\nPlease download GTFS data to: {self.gtfs_dir}")
            print("See GTFS_SETUP.md for instructions")
            return False
        
        # Create database connection
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Load each GTFS file
            self._load_routes(conn)
            self._load_stops(conn)
            self._load_trips(conn)
            self._load_stop_times(conn)
            self._load_calendar(conn)
            
            # Create indexes for fast queries
            self._create_indexes(conn)
            
            # Print statistics
            self._print_stats(conn)
            
            conn.commit()
            elapsed = time.time() - start_time
            print(f"\n✓ Database created successfully in {elapsed:.1f}s")
            print(f"  Location: {self.db_path}")
            print(f"  Size: {self.db_path.stat().st_size / 1024 / 1024:.1f} MB")
            
            return True
            
        except Exception as e:
            print(f"✗ Error loading GTFS data: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _load_routes(self, conn):
        """Load routes.txt"""
        print("Loading routes...")
        df = pd.read_csv(self.gtfs_dir / 'routes.txt')
        df.to_sql('routes', conn, if_exists='replace', index=False)
        print(f"  ✓ Loaded {len(df)} routes")
    
    def _load_stops(self, conn):
        """Load stops.txt"""
        print("Loading stops...")
        df = pd.read_csv(self.gtfs_dir / 'stops.txt')
        df.to_sql('stops', conn, if_exists='replace', index=False)
        print(f"  ✓ Loaded {len(df)} stops")
    
    def _load_trips(self, conn):
        """Load trips.txt"""
        print("Loading trips...")
        df = pd.read_csv(self.gtfs_dir / 'trips.txt')
        df.to_sql('trips', conn, if_exists='replace', index=False)
        print(f"  ✓ Loaded {len(df)} trips")
    
    def _load_stop_times(self, conn):
        """Load stop_times.txt (this is the largest file)"""
        print("Loading stop_times (this may take a while)...")
        
        # Load in chunks to handle large files
        chunk_size = 100000
        chunks = pd.read_csv(self.gtfs_dir / 'stop_times.txt', chunksize=chunk_size)
        
        total_rows = 0
        for i, chunk in enumerate(chunks):
            chunk.to_sql('stop_times', conn, if_exists='append' if i > 0 else 'replace', index=False)
            total_rows += len(chunk)
            print(f"  ... {total_rows:,} rows loaded", end='\r')
        
        print(f"\n  ✓ Loaded {total_rows:,} stop times")
    
    def _load_calendar(self, conn):
        """Load calendar.txt"""
        calendar_file = self.gtfs_dir / 'calendar.txt'
        if calendar_file.exists():
            print("Loading calendar...")
            df = pd.read_csv(calendar_file)
            df.to_sql('calendar', conn, if_exists='replace', index=False)
            print(f"  ✓ Loaded {len(df)} calendar entries")
        else:
            print("  ⚠ calendar.txt not found (optional)")
    
    def _create_indexes(self, conn):
        """Create indexes for fast queries"""
        print("Creating indexes...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_routes_id ON routes(route_id)",
            "CREATE INDEX IF NOT EXISTS idx_stops_id ON stops(stop_id)",
            "CREATE INDEX IF NOT EXISTS idx_stops_location ON stops(stop_lat, stop_lon)",
            "CREATE INDEX IF NOT EXISTS idx_trips_route ON trips(route_id)",
            "CREATE INDEX IF NOT EXISTS idx_trips_id ON trips(trip_id)",
            "CREATE INDEX IF NOT EXISTS idx_stop_times_trip ON stop_times(trip_id)",
            "CREATE INDEX IF NOT EXISTS idx_stop_times_stop ON stop_times(stop_id)",
            "CREATE INDEX IF NOT EXISTS idx_stop_times_time ON stop_times(arrival_time)",
        ]
        
        for idx_sql in indexes:
            conn.execute(idx_sql)
        
        print(f"  ✓ Created {len(indexes)} indexes")
    
    def _print_stats(self, conn):
        """Print database statistics"""
        print("\nDatabase Statistics:")
        
        tables = ['routes', 'stops', 'trips', 'stop_times']
        for table in tables:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count:,} rows")

def main():
    """Main entry point"""
    loader = GTFSLoader()
    success = loader.load_all()
    
    if success:
        print("\n✓ GTFS data is ready!")
        print("  You can now start the route planning server")
    else:
        print("\n✗ Please download GTFS data first")
        print("  See GTFS_SETUP.md for instructions")

if __name__ == "__main__":
    main()
