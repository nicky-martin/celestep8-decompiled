# Celeste PICO-8 Decompiler

Modified Python scripts that decompile the PICO-8 game *Celeste* from its .p8.png cartridge format, revealing how game data is steganographically embedded in pixel color channels.

This project demonstrates the step-by-step extraction process: bit extraction → byte assembly → decompression → Lua script output. The included output files show each stage of decompilation for analysis and preservation research.

## Attribution

Based on [rvaccarim's p8png_decoder](https://github.com/rvaccarim/p8png_decoder).  
Original code © 2021 rvaccarim, MIT License.  
Modifications © 2025 nicky-martin, MIT License.

## Usage

```bash
pip install -r requirements.txt
python src/decoder.py celeste.p8.png
```

See `output/` folder for example decompilation results.# celestep8-decompiled
Decompiling Celeste PICO-8 cartridge step-by-step, demonstrating steganographic data extraction. Modified version of rvaccarim's p8png_decoder.
