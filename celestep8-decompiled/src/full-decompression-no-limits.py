import re

# Read from the FULL bit extraction file (includes all bytes)
with open("celeste-bits.txt", "r") as f:
    content = f.read()

# Extract ALL decimal values from byte position 17152 onwards (the code section starts at 0x4300)
all_decimals = re.findall(r'\[byte position (\d+)\].*?decimal:\s+(\d+)', content, re.DOTALL)

# Filter to only get bytes from position 17152 onwards (0x4300 = start of code)
code_section = [(int(pos), int(val)) for pos, val in all_decimals if int(pos) >= 17152]
code_section.sort(key=lambda x: x[0])  # Sort by position
decimal_values = [val for pos, val in code_section]

print(f"Extracted {len(decimal_values)} bytes from code section")
print("Starting FULL decompression trace - this will take a while and create a large file...")

# This is the character lookup table used by OLD_COMPRESSED_FORMAT
CHAR_TABLE = ' \n 0123456789abcdefghijklmnopqrstuvwxyz!#%(){}[]<>+=/*:;.,~_'

# Open debug output file
with open("celeste-decompression-FULL.txt", "w") as out:
    out.write("=" * 80 + "\n")
    out.write("CELESTE OLD_COMPRESSED_FORMAT FULL DECOMPRESSION TRACE\n")
    out.write("=" * 80 + "\n\n")
    
    out.write("STEP 1: Read compression header\n")
    out.write("-" * 80 + "\n")
    out.write(f"Bytes 0-3: {decimal_values[0:4]}\n")
    out.write(f"  = '{chr(decimal_values[0])}{chr(decimal_values[1])}{chr(decimal_values[2])}' + null byte\n")
    out.write("This is the OLD_COMPRESSED_FORMAT marker: ':c:\\x00'\n\n")
    
    # Bytes 4-5: decompressed length (MSB first)
    decompressed_length = (decimal_values[4] << 8) | decimal_values[5]
    out.write(f"Bytes 4-5: {decimal_values[4]}, {decimal_values[5]}\n")
    out.write(f"Decompressed code length = ({decimal_values[4]} << 8) | {decimal_values[5]} = {decompressed_length} bytes\n\n")
    
    out.write(f"Bytes 6-7: {decimal_values[6]}, {decimal_values[7]} (should be zero)\n\n")
    
    out.write("=" * 80 + "\n")
    out.write("STEP 2: Decompress the data byte-by-byte (ALL STEPS)\n")
    out.write("=" * 80 + "\n\n")
    
    code = []
    code_pos = 8  # Start after 8-byte header
    step_count = 0
    
    while len(code) < decompressed_length and code_pos < len(decimal_values):
        curr_byte = decimal_values[code_pos]
        step_count += 1
        
        # Progress indicator every 1000 steps
        if step_count % 1000 == 0:
            print(f"  Progress: {step_count} steps, {len(code)} chars decompressed...")
        
        out.write(f"\n--- Step {step_count} (byte position {code_pos + 17152}) ---\n")
        out.write(f"Current byte: {curr_byte} (0x{curr_byte:02x}, binary: {curr_byte:08b})\n")
        
        if curr_byte == 0x00:
            # 0x00: Copy next byte directly
            if code_pos + 1 >= len(decimal_values):
                break
            next_byte = decimal_values[code_pos + 1]
            char = chr(next_byte)
            out.write(f"Action: 0x00 = LITERAL CHARACTER\n")
            out.write(f"  Next byte: {next_byte} = '{char}'\n")
            code.append(char)
            code_pos += 2
            
        elif curr_byte <= 0x3b:
            # 0x01-0x3b: Character from lookup table
            char = CHAR_TABLE[curr_byte]
            out.write(f"Action: LOOKUP TABLE (0x01-0x3B)\n")
            out.write(f"  Table index: {curr_byte}\n")
            out.write(f"  Character from table: '{char}'\n")
            code.append(char)
            code_pos += 1
            
        else:
            # 0x3c-0xff: Copy from previous output
            if code_pos + 1 >= len(decimal_values):
                break
            next_byte = decimal_values[code_pos + 1]
            
            offset = (curr_byte - 0x3c) * 16 + (next_byte & 0xf)
            length = (next_byte >> 4) + 2
            
            out.write(f"Action: COPY FROM HISTORY (0x3C-0xFF)\n")
            out.write(f"  Current: {curr_byte} (0x{curr_byte:02x}), Next: {next_byte} (0x{next_byte:02x})\n")
            out.write(f"  Offset: ({curr_byte} - 60) * 16 + ({next_byte} & 15) = {offset} chars back\n")
            out.write(f"  Length: ({next_byte} >> 4) + 2 = {length} chars\n")
            
            index = len(code) - offset
            if index < 0 or index >= len(code):
                out.write(f"  ERROR: Invalid offset (current output is only {len(code)} chars)\n")
                break
                
            chunk = ""
            for i in range(length):
                chunk += code[index + i]
            out.write(f"  Copying: '{chunk}'\n")
            code.extend(chunk)
            code_pos += 2
        
        # Show current output
        current_output = ''.join(code)
        preview = current_output[-80:] if len(current_output) > 80 else current_output
        out.write(f"Output so far ({len(code)} chars): ...{preview}\n")
    
    out.write("\n" + "=" * 80 + "\n")
    out.write(f"FINAL COMPLETE OUTPUT ({len(code)} bytes):\n")
    out.write("=" * 80 + "\n\n")
    
    final_code = ''.join(code)
    out.write(final_code)
    
    out.write("\n\n" + "=" * 80 + "\n")
    out.write(f"DECOMPRESSION COMPLETE\n")
    out.write(f"Total steps: {step_count}\n")
    out.write(f"Output length: {len(code)} bytes (expected: {decompressed_length})\n")
    out.write("=" * 80 + "\n")

print("✓ FULL decompression trace saved to celeste-decompression-FULL.txt")
print(f"✓ Processed {step_count} decompression steps")
print(f"✓ Total output: {len(code)} bytes")