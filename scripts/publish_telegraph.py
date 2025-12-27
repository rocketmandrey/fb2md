import os
import re
import time
from dotenv import load_dotenv
from telegraph import Telegraph
import markdown

def create_telegraph_page(title, content_html, access_token):
    """Creates a new page on Telegraph."""
    telegraph = Telegraph(access_token=access_token)
    response = telegraph.create_page(
        title=title,
        html_content=content_html
    )
    return response['url']

def demote_headers(markdown_content):
    """Demotes h1 and h2 headers in markdown to h3 and h4."""
    content = markdown_content.replace('\n# ', '\n### ').replace('\n## ', '\n#### ')
    if content.startswith('# '):
        content = '### ' + content[2:]
    if content.startswith('## '):
        content = '#### ' + content[3:]
    return content

def main():
    """Main function to create the book on Telegraph."""
    load_dotenv()
    access_token = os.getenv("TELEGRAPH_ACCESS_TOKEN")
    if not access_token:
        raise ValueError("TELEGRAPH_ACCESS_TOKEN environment variable not set.")

    markdown_file_path = '/Users/andrey/Documents/Cursor/fb2epub-markdown converter/markdown/DreamFormulaRussian - Tomabechi.md'

    with open(markdown_file_path, 'r', encoding='utf-8') as f:
        full_content = f.read()

    sections = re.split(r'\n## ', full_content)
    
    book_title_section = sections.pop(0)
    book_title = book_title_section.strip().split('\n')[0].replace('# ', '')

    processed_sections = []
    for section in sections:
        lines = section.strip().split('\n')
        title = lines[0].strip()
        if "Содержание" in title:
            continue # Skip the original ToC section
        content = '\n'.join(lines[1:]).strip()
        processed_sections.append({'title': title, 'content': content, 'url': ''})

    for i in range(len(processed_sections) - 1, -1, -1):
        section = processed_sections[i]
        title = section['title']
        
        content_md = f"## {title}\n{section['content']}"
        content_md = demote_headers(content_md)
        content_html = markdown.markdown(content_md)

        nav_links = {
            'prev': processed_sections[i - 1]['url'] if i > 0 else '',
            'next': processed_sections[i + 1]['url'] if i < len(processed_sections) - 1 else ''
        }
        
        nav_html = "<p>"
        if nav_links['prev']:
            nav_html += f"<a href='{nav_links['prev']}'>&lt; Предыдущая глава</a>"
        if nav_links['prev'] and nav_links['next']:
            nav_html += " | "
        if nav_links['next']:
            nav_html += f"<a href='{nav_links['next']}'>Следующая глава &gt;</a>"
        nav_html += "</p>"

        full_html = f"{nav_html}<hr>{content_html}<hr>{nav_html}"
        
        print(f"Creating page for: {title}")
        try:
            url = create_telegraph_page(f"{book_title} - {title}", full_html, access_token)
            processed_sections[i]['url'] = url
            print(f"  -> {url}")
            time.sleep(1) # Add delay to avoid rate limiting
        except Exception as e:
            print(f"An error occurred while creating page for {title}: {e}")
            if 'CONTENT_TOO_BIG' in str(e):
                print("    CONTENT_TOO_BIG: This section needs to be split.")
            processed_sections[i]['url'] = '#'

    toc_html = f"<h3>{book_title}</h3>\n<ul>"
    for section in processed_sections:
        toc_html += f"<li><a href='{section['url']}'>{section['title']}</a></li>"
    toc_html += "</ul>"
    
    print("Creating Table of Contents page...")
    try:
        toc_url = create_telegraph_page(book_title, toc_html, access_token)
        print(f"  -> Table of Contents created: {toc_url}")
        time.sleep(1) # Add delay
    except Exception as e:
        print(f"An error occurred while creating the Table of Contents: {e}")
        return

    print("Updating pages with ToC link...")
    telegraph = Telegraph(access_token=access_token)
    for i, section in enumerate(processed_sections):
        if section['url'] != '#':
            title = section['title']
            content_md = f"## {title}\n{section['content']}"
            content_md = demote_headers(content_md)
            content_html = markdown.markdown(content_md)

            prev_url = processed_sections[i - 1]['url'] if i > 0 and processed_sections[i-1]['url'] != '#' else ''
            next_url = processed_sections[i + 1]['url'] if i < len(processed_sections) - 1 and processed_sections[i+1]['url'] != '#' else ''
            
            nav_html = f"<p><a href='{toc_url}'>Оглавление</a></p><p>"
            if prev_url:
                nav_html += f"<a href='{prev_url}'>&lt; Предыдущая глава</a>"
            if prev_url and next_url:
                nav_html += " | "
            if next_url:
                nav_html += f"<a href='{next_url}'>Следующая глава &gt;</a>"
            nav_html += "</p>"

            full_html = f"{nav_html}<hr>{content_html}<hr>{nav_html}"
            
            print(f"Updating page for: {title}")
            try:
                page_path = section['url'].replace('https://telegra.ph/', '')
                telegraph.edit_page(
                    path=page_path,
                    title=f"{book_title} - {title}",
                    html_content=full_html
                )
                new_url = f"https://telegra.ph/{page_path}"
                processed_sections[i]['url'] = new_url
                print(f"  -> Updated: {new_url}")
                time.sleep(1) # Add delay
            except Exception as e:
                print(f"An error occurred while updating page for {title}: {e}")

    print("Finalizing Table of Contents...")
    toc_html = f"<h3>{book_title}</h3>\n<ul>"
    for section in processed_sections:
        toc_html += f"<li><a href='{section['url']}'>{section['title']}</a></li>"
    toc_html += "</ul>"
    try:
        toc_path = toc_url.replace('https://telegra.ph/', '')
        telegraph.edit_page(path=toc_path, title=book_title, html_content=toc_html)
        print("  -> Table of Contents updated.")
    except Exception as e:
        print(f"An error occurred while updating the Table of Contents: {e}")

    print("\nProcess finished.")
    print(f"Main Table of Contents URL: {toc_url}")

if __name__ == '__main__':
    main()