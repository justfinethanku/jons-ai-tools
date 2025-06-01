#!/bin/bash

# Safe Obsolete File Cleanup Script for AI Tools Project
# Generated on 2025-06-01 by Claude Code Analysis
# 
# This script stages potentially obsolete files for review and safe removal.
# Run with --dry-run to see what would be moved without actually moving files.
# Run with --execute to perform the actual staging.

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/Users/jonathanedwards/jons-ai-tools"
STAGING_DIR="$PROJECT_ROOT/obsolete_files_staging"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$STAGING_DIR/backup_$DATE"

# Files to stage for removal (definitely obsolete)
DEFINITELY_OBSOLETE=(
    # Completely unused resources directory
    "resources/__init__.py"
    "resources/copywriting_best_practices.md"
    "resources/write_copy/__init__.py"
    "resources/write_copy/web_copy_tool.py"
    "resources/write_copy/youtube_copy_tool.py"
    
    # Explicitly unused prompts
    "prompts/unused_Prompts/__init__.py"
    "prompts/unused_Prompts/generic_social_copy.py"
    "prompts/unused_Prompts/libsyn_copy.py"
    
    # Test files for non-existent modules
    "xfindandfixshit/tests/unit/test_research_tools_framework.py"
    "xfindandfixshit/tests/integration/test_notion_update.py"
    
    # Empty debug directories (keep only __init__.py files to preserve structure)
    "xfindandfixshit/debug/brand_builder/__init__.py"
    "xfindandfixshit/debug/frameworks/__init__.py"
    "xfindandfixshit/debug/tools/__init__.py"
    "xfindandfixshit/legacy/__init__.py"
    
    # Unreferenced data files (legacy client data)
    "data/content/indelible_inc_content.json"
    "data/content/paulette_michelle_photography_content.json"
    "data/sitemaps/indelible_inc_sitemap.json"
    "data/sitemaps/paulette_michelle_photography_sitemap.json"
)

# Files to investigate further (potentially obsolete)
POTENTIALLY_OBSOLETE=(
    # Empty placeholder directories
    "prompts/random_prompts/__init__.py"
    
    # Debug script (may be used for testing)
    "xfindandfixshit/debug/general/test_token_direct.py"
    
    # Empty creative directories (may be planned for future use)
    "prompts/creative/constraints/"
    "prompts/creative/contexts/"
    "prompts/creative/starters/"
    "prompts/creative/styles/"
    
    # Virtual environment artifacts that might be redundant
    "lib/"
    "include/"
    "bin/"
    "share/"
    "etc/"
)

# Function to print colored output
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to create staging directory
create_staging_dir() {
    if [[ ! -d "$STAGING_DIR" ]]; then
        mkdir -p "$STAGING_DIR"
        print_color $GREEN "Created staging directory: $STAGING_DIR"
    fi
    
    mkdir -p "$BACKUP_DIR"
    print_color $GREEN "Created backup directory: $BACKUP_DIR"
}

# Function to stage a file
stage_file() {
    local file_path="$1"
    local full_path="$PROJECT_ROOT/$file_path"
    
    if [[ -e "$full_path" ]]; then
        local backup_path="$BACKUP_DIR/$file_path"
        local backup_dir=$(dirname "$backup_path")
        
        # Create backup directory structure
        mkdir -p "$backup_dir"
        
        if [[ "$DRY_RUN" == "true" ]]; then
            print_color $YELLOW "DRY RUN: Would move $file_path to staging"
        else
            # Copy to backup first
            cp -r "$full_path" "$backup_path"
            
            # Remove original
            rm -rf "$full_path"
            
            print_color $GREEN "Staged: $file_path"
        fi
    else
        print_color $RED "File not found: $file_path"
    fi
}

# Function to stage directory if empty
stage_empty_directory() {
    local dir_path="$1"
    local full_path="$PROJECT_ROOT/$dir_path"
    
    if [[ -d "$full_path" ]]; then
        # Check if directory is empty (only contains . and ..)
        if [[ -z "$(ls -A "$full_path")" ]]; then
            if [[ "$DRY_RUN" == "true" ]]; then
                print_color $YELLOW "DRY RUN: Would remove empty directory $dir_path"
            else
                rmdir "$full_path"
                print_color $GREEN "Removed empty directory: $dir_path"
            fi
        fi
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [--dry-run|--execute] [--include-potential]"
    echo ""
    echo "Options:"
    echo "  --dry-run           Show what would be staged without moving files (default)"
    echo "  --execute           Actually stage the files for removal"
    echo "  --include-potential Include potentially obsolete files (use with caution)"
    echo "  --help              Show this help message"
    echo ""
    echo "The script will create a staging directory with backups before removing files."
    echo "Files are categorized as 'definitely obsolete' or 'potentially obsolete'."
}

# Main execution function
main() {
    local include_potential=false
    
    # Parse command line arguments
    DRY_RUN="true"  # Default to dry run for safety
    
    for arg in "$@"; do
        case $arg in
            --dry-run)
                DRY_RUN="true"
                ;;
            --execute)
                DRY_RUN="false"
                ;;
            --include-potential)
                include_potential=true
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                print_color $RED "Unknown option: $arg"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Change to project directory
    cd "$PROJECT_ROOT"
    
    # Print header
    print_color $BLUE "==============================================="
    print_color $BLUE "AI Tools Obsolete File Cleanup Script"
    print_color $BLUE "==============================================="
    echo ""
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_color $YELLOW "DRY RUN MODE - No files will be moved"
        print_color $YELLOW "Run with --execute to perform actual staging"
    else
        print_color $RED "EXECUTE MODE - Files will be moved to staging"
        create_staging_dir
    fi
    
    echo ""
    
    # Stage definitely obsolete files
    print_color $BLUE "Processing DEFINITELY OBSOLETE files:"
    echo ""
    
    for file in "${DEFINITELY_OBSOLETE[@]}"; do
        stage_file "$file"
    done
    
    # Stage potentially obsolete files if requested
    if [[ "$include_potential" == "true" ]]; then
        echo ""
        print_color $BLUE "Processing POTENTIALLY OBSOLETE files:"
        print_color $YELLOW "WARNING: These files may still be needed!"
        echo ""
        
        for file in "${POTENTIALLY_OBSOLETE[@]}"; do
            stage_file "$file"
        done
    fi
    
    # Clean up empty directories
    echo ""
    print_color $BLUE "Checking for empty directories to remove:"
    echo ""
    
    # List of directories that might become empty
    local dirs_to_check=(
        "resources/write_copy"
        "resources"
        "prompts/unused_Prompts"
        "data/content"
        "data/sitemaps"
        "data"
        "xfindandfixshit/debug/brand_builder"
        "xfindandfixshit/debug/frameworks"
        "xfindandfixshit/debug/tools"
        "xfindandfixshit/legacy"
    )
    
    for dir in "${dirs_to_check[@]}"; do
        stage_empty_directory "$dir"
    done
    
    # Final summary
    echo ""
    print_color $BLUE "==============================================="
    print_color $BLUE "Summary"
    print_color $BLUE "==============================================="
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_color $YELLOW "This was a DRY RUN. No files were actually moved."
        print_color $YELLOW "Run with --execute to perform the actual staging."
    else
        print_color $GREEN "Files have been staged for removal in: $STAGING_DIR"
        print_color $GREEN "Backups created in: $BACKUP_DIR"
        print_color $BLUE "Review the staged files before permanently deleting them."
    fi
    
    echo ""
    print_color $BLUE "To restore files if needed:"
    print_color $BLUE "cp -r $BACKUP_DIR/* $PROJECT_ROOT/"
    
    echo ""
    print_color $BLUE "To permanently delete staged files:"
    print_color $BLUE "rm -rf $STAGING_DIR"
}

# Check if we're in the right directory
if [[ ! -f "app.py" ]]; then
    print_color $RED "Error: This script must be run from the AI Tools project root directory."
    print_color $RED "Expected to find app.py in current directory."
    exit 1
fi

# Run main function
main "$@"