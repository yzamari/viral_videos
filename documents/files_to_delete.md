# Viral AI Video Generation Platform - Files to Delete

This document lists the files that can be safely deleted from the project. These files are either temporary, backups, or no longer used.

## Temporary Files

*   `11771925140-v5mqfkq7em7g9n8u4fl6dfulo63e`
*   `csv=p=0`

## Backup Files

*   `src/agents/multi_agent_discussion.py.backup_20250713_201745`
*   `src/generators/video_generator.py.backup`
*   `src/generators/video_generator.py.backup_20250713_201745`

## Redundant or Unused Files

*   The numerous `fix_*.py` and `test_*.py` scripts in the root directory appear to be from previous debugging and testing sessions. These should be reviewed and either integrated into the `tests/` directory or deleted.
*   The numerous `*_SUMMARY.md`, `*_STATUS.md`, `*_NOTES.md` and similar markdown files in the root directory appear to be from previous sessions. These should be reviewed and either integrated into the `docs/` directory or deleted.

## Image and Test Output Files

*   The `ui_verification_*.png` and `ui_test_results.json` files in the root directory are likely from previous UI testing and can be deleted.
*   The `test-output/` and `test_output/` directories and their contents can be deleted.

**Note:** Before deleting any files, it is recommended to create a backup of the project. 