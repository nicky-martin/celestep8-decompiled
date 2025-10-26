import re

with open("celeste-meaningful-bits.txt", "r") as f:
    content = f.read()

# Extract all binary strings and decimal values
binary_matches = re.findall(r'Reassembled byte:\s+(\d{8})', content)
decimal_matches = re.findall(r'Reassembled byte:\s+\d{8} \(decimal:\s+(\d+)\)', content)

# Join binary into continuous bitstream
bitstream = ''.join(binary_matches)

# Join decimals with commas
decimal_stream = ','.join(decimal_matches)

# Write to output file
with open("celeste-bitstream.txt", "w") as out:
    out.write("=" * 70 + "\n")
    out.write("CELESTE COMPRESSED DATA BITSTREAM\n")
    out.write("=" * 70 + "\n\n")
    
    out.write(f"Total extracted bytes: {len(binary_matches)}\n")
    out.write(f"Total bits: {len(bitstream)}\n\n")
    
    out.write("=" * 70 + "\n")
    out.write("CONTINUOUS BINARY BITSTREAM:\n")
    out.write("=" * 70 + "\n")
    out.write(bitstream + "\n\n")
    
    out.write("=" * 70 + "\n")
    out.write("DECIMAL BYTE VALUES (comma-separated):\n")
    out.write("=" * 70 + "\n")
    out.write(decimal_stream + "\n\n")
    
    out.write("=" * 70 + "\n")
    out.write("END OF BITSTREAM\n")
    out.write("=" * 70 + "\n")

print(f"✓ Extracted {len(binary_matches)} bytes")
print(f"✓ Total of {len(bitstream)} bits")
print(f"✓ Output saved to celeste-bitstream.txt")