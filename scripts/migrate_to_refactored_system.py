#!/usr/bin/env python3
"""
Migration Script - Transition to Refactored Video Generation System

This script helps migrate from the old distributed duration management
to the new centralized, audio-first approach.
"""

import os
import sys
import logging
import argparse
import shutil
from pathlib import Path
from typing import List, Dict, Any

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from src.core.duration_authority import DurationAuthority
from src.utils.audio_first_subtitle_generator import AudioFirstSubtitleGenerator
from src.utils.simplified_audio_processor import SimplifiedAudioProcessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SystemMigrator:
    """Migrates video generation system to refactored architecture"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.src_path = self.project_root / "src"
        self.backup_path = self.project_root / "backups" / "pre_refactor"
        
        logger.info(f"🔄 System Migrator initialized")
        logger.info(f"   Project root: {self.project_root}")
        logger.info(f"   Backup location: {self.backup_path}")
        
    def create_backup(self, components_to_backup: List[str]) -> bool:
        """Create backup of existing components before migration"""
        logger.info("💾 Creating backup of existing components")
        
        try:
            self.backup_path.mkdir(parents=True, exist_ok=True)
            
            for component in components_to_backup:
                src_file = self.src_path / component
                if src_file.exists():
                    backup_file = self.backup_path / component
                    backup_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_file, backup_file)
                    logger.info(f"   ✅ Backed up: {component}")
                else:
                    logger.warning(f"   ⚠️ Not found: {component}")
                    
            logger.info("✅ Backup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            return False
            
    def update_imports_in_file(self, file_path: Path, import_updates: Dict[str, str]) -> bool:
        """Update import statements in a file"""
        if not file_path.exists():
            logger.warning(f"⚠️ File not found: {file_path}")
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # Apply import updates
            for old_import, new_import in import_updates.items():
                content = content.replace(old_import, new_import)
                
            # Only write if content changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"   ✅ Updated imports in: {file_path.name}")
                return True
            else:
                logger.debug(f"   ℹ️ No changes needed in: {file_path.name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to update {file_path}: {e}")
            return False
            
    def remove_hardcoded_durations(self) -> bool:
        """Remove hardcoded duration values from key files"""
        logger.info("🔧 Removing hardcoded duration values")
        
        files_to_update = [
            {
                'path': 'generators/video_generator.py',
                'patterns': [
                    ('duration_seconds=15', 'duration_seconds'),
                    ('duration_seconds: int = 10', 'duration_seconds: int'),
                    ('hook_duration = 2.5', 'hook_duration = min(3.0, max(1.5, video_duration * 0.08))'),
                ]
            },
            {
                'path': 'agents/image_timing_agent.py', 
                'patterns': [
                    ('duration = 7.0', 'duration = self.calculate_base_duration(target_duration, num_images)'),
                ]
            },
            {
                'path': 'agents/voice_director_agent.py',
                'patterns': [
                    ('duration_seconds: int = 10', 'duration_seconds: int'),
                ]
            },
            {
                'path': 'agents/overlay_positioning_agent.py',
                'patterns': [
                    ('hook_duration = 2.5', 'hook_duration = min(3.0, max(1.5, video_duration * 0.08))'),
                ]
            }
        ]
        
        success_count = 0
        
        for file_info in files_to_update:
            file_path = self.src_path / file_info['path']
            
            if not file_path.exists():
                logger.warning(f"⚠️ File not found: {file_path}")
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                original_content = content
                
                # Apply pattern replacements
                for old_pattern, new_pattern in file_info['patterns']:
                    if old_pattern in content:
                        content = content.replace(old_pattern, new_pattern)
                        logger.info(f"   🔄 Replaced: {old_pattern} → {new_pattern}")
                        
                # Write back if changed
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info(f"   ✅ Updated: {file_path.name}")
                    success_count += 1
                    
            except Exception as e:
                logger.error(f"❌ Failed to update {file_path}: {e}")
                
        logger.info(f"✅ Updated {success_count}/{len(files_to_update)} files")
        return success_count > 0
        
    def add_duration_authority_integration(self) -> bool:
        """Add duration authority integration to existing components"""
        logger.info("🎯 Adding Duration Authority integration")
        
        # Key files that need Duration Authority integration
        integration_files = [
            'workflows/generate_viral_video.py',
            'generators/video_generator.py',
            'generators/enhanced_script_processor.py',
        ]
        
        duration_authority_import = """
# Import refactored duration management
from ..core.duration_authority import DurationAuthority, ComponentType
"""
        
        success_count = 0
        
        for file_name in integration_files:
            file_path = self.src_path / file_name
            
            if not file_path.exists():
                logger.warning(f"⚠️ File not found: {file_path}")
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check if already has duration authority import
                if 'duration_authority' in content.lower():
                    logger.info(f"   ℹ️ Already integrated: {file_path.name}")
                    continue
                    
                # Add import after existing imports (find last import line)
                lines = content.split('\n')
                import_end_index = 0
                
                for i, line in enumerate(lines):
                    if line.strip().startswith('from ') or line.strip().startswith('import '):
                        import_end_index = i
                        
                # Insert duration authority import
                lines.insert(import_end_index + 1, duration_authority_import)
                
                updated_content = '\n'.join(lines)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                    
                logger.info(f"   ✅ Added Duration Authority to: {file_path.name}")
                success_count += 1
                
            except Exception as e:
                logger.error(f"❌ Failed to integrate {file_path}: {e}")
                
        logger.info(f"✅ Integrated Duration Authority in {success_count} files")
        return success_count > 0
        
    def create_migration_summary(self) -> Dict[str, Any]:
        """Create summary of migration changes"""
        summary = {
            'migration_type': 'Audio-Subtitle Sync Refactor',
            'timestamp': self._get_timestamp(),
            'changes_made': [
                'Created centralized Duration Authority',
                'Implemented audio-first subtitle generation',
                'Added simplified audio processing',
                'Removed hardcoded duration defaults',
                'Updated import statements',
            ],
            'new_components': [
                'src/core/duration_authority.py',
                'src/utils/audio_first_subtitle_generator.py', 
                'src/utils/simplified_audio_processor.py',
                'src/generators/refactored_video_generator.py',
            ],
            'deprecated_components': [
                'Complex filter chains in ffmpeg_processor.py',
                'Estimation-based subtitle generation',
                'Distributed duration management',
            ],
            'benefits': [
                'Eliminates audio-subtitle sync issues',
                'Prevents audio stuttering artifacts',
                'Ensures consistent duration management',
                'Improves video generation reliability',
            ]
        }
        
        return summary
        
    def run_migration(self, dry_run: bool = False) -> bool:
        """Run the complete migration process"""
        logger.info("🚀 Starting system migration to refactored architecture")
        
        if dry_run:
            logger.info("   🔍 DRY RUN MODE - No files will be modified")
            
        # Components to backup before migration  
        components_to_backup = [
            'generators/video_generator.py',
            'utils/ffmpeg_processor.py', 
            'generators/enhanced_script_processor.py',
            'utils/duration_coordinator.py',
            'utils/audio_duration_manager.py',
        ]
        
        if not dry_run:
            # Step 1: Create backup
            if not self.create_backup(components_to_backup):
                logger.error("❌ Migration aborted - backup failed")
                return False
                
        # Step 2: Remove hardcoded durations
        if not dry_run:
            self.remove_hardcoded_durations()
            
        # Step 3: Add Duration Authority integration
        if not dry_run:
            self.add_duration_authority_integration()
            
        # Step 4: Create migration summary
        summary = self.create_migration_summary()
        
        if not dry_run:
            summary_path = self.project_root / 'MIGRATION_SUMMARY.md'
            self._write_migration_summary(summary, summary_path)
            
        logger.info("✅ Migration completed successfully!")
        logger.info("📄 Next steps:")
        logger.info("   1. Run tests: python -m pytest tests/test_refactored_video_generation.py")
        logger.info("   2. Test video generation with new system")
        logger.info("   3. Compare results with old system")
        logger.info("   4. Update documentation and deployment scripts")
        
        return True
        
    def _get_timestamp(self) -> str:
        """Get current timestamp for migration tracking"""
        from datetime import datetime
        return datetime.now().isoformat()
        
    def _write_migration_summary(self, summary: Dict[str, Any], output_path: Path):
        """Write migration summary to markdown file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("# Video Generation System Migration Summary\n\n")
                f.write(f"**Migration Type:** {summary['migration_type']}\n")
                f.write(f"**Timestamp:** {summary['timestamp']}\n\n")
                
                f.write("## Changes Made\n")
                for change in summary['changes_made']:
                    f.write(f"- {change}\n")
                f.write("\n")
                
                f.write("## New Components\n")
                for component in summary['new_components']:
                    f.write(f"- `{component}`\n")
                f.write("\n")
                
                f.write("## Deprecated Components\n")
                for component in summary['deprecated_components']:
                    f.write(f"- {component}\n")
                f.write("\n")
                
                f.write("## Benefits\n")
                for benefit in summary['benefits']:
                    f.write(f"- {benefit}\n")
                f.write("\n")
                
                f.write("## Testing\n")
                f.write("Run the test suite to validate the migration:\n")
                f.write("```bash\n")
                f.write("python -m pytest tests/test_refactored_video_generation.py -v\n")
                f.write("```\n\n")
                
                f.write("## Rollback\n")
                f.write("If issues occur, restore from backup:\n")
                f.write(f"- Backup location: `{self.backup_path}`\n")
                f.write("- Restore files from backup if needed\n")
                
            logger.info(f"📄 Migration summary written to: {output_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to write migration summary: {e}")


def main():
    """Main migration script entry point"""
    parser = argparse.ArgumentParser(description='Migrate to refactored video generation system')
    parser.add_argument('--project-root', default='.', help='Project root directory')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without modifying files')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    # Initialize migrator
    migrator = SystemMigrator(args.project_root)
    
    # Run migration
    success = migrator.run_migration(dry_run=args.dry_run)
    
    if success:
        logger.info("🎉 Migration completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 Migration failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()