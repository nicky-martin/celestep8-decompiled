import re

# Read the decimal byte values from your bitstream file
with open("celeste-bitstream.txt", "r") as f:
    content = f.read()
    # Extract the decimal values line
    decimal_line = re.search(r'DECIMAL BYTE VALUES.*\n.*\n([\d,]+)', content, re.DOTALL)
    decimal_values = [int(x) for x in decimal_line.group(1).strip().split(',')]

# This is the character lookup table used by OLD_COMPRESSED_FORMAT
CHAR_TABLE = ' \n 0123456789abcdefghijklmnopqrstuvwxyz!#%(){}[]<>+=/*:;.,~_'

# Open debug output file
with open("celeste-decompression-steps.txt", "w") as out:
    out.write("=" * 80 + "\n")
    out.write("CELESTE OLD_COMPRESSED_FORMAT DECOMPRESSION TRACE\n")
    out.write("=" * 80 + "\n\n")
    
    # The header starts at byte position 17152 (but in our extracted data, it's position 0)
    # Format: :c:\x00 [length_msb] [length_lsb] [0x00] [0x00] [compressed_data...]
    
    out.write("STEP 1: Read compression header\n")
    out.write("-" * 80 + "\n")
    out.write(f"Bytes 0-3: {decimal_values[0:4]} = '{chr(decimal_values[0])}{chr(decimal_values[1])}{chr(decimal_values[2])}\\x00'\n")
    out.write("This is the OLD_COMPRESSED_FORMAT marker: ':c:\\x00'\n\n")
    
    # Bytes 4-5: decompressed length (MSB first)
    decompressed_length = (decimal_values[4] << 8) | decimal_values[5]
    out.write(f"Bytes 4-5: {decimal_values[4]}, {decimal_values[5]}\n")
    out.write(f"Decompressed code length = ({decimal_values[4]} << 8) | {decimal_values[5]} = {decompressed_length} bytes\n\n")
    
    out.write(f"Bytes 6-7: {decimal_values[6]}, {decimal_values[7]} (always zero)\n\n")
    
    out.write("=" * 80 + "\n")
    out.write("STEP 2: Decompress the data byte-by-byte\n")
    out.write("=" * 80 + "\n\n")
    
    code = []
    code_pos = 8  # Start after 8-byte header
    step_count = 0
    max_steps = 200  # Limit output for readability
    
    while len(code) < decompressed_length and step_count < max_steps:
        curr_byte = decimal_values[code_pos]
        step_count += 1
        
        out.write(f"\n--- Step {step_count} (byte position {code_pos}) ---\n")
        out.write(f"Current byte: {curr_byte} (0x{curr_byte:02x}, binary: {curr_byte:08b})\n")
        
        if curr_byte == 0x00:
            # 0x00: Copy next byte directly
            next_byte = decimal_values[code_pos + 1]
            char = chr(next_byte)
            out.write(f"Action: 0x00 = LITERAL CHARACTER\n")
            out.write(f"  Next byte: {next_byte} = '{char}'\n")
            out.write(f"  Output: '{char}'\n")
            code.append(char)
            code_pos += 2
            
        elif curr_byte <= 0x3b:
            # 0x01-0x3b: Character from lookup table
            char = CHAR_TABLE[curr_byte]
            out.write(f"Action: 0x01-0x3B = LOOKUP TABLE\n")
            out.write(f"  Table index: {curr_byte}\n")
            out.write(f"  Character: '{char}' ('{repr(char)}')\n")
            out.write(f"  Output: '{char}'\n")
            code.append(char)
            code_pos += 1
            
        else:
            # 0x3c-0xff: Copy from previous output (LZ77-style)
            next_byte = decimal_values[code_pos + 1]
            
            offset = (curr_byte - 0x3c) * 16 + (next_byte & 0xf)
            length = (next_byte >> 4) + 2
            
            out.write(f"Action: 0x3C-0xFF = COPY FROM HISTORY\n")
            out.write(f"  Current byte: {curr_byte}, Next byte: {next_byte}\n")
            out.write(f"  Offset calculation: ({curr_byte} - 0x3c) * 16 + ({next_byte} & 0xf) = {offset}\n")
            out.write(f"  Length calculation: ({next_byte} >> 4) + 2 = {length}\n")
            out.write(f"  Action: Go back {offset} chars, copy {length} chars\n")
            
            index = len(code) - offset
            chunk = ""
            try:
                for i in range(length):
                    chunk += code[index + i]
                out.write(f"  Copied text: '{chunk}'\n")
                out.write(f"  Output: '{chunk}'\n")
                code.extend(chunk)
            except IndexError:
                out.write(f"  ERROR: Index out of range\n")
                break
            
            code_pos += 2
        
        # Show current output state
        current_output = ''.join(code)
        out.write(f"Current decompressed output ({len(code)} bytes): '{current_output[-60:] if len(current_output) > 60 else current_output}'\n")
    
    out.write("\n" + "=" * 80 + "\n")
    out.write(f"STEP 3: Final output (first {max_steps} decompression steps)\n")
    out.write("=" * 80 + "\n\n")
    
    final_code = ''.join(code)
    out.write(final_code)
    
    if len(code) < decompressed_length:
        out.write(f"\n\n[Output truncated at {max_steps} steps for readability]")
        out.write(f"\nFull decompression would produce {decompressed_length} bytes total")

print("✓ Decompression trace saved to celeste-decompression-steps.txt")
print(f"✓ Showing first 200 decompression steps")