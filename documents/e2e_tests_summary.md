# Viral AI Video Generation Platform - E2E Tests Summary

This document provides a summary of the end-to-end (E2E) tests for the Viral AI Video Generation Platform.

## Overview

The E2E tests are located in the `tests/e2e/` directory. They are designed to test the entire video generation workflow, from the user's prompt to the final video output.

## Test Suites

The E2E tests are organized into the following suites:

*   `test_full_system.py`: Tests the full video generation pipeline, including the multi-agent discussion, script generation, video generation, and video editing.
*   `test_full_system_integration.py`: A recently added test that covers the full end-to-end flow of generating a video.

## Running the Tests

The E2E tests can be run using the following command:

```
pytest tests/e2e/
```

## Coverage

The E2E tests cover the following key areas of the system:

*   **User Workflow**: The tests simulate a user's interaction with the platform, from providing a prompt to receiving the final video.
*   **Full Pipeline**: The tests ensure that the entire video generation pipeline is working correctly, from start to finish.
*   **Output Validation**: The tests validate the output of the video generation pipeline, ensuring that the final video is generated correctly and meets the user's specifications. 