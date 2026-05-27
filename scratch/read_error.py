import re

def clean_and_write(input_file, output_file):
    try:
        with open(input_file, "r", encoding="utf-16") as f:
            content = f.read()
        
        # strip HTML tags to make it super readable
        clean_text = re.sub('<[^<]+?>', '', content)
        clean_text = "\n".join([line.strip() for line in clean_text.splitlines() if line.strip()])
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(clean_text[:5000])
        print(f"Wrote cleaned {input_file} to {output_file}")
    except Exception as e:
        print(f"Error processing {input_file}: {e}")

clean_and_write("render_error.html", "scratch/error_clean1.txt")
clean_and_write("render_error2.html", "scratch/error_clean2.txt")
