import re

# Regular expression pattern to match the lines
pattern = re.compile(r'^(.*?):\s*(.*?)\s*(\d+)\s*$')

# Function to process each line and extract the required components
def process_line(line):
    match = pattern.match(line)
    if match:
        username = match.group(1)
        album = match.group(2)
        number = match.group(3)
        return f'{username},{album},{number}\n'  # Comma-separated with newline
    else:
        return None

# Read the input file
input_file = 'C:/Users/Linus/Documents/txt files/daily/rymsponsoredwithnames.txt'
output_file = 'C:/Users/Linus/Documents/txt files/daily/rymsponsoredwithnames.csv'
error_file = 'C:/Users/Linus/Documents/txt files/daily/errors.log'

with open(input_file, 'r', encoding='utf-8') as infile, \
     open(output_file, 'w', encoding='utf-8') as outfile, \
     open(error_file, 'w', encoding='utf-8') as errfile:
    
    # Write the header
    outfile.write('username,artist and album title,number\n')
    
    # Process each line and write to the CSV
    for line_number, line in enumerate(infile, start=1):
        line = line.rstrip('\n')  # Remove only the trailing newline character
        if line.strip():  # Skip empty lines
            try:
                processed_line = process_line(line)
                if processed_line:
                    outfile.write(processed_line)
                else:
                    # Write the problematic line to the error log
                    errfile.write(f'Error processing line {line_number}: {line}\n')
            except Exception as e:
                # Write the error and the problematic line to the error log
                errfile.write(f'Error: {e} - processing line {line_number}: {line}\n')

print(f'Processed data has been saved to {output_file}')
