import os
import shutil
import re
import pypandoc

def crawl_and_copy_md_files(base_dir):
    all_md_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                dest_path = os.path.join(base_dir, file)
                if full_path != dest_path:  # Avoid copying files to themselves
                    try:
                        shutil.copy(full_path, dest_path)
                        all_md_files.append(dest_path)
                    except PermissionError:
                        print(f"Skipping {full_path} due to permissions error.")
    return all_md_files

def clean_markdown(content):
    # Remove LaTeX specific commands that might cause issues
    content = re.sub(r'\\text.*?\{.*?\}', '', content)
    content = re.sub(r'\\begin\{.*?\}.*?\\end\{.*?\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\\.*', '', content)
    return content

def break_long_lines(content, max_length=80):
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        while len(line) > max_length:
            break_point = line.rfind(' ', 0, max_length)
            if break_point == -1:  # No space found, just break at max_length
                break_point = max_length
            new_lines.append(line[:break_point] + ' \\')
            line = line[break_point:].strip()
        new_lines.append(line)
    return '\n.join(new_lines)

def merge_md_files(md_files, output_file):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for md_file in md_files:
            with open(md_file, 'r', encoding='utf-8') as infile:
                content = infile.read()
                cleaned_content = clean_markdown(content)
                formatted_content = break_long_lines(cleaned_content)
                outfile.write(formatted_content)
                outfile.write('\n\n')

def convert_md_to_pdf(md_file, pdf_file):
    pypandoc.convert_file(md_file, 'pdf', outputfile=pdf_file, extra_args=[
        '--pdf-engine=xelatex',
        '--variable', 'mainfont=LiberationSerif',
        '--variable', 'papersize=letterpaper',
        '--variable', 'geometry:margin=1in',
        '--variable', 'geometry:top=1in',
        '--variable', 'geometry:bottom=1in',
        '--variable', 'geometry:left=1.5in',
        '--variable', 'geometry:right=1in'
    ])

if __name__ == "__main__":
    base_directory = os.getcwd()
    output_md = 'merged_notes.md'
    output_pdf = 'merged_notes.pdf'

    md_files = crawl_and_copy_md_files(base_directory)
    merge_md_files(md_files, output_md)
    convert_md_to_pdf(output_md, output_pdf)

    print(f"Markdown files merged into {output_md} and converted to PDF {output_pdf}.")
