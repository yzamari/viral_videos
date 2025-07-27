# Release Notes

## v3.2.0-rc1 (July 27, 2025)

### 🎉 New Features

#### 🎓 University Theme & Custom Overlays
- **New `preset_university` theme**: Professional academic theme designed for educational content
- **Integrated logo overlays**: Themes now support automatic PNG logo overlays
- **AI University branding**: Complete educational branding kit with logo generation
- **Smart positioning**: Logos automatically positioned with proper padding and animations
- **Theme-based overlay management**: Logo configuration is part of theme definition

#### 📺 Enhanced Episode Selection
- **Selective episode generation**: Use `-e` or `--episodes` flag to generate specific episodes
- **Multiple episode support**: Generate batches like `-e 1 3 5 7`
- **Universal implementation**: Works across all series scripts (Educational, News, Israeli PM)
- **Parallel compatibility**: Episode selection works with parallel generation (`-p` flag)
- **Help documentation**: All scripts now include episode listing with `-h` flag

### 🔧 Improvements

#### Script Enhancements
- **Bash compatibility fixes**: Removed associative arrays for older bash version support
- **Parallel generation optimization**: Fixed concurrent episode generation issues
- **Better error handling**: Improved error messages and recovery mechanisms
- **Progress tracking**: Enhanced logging for multi-episode generation

#### Theme System Updates
- **Logo overlay support**: All themes can now include custom PNG overlays
- **Position control**: Configure logo position, size, opacity, and animation
- **Brand consistency**: Maintain visual identity across all generated videos
- **Educational focus**: New academic styling options for learning content

### 🐛 Bug Fixes
- Fixed bash `declare -A` errors in parallel generation script
- Fixed `--overlay` option to use theme system instead
- Resolved theme registration issues in theme manager
- Fixed episode data validation in series scripts

### 📚 Documentation Updates
- Updated README.md with v3.2.0-rc1 features
- Enhanced SYSTEM_ARCHITECTURE.md with theme system details
- Added university theme documentation
- Updated series generation examples

### 🔄 Migration Notes
- Replace `--overlay` with `--theme preset_university` for logo overlays
- Update bash scripts if using associative arrays
- Logo files should be PNG format with transparent backgrounds
- Themes now handle all overlay management

### 💡 Usage Examples

```bash
# Generate calculus series with university branding
./run_calculus_baby_dragon_series.sh -e 1 2 3

# Use parallel generation with episode selection
./run_calculus_baby_dragon_series_parallel.sh -e 1 5 9 -p 3

# Apply university theme to any generation
python3 main.py generate \
  --mission "Your educational content" \
  --theme preset_university \
  --platform instagram
```

### 🙏 Acknowledgments
- Thanks to all contributors who reported bash compatibility issues
- Special thanks for feedback on educational content needs

---

## Previous Releases

### v3.1.0 (July 2025)
- Universal AI Provider Interface
- Enhanced configuration system with zero hardcoding
- Critical bug fixes for VEO generation
- Character consistency system
- Style reference system implementation

### v3.0.0 (July 2025)
- Initial release of centralized decision framework
- 22-agent AI collaboration system
- Multi-language support
- Professional video generation modes